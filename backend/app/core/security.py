from jose import jwt
import bcrypt
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional, Dict, List
from passlib.context import CryptContext
from pydantic import ValidationError
from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from functools import wraps
import time
import hashlib
from collections import defaultdict
import asyncio

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=12  # Increased rounds for better security
)

# JWT Security
security = HTTPBearer()

# Rate limiting storage (in production, use Redis)
rate_limit_storage = defaultdict(list)
failed_attempts = defaultdict(int)
blocked_ips = defaultdict(float)

# Security constants
MAX_LOGIN_ATTEMPTS = 5
BLOCK_DURATION = 300  # 5 minutes
TOKEN_BLACKLIST = set()  # In production, use Redis
CSRF_TOKEN_LENGTH = 32
PASSWORD_MIN_LENGTH = 8


class SecurityHeaders:
    """Security headers middleware configuration"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY", 
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; font-src 'self' https://cdn.jsdelivr.net; img-src 'self' data: https:;",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "X-Permitted-Cross-Domain-Policies": "none"
        }


class RateLimiter:
    """Advanced rate limiting with different strategies"""
    
    @staticmethod
    def is_rate_limited(identifier: str, max_requests: int = None, window: int = None) -> bool:
        """Check if identifier is rate limited"""
        max_requests = max_requests or settings.RATE_LIMIT_REQUESTS
        window = window or settings.RATE_LIMIT_PERIOD
        
        now = time.time()
        # Clean old entries
        rate_limit_storage[identifier] = [
            timestamp for timestamp in rate_limit_storage[identifier]
            if now - timestamp < window
        ]
        
        # Check if limit exceeded
        if len(rate_limit_storage[identifier]) >= max_requests:
            return True
            
        # Add current request
        rate_limit_storage[identifier].append(now)
        return False
    
    @staticmethod
    def get_client_ip(request: Request) -> str:
        """Get real client IP considering proxies"""
        # Check X-Forwarded-For header first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
            
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"


class PasswordValidator:
    """Advanced password validation"""
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength with detailed feedback"""
        issues = []
        score = 0
        
        # Length check
        if len(password) < PASSWORD_MIN_LENGTH:
            issues.append(f"Senha deve ter pelo menos {PASSWORD_MIN_LENGTH} caracteres")
        else:
            score += 1
            
        # Character diversity checks
        if not any(c.islower() for c in password):
            issues.append("Senha deve conter pelo menos uma letra minúscula")
        else:
            score += 1
            
        if not any(c.isupper() for c in password):
            issues.append("Senha deve conter pelo menos uma letra maiúscula")
        else:
            score += 1
            
        if not any(c.isdigit() for c in password):
            issues.append("Senha deve conter pelo menos um número")
        else:
            score += 1
            
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            issues.append("Senha deve conter pelo menos um caractere especial")
        else:
            score += 1
            
        # Common patterns check
        common_patterns = ['123', 'abc', 'password', 'admin', '111', '000']
        if any(pattern in password.lower() for pattern in common_patterns):
            issues.append("Senha não deve conter sequências comuns")
            score -= 1
            
        strength = "weak"
        if score >= 4:
            strength = "strong"
        elif score >= 3:
            strength = "medium"
            
        return {
            "valid": len(issues) == 0,
            "score": max(0, score),
            "strength": strength,
            "issues": issues
        }


class TokenManager:
    """Advanced JWT token management"""
    
    @staticmethod
    def create_access_token(
        subject: Union[str, Any], 
        expires_delta: timedelta = None,
        additional_claims: Dict[str, Any] = None
    ) -> str:
        """Create JWT access token with enhanced security"""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        # Base claims
        to_encode = {
            "exp": expire,
            "sub": str(subject),
            "iat": datetime.now(timezone.utc),
            "type": "access",
            "jti": secrets.token_urlsafe(16)  # JWT ID for revocation
        }
        
        # Add additional claims if provided
        if additional_claims:
            to_encode.update(additional_claims)
        
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    @staticmethod
    def create_refresh_token(subject: Union[str, Any]) -> str:
        """Create JWT refresh token"""
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )
        
        to_encode = {
            "exp": expire,
            "sub": str(subject),
            "iat": datetime.now(timezone.utc),
            "type": "refresh",
            "jti": secrets.token_urlsafe(16)
        }
        
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token with enhanced validation"""
        try:
            # Check if token is blacklisted
            if token in TOKEN_BLACKLIST:
                return None
                
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            
            # Verify token type
            if payload.get("type") != token_type:
                return None
                
            # Verify not expired
            exp = payload.get("exp")
            if not exp or datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                return None
                
            return payload
            
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def revoke_token(token: str) -> bool:
        """Add token to blacklist"""
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            jti = payload.get("jti")
            if jti:
                TOKEN_BLACKLIST.add(jti)
                return True
        except jwt.InvalidTokenError:
            pass
        return False


class SecurityAudit:
    """Security audit and logging"""
    
    @staticmethod
    def log_security_event(
        event_type: str, 
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log security events for audit trail"""
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "details": details or {}
        }
        
        # In production, send to proper logging system (ELK, Splunk, etc.)
        print(f"SECURITY_AUDIT: {event}")
    
    @staticmethod
    def check_login_attempts(identifier: str) -> bool:
        """Check and update failed login attempts"""
        # Check if IP is blocked
        if identifier in blocked_ips:
            if time.time() < blocked_ips[identifier]:
                return False  # Still blocked
            else:
                # Unblock
                del blocked_ips[identifier]
                failed_attempts[identifier] = 0
                
        # Check failed attempts
        if failed_attempts[identifier] >= MAX_LOGIN_ATTEMPTS:
            # Block IP
            blocked_ips[identifier] = time.time() + BLOCK_DURATION
            SecurityAudit.log_security_event(
                "ip_blocked",
                ip_address=identifier,
                details={"attempts": failed_attempts[identifier]}
            )
            return False
            
        return True
    
    @staticmethod
    def record_failed_login(identifier: str):
        """Record failed login attempt"""
        failed_attempts[identifier] += 1
        SecurityAudit.log_security_event(
            "failed_login",
            ip_address=identifier,
            details={"attempt_count": failed_attempts[identifier]}
        )
    
    @staticmethod
    def reset_failed_attempts(identifier: str):
        """Reset failed login attempts after successful login"""
        if identifier in failed_attempts:
            del failed_attempts[identifier]


# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def generate_csrf_token() -> str:
    """Generate CSRF token"""
    return secrets.token_urlsafe(CSRF_TOKEN_LENGTH)


def verify_csrf_token(token: str, expected: str) -> bool:
    """Verify CSRF token (constant time comparison)"""
    return secrets.compare_digest(token, expected)


def generate_api_key() -> str:
    """Generate secure API key"""
    return f"biuai_{secrets.token_urlsafe(32)}"


def hash_sensitive_data(data: str) -> str:
    """Hash sensitive data for storage"""
    return hashlib.sha256(data.encode()).hexdigest()


# Decorator for rate limiting
def rate_limit(max_requests: int = None, window: int = None):
    """Rate limiting decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = RateLimiter.get_client_ip(request)
            
            if RateLimiter.is_rate_limited(client_ip, max_requests, window):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Taxa de requisições excedida. Tente novamente mais tarde."
                )
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


# Security exceptions
class SecurityException(Exception):
    """Base security exception"""
    pass


class InvalidTokenException(SecurityException):
    """Invalid token exception"""
    pass


class RateLimitException(SecurityException):
    """Rate limit exceeded exception"""
    pass


class WeakPasswordException(SecurityException):
    """Exception for weak passwords"""
    pass


# Convenience functions for backwards compatibility
def create_access_token(
    subject: Union[str, Any], 
    expires_delta: timedelta = None,
    additional_claims: Dict[str, Any] = None
) -> str:
    """Convenience function for creating access tokens"""
    return TokenManager.create_access_token(subject, expires_delta, additional_claims)

def create_refresh_token(subject: Union[str, Any]) -> str:
    """Convenience function for creating refresh tokens"""
    return TokenManager.create_refresh_token(subject)

def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """Convenience function for verifying tokens"""
    return TokenManager.verify_token(token, token_type)

def revoke_token(token: str) -> bool:
    """Convenience function for revoking tokens"""
    return TokenManager.revoke_token(token) 