import time
import json
import uuid
import asyncio
from typing import Callable, Dict, Any, Optional
from datetime import datetime, timezone
import logging
from contextvars import ContextVar
import traceback

from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.security import SecurityHeaders, RateLimiter, SecurityAudit

# Context variables for request tracking
request_id_context: ContextVar[str] = ContextVar('request_id', default='')
user_id_context: ContextVar[str] = ContextVar('user_id', default='')

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT,
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class StructuredLogger:
    """Structured logging for better observability"""
    
    @staticmethod
    def log_request(
        request: Request, 
        response: Response, 
        duration: float,
        request_id: str,
        user_id: Optional[str] = None
    ):
        """Log request in structured format"""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": request_id,
            "user_id": user_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "client_ip": RateLimiter.get_client_ip(request),
            "user_agent": request.headers.get("user-agent", ""),
            "content_length": response.headers.get("content-length", 0)
        }
        
        # Log level based on status code
        if response.status_code >= 500:
            logger.error("Request completed", extra=log_data)
        elif response.status_code >= 400:
            logger.warning("Request completed", extra=log_data)
        else:
            logger.info("Request completed", extra=log_data)
    
    @staticmethod
    def log_error(
        request: Request, 
        error: Exception, 
        request_id: str,
        user_id: Optional[str] = None
    ):
        """Log error in structured format"""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": request_id,
            "user_id": user_id,
            "method": request.method,
            "url": str(request.url),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "client_ip": RateLimiter.get_client_ip(request)
        }
        
        logger.error("Request error", extra=log_data)


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware for request tracking and correlation"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request_id_context.set(request_id)
        
        # Add request ID to headers for tracing
        request.state.request_id = request_id
        
        # Start timer
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            # Get user ID if available
            user_id = getattr(request.state, 'user_id', None)
            if user_id:
                user_id_context.set(str(user_id))
            
            # Log request
            StructuredLogger.log_request(
                request, response, duration, request_id, user_id
            )
            
            return response
            
        except Exception as error:
            # Log error
            StructuredLogger.log_error(request, error, request_id)
            
            # Return error response
            if isinstance(error, HTTPException):
                return JSONResponse(
                    status_code=error.status_code,
                    content={
                        "detail": error.detail,
                        "request_id": request_id
                    }
                )
            else:
                return JSONResponse(
                    status_code=500,
                    content={
                        "detail": "Erro interno do servidor",
                        "request_id": request_id
                    }
                )


class SecurityMiddleware(BaseHTTPMiddleware):
    """Enhanced security middleware"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client IP
        client_ip = RateLimiter.get_client_ip(request)
        
        # Rate limiting check
        if RateLimiter.is_rate_limited(client_ip):
            SecurityAudit.log_security_event(
                "rate_limit_exceeded",
                ip_address=client_ip,
                details={"path": request.url.path, "method": request.method}
            )
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Taxa de requisições excedida. Tente novamente mais tarde.",
                    "retry_after": settings.RATE_LIMIT_PERIOD
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        security_headers = SecurityHeaders.get_security_headers()
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Performance monitoring and optimization middleware"""
    
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.slow_request_threshold = 1.0  # 1 second
        self.metrics = {
            "total_requests": 0,
            "total_errors": 0,
            "avg_response_time": 0,
            "slow_requests": 0
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Increment request counter
        self.metrics["total_requests"] += 1
        
        try:
            response = await call_next(request)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Update metrics
            self._update_metrics(response_time, response.status_code >= 400)
            
            # Add performance headers
            response.headers["X-Response-Time"] = f"{response_time:.3f}s"
            
            # Log slow requests
            if response_time > self.slow_request_threshold:
                logger.warning(
                    f"Slow request detected: {request.method} {request.url.path} "
                    f"took {response_time:.3f}s"
                )
            
            return response
            
        except Exception as error:
            # Update error metrics
            self.metrics["total_errors"] += 1
            raise error
    
    def _update_metrics(self, response_time: float, is_error: bool):
        """Update performance metrics"""
        # Update average response time (simple moving average)
        current_avg = self.metrics["avg_response_time"]
        total_requests = self.metrics["total_requests"]
        
        self.metrics["avg_response_time"] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
        
        # Update slow request counter
        if response_time > self.slow_request_threshold:
            self.metrics["slow_requests"] += 1
        
        # Update error counter
        if is_error:
            self.metrics["total_errors"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return {
            **self.metrics,
            "error_rate": (
                self.metrics["total_errors"] / self.metrics["total_requests"] 
                if self.metrics["total_requests"] > 0 else 0
            ),
            "slow_request_rate": (
                self.metrics["slow_requests"] / self.metrics["total_requests"]
                if self.metrics["total_requests"] > 0 else 0
            )
        }


class HealthCheckMiddleware(BaseHTTPMiddleware):
    """Health check and monitoring middleware"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Health check endpoint
        if request.url.path == "/health":
            return JSONResponse({
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "version": settings.PROJECT_VERSION,
                "environment": settings.ENVIRONMENT
            })
        
        # Metrics endpoint
        if request.url.path == "/metrics":
            # Get performance metrics if available
            perf_middleware = None
            for middleware in request.app.middleware_stack:
                if isinstance(middleware.cls, type) and issubclass(middleware.cls, PerformanceMiddleware):
                    perf_middleware = middleware
                    break
            
            metrics = {}
            if perf_middleware:
                metrics = perf_middleware.get_metrics()
            
            return JSONResponse({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "performance": metrics,
                "system": {
                    "environment": settings.ENVIRONMENT,
                    "version": settings.PROJECT_VERSION
                }
            })
        
        return await call_next(request)


class CacheControlMiddleware(BaseHTTPMiddleware):
    """Cache control middleware for static resources"""
    
    CACHE_PATTERNS = {
        "/static/": "public, max-age=31536000",  # 1 year
        "/api/v1/": "no-cache, no-store, must-revalidate",  # No cache for API
        "/docs": "no-cache",
        "/redoc": "no-cache",
    }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Apply cache control based on path
        for pattern, cache_directive in self.CACHE_PATTERNS.items():
            if request.url.path.startswith(pattern):
                response.headers["Cache-Control"] = cache_directive
                break
        else:
            # Default cache control
            response.headers["Cache-Control"] = "no-cache"
        
        return response


def setup_middleware(app: FastAPI) -> None:
    """Setup all middleware for the application"""
    
    # Trusted hosts (security)
    if settings.ENVIRONMENT == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["api.biuai.com", "biuai.com", "localhost"]
        )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Response-Time"]
    )
    
    # Gzip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Custom middleware (order matters!)
    app.add_middleware(RequestTrackingMiddleware)
    app.add_middleware(SecurityMiddleware)
    app.add_middleware(PerformanceMiddleware)
    app.add_middleware(HealthCheckMiddleware)
    app.add_middleware(CacheControlMiddleware)


# Global exception handler
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for better error responses"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    # Log the error
    StructuredLogger.log_error(request, exc, request_id)
    
    # Security audit for authentication/authorization errors
    if isinstance(exc, HTTPException) and exc.status_code in [401, 403]:
        SecurityAudit.log_security_event(
            "unauthorized_access",
            ip_address=RateLimiter.get_client_ip(request),
            details={
                "path": request.url.path,
                "method": request.method,
                "status_code": exc.status_code
            }
        )
    
    # Return appropriate error response
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    
    # For unexpected errors, don't expose internal details in production
    detail = str(exc) if settings.DEBUG else "Erro interno do servidor"
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": detail,
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup global exception handlers"""
    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(StarletteHTTPException, global_exception_handler) 