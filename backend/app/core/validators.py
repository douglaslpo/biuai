"""
Sistema Avançado de Validação para BIUAI
Validações customizadas, sanitização e verificação de integridade
"""

import re
import decimal
from typing import Any, Dict, List, Optional, Union, Callable, Type
from datetime import datetime, date, timedelta
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from phonenumbers import NumberParseException

from pydantic import BaseModel, validator, Field, ValidationError
from pydantic.validators import str_validator
import cpf_cnpj

from app.core.config import settings


class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message: str, field: str = None, value: Any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(message)


class BusinessRuleError(ValidationError):
    """Business rule validation error"""
    pass


class SecurityValidationError(ValidationError):
    """Security validation error"""
    pass


class DataSanitizer:
    """Advanced data sanitization"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = None, allow_html: bool = False) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            value = str(value)
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Strip whitespace
        value = value.strip()
        
        # Remove HTML if not allowed
        if not allow_html:
            value = re.sub(r'<[^>]+>', '', value)
        
        # Limit length
        if max_length and len(value) > max_length:
            value = value[:max_length]
        
        return value
    
    @staticmethod
    def sanitize_number(value: Union[str, int, float], decimal_places: int = 2) -> decimal.Decimal:
        """Sanitize numeric input"""
        try:
            if isinstance(value, str):
                # Remove non-numeric characters except decimal point and minus
                value = re.sub(r'[^\d.-]', '', value)
            
            decimal_value = decimal.Decimal(str(value))
            
            # Round to specified decimal places
            return decimal_value.quantize(decimal.Decimal('0.01') if decimal_places == 2 else decimal.Decimal('0.' + '0' * decimal_places))
            
        except (decimal.InvalidOperation, ValueError):
            raise ValidationError(f"Invalid numeric value: {value}")
    
    @staticmethod
    def sanitize_phone(phone: str) -> str:
        """Sanitize phone number"""
        if not phone:
            return ""
        
        # Remove all non-numeric characters
        cleaned = re.sub(r'[^\d]', '', phone)
        
        # Add country code if missing (Brazil default)
        if len(cleaned) == 10:  # Local number
            cleaned = "55" + cleaned
        elif len(cleaned) == 11 and not cleaned.startswith("55"):  # Mobile without country code
            cleaned = "55" + cleaned
        
        return cleaned


class CPFValidator:
    """CPF validation"""
    
    @staticmethod
    def validate(cpf: str) -> bool:
        """Validate Brazilian CPF"""
        if not cpf:
            return False
        
        # Remove formatting
        cpf = re.sub(r'[^\d]', '', cpf)
        
        # Check length
        if len(cpf) != 11:
            return False
        
        # Check for repeated digits
        if cpf == cpf[0] * 11:
            return False
        
        # Calculate check digits
        def calculate_digit(cpf_digits: str, weights: List[int]) -> int:
            total = sum(int(digit) * weight for digit, weight in zip(cpf_digits, weights))
            remainder = total % 11
            return 0 if remainder < 2 else 11 - remainder
        
        # First check digit
        first_digit = calculate_digit(cpf[:9], list(range(10, 1, -1)))
        if int(cpf[9]) != first_digit:
            return False
        
        # Second check digit
        second_digit = calculate_digit(cpf[:10], list(range(11, 1, -1)))
        if int(cpf[10]) != second_digit:
            return False
        
        return True
    
    @staticmethod
    def format(cpf: str) -> str:
        """Format CPF with dots and dash"""
        cpf = re.sub(r'[^\d]', '', cpf)
        if len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        return cpf


class CNPJValidator:
    """CNPJ validation"""
    
    @staticmethod
    def validate(cnpj: str) -> bool:
        """Validate Brazilian CNPJ"""
        if not cnpj:
            return False
        
        # Remove formatting
        cnpj = re.sub(r'[^\d]', '', cnpj)
        
        # Check length
        if len(cnpj) != 14:
            return False
        
        # Check for repeated digits
        if cnpj == cnpj[0] * 14:
            return False
        
        # Calculate check digits
        def calculate_digit(cnpj_digits: str, weights: List[int]) -> int:
            total = sum(int(digit) * weight for digit, weight in zip(cnpj_digits, weights))
            remainder = total % 11
            return 0 if remainder < 2 else 11 - remainder
        
        # First check digit
        first_digit = calculate_digit(cnpj[:12], [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
        if int(cnpj[12]) != first_digit:
            return False
        
        # Second check digit
        second_digit = calculate_digit(cnpj[:13], [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
        if int(cnpj[13]) != second_digit:
            return False
        
        return True
    
    @staticmethod
    def format(cnpj: str) -> str:
        """Format CNPJ with dots, slash and dash"""
        cnpj = re.sub(r'[^\d]', '', cnpj)
        if len(cnpj) == 14:
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        return cnpj


class FinancialValidators:
    """Financial-specific validators"""
    
    @staticmethod
    def validate_amount(amount: Union[str, int, float], min_value: float = None, max_value: float = None) -> decimal.Decimal:
        """Validate financial amount"""
        try:
            sanitized = DataSanitizer.sanitize_number(amount)
            
            if min_value is not None and sanitized < decimal.Decimal(str(min_value)):
                raise ValidationError(f"Amount must be at least {min_value}")
            
            if max_value is not None and sanitized > decimal.Decimal(str(max_value)):
                raise ValidationError(f"Amount cannot exceed {max_value}")
            
            return sanitized
            
        except Exception as e:
            raise ValidationError(f"Invalid amount: {amount}")
    
    @staticmethod
    def validate_account_number(account: str) -> str:
        """Validate bank account number"""
        if not account:
            raise ValidationError("Account number is required")
        
        # Remove non-numeric characters
        account = re.sub(r'[^\d]', '', account)
        
        # Check length (Brazilian accounts typically 5-8 digits)
        if not (5 <= len(account) <= 8):
            raise ValidationError("Account number must be between 5 and 8 digits")
        
        return account
    
    @staticmethod
    def validate_agency(agency: str) -> str:
        """Validate bank agency"""
        if not agency:
            raise ValidationError("Agency is required")
        
        # Remove non-numeric characters
        agency = re.sub(r'[^\d]', '', agency)
        
        # Check length (Brazilian agencies typically 4-5 digits)
        if not (4 <= len(agency) <= 5):
            raise ValidationError("Agency must be between 4 and 5 digits")
        
        return agency
    
    @staticmethod
    def validate_bank_code(code: str) -> str:
        """Validate Brazilian bank code"""
        if not code:
            raise ValidationError("Bank code is required")
        
        # Remove non-numeric characters
        code = re.sub(r'[^\d]', '', code)
        
        # Check length (Brazilian bank codes are 3 digits)
        if len(code) != 3:
            raise ValidationError("Bank code must be 3 digits")
        
        # List of valid Brazilian bank codes (partial list)
        valid_codes = [
            "001",  # Banco do Brasil
            "104",  # Caixa Econômica Federal
            "237",  # Bradesco
            "341",  # Itaú
            "033",  # Santander
            "745",  # Citibank
            "399",  # HSBC
            "756",  # Sicoob
            "748",  # Sicredi
        ]
        
        return code


class SecurityValidators:
    """Security-related validators"""
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength"""
        if not password:
            raise SecurityValidationError("Password is required")
        
        issues = []
        score = 0
        
        # Length check
        if len(password) < 8:
            issues.append("Password must be at least 8 characters long")
        else:
            score += 1
        
        # Character diversity
        if not re.search(r'[a-z]', password):
            issues.append("Password must contain at least one lowercase letter")
        else:
            score += 1
        
        if not re.search(r'[A-Z]', password):
            issues.append("Password must contain at least one uppercase letter")
        else:
            score += 1
        
        if not re.search(r'\d', password):
            issues.append("Password must contain at least one number")
        else:
            score += 1
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            issues.append("Password must contain at least one special character")
        else:
            score += 1
        
        # Common patterns
        common_patterns = ['password', '123456', 'qwerty', 'abc123', 'admin']
        if any(pattern in password.lower() for pattern in common_patterns):
            issues.append("Password contains common patterns")
            score -= 1
        
        # Sequential characters
        if re.search(r'(.)\1{2,}', password):
            issues.append("Password contains repeated characters")
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
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email address"""
        if not email:
            raise ValidationError("Email is required")
        
        email = email.strip().lower()
        
        try:
            valid = validate_email(email)
            return valid.email
        except EmailNotValidError as e:
            raise ValidationError(f"Invalid email: {str(e)}")
    
    @staticmethod
    def validate_phone(phone: str, country_code: str = "BR") -> str:
        """Validate phone number"""
        if not phone:
            raise ValidationError("Phone number is required")
        
        try:
            sanitized = DataSanitizer.sanitize_phone(phone)
            parsed = phonenumbers.parse(sanitized, country_code)
            
            if not phonenumbers.is_valid_number(parsed):
                raise ValidationError("Invalid phone number")
            
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            
        except NumberParseException as e:
            raise ValidationError(f"Invalid phone format: {str(e)}")


class BusinessRuleValidators:
    """Business rule validators"""
    
    @staticmethod
    def validate_transaction_date(transaction_date: date, future_days: int = 30) -> date:
        """Validate transaction date"""
        if not transaction_date:
            raise BusinessRuleError("Transaction date is required")
        
        today = date.today()
        
        # Don't allow dates too far in the past (1 year)
        min_date = today - timedelta(days=365)
        if transaction_date < min_date:
            raise BusinessRuleError("Transaction date cannot be more than 1 year in the past")
        
        # Don't allow dates too far in the future
        max_date = today + timedelta(days=future_days)
        if transaction_date > max_date:
            raise BusinessRuleError(f"Transaction date cannot be more than {future_days} days in the future")
        
        return transaction_date
    
    @staticmethod
    def validate_transaction_amount(amount: decimal.Decimal, transaction_type: str) -> decimal.Decimal:
        """Validate transaction amount based on type"""
        if amount == 0:
            raise BusinessRuleError("Transaction amount cannot be zero")
        
        # Revenue should be positive
        if transaction_type == "revenue" and amount < 0:
            raise BusinessRuleError("Revenue transactions must have positive amounts")
        
        # Expense should be negative
        if transaction_type == "expense" and amount > 0:
            raise BusinessRuleError("Expense transactions must have negative amounts")
        
        # Check reasonable limits
        max_amount = decimal.Decimal('1000000.00')  # 1 million
        if abs(amount) > max_amount:
            raise BusinessRuleError(f"Transaction amount cannot exceed {max_amount}")
        
        return amount
    
    @staticmethod
    def validate_category_assignment(category_id: int, transaction_type: str, categories: List[Dict]) -> int:
        """Validate category assignment"""
        if not category_id:
            raise BusinessRuleError("Category is required")
        
        # Find category
        category = next((c for c in categories if c['id'] == category_id), None)
        if not category:
            raise BusinessRuleError("Invalid category")
        
        # Check if category type matches transaction type
        if category.get('tipo') and category['tipo'] != transaction_type:
            raise BusinessRuleError(f"Category type {category['tipo']} doesn't match transaction type {transaction_type}")
        
        return category_id
    
    @staticmethod
    def validate_goal_amount(current_amount: decimal.Decimal, goal_amount: decimal.Decimal) -> decimal.Decimal:
        """Validate financial goal amount"""
        if goal_amount <= 0:
            raise BusinessRuleError("Goal amount must be positive")
        
        if current_amount < 0:
            raise BusinessRuleError("Current amount cannot be negative")
        
        if current_amount > goal_amount:
            raise BusinessRuleError("Current amount cannot exceed goal amount")
        
        return goal_amount
    
    @staticmethod
    def validate_goal_deadline(deadline: date) -> date:
        """Validate goal deadline"""
        if not deadline:
            raise BusinessRuleError("Goal deadline is required")
        
        today = date.today()
        
        if deadline <= today:
            raise BusinessRuleError("Goal deadline must be in the future")
        
        # Don't allow goals more than 10 years in the future
        max_deadline = today + timedelta(days=3650)
        if deadline > max_deadline:
            raise BusinessRuleError("Goal deadline cannot be more than 10 years in the future")
        
        return deadline


class DataIntegrityValidator:
    """Data integrity validators"""
    
    @staticmethod
    def validate_unique_constraint(value: Any, existing_values: List[Any], field_name: str):
        """Validate unique constraint"""
        if value in existing_values:
            raise ValidationError(f"{field_name} must be unique")
    
    @staticmethod
    def validate_foreign_key(foreign_id: int, valid_ids: List[int], entity_name: str):
        """Validate foreign key reference"""
        if foreign_id not in valid_ids:
            raise ValidationError(f"Invalid {entity_name} reference")
    
    @staticmethod
    def validate_json_structure(data: Dict, required_fields: List[str], optional_fields: List[str] = None):
        """Validate JSON structure"""
        optional_fields = optional_fields or []
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Required field '{field}' is missing")
        
        # Check for unexpected fields
        allowed_fields = set(required_fields + optional_fields)
        unexpected_fields = set(data.keys()) - allowed_fields
        
        if unexpected_fields:
            raise ValidationError(f"Unexpected fields: {', '.join(unexpected_fields)}")


# Pydantic models with custom validators
class BaseValidatedModel(BaseModel):
    """Base model with common validations"""
    
    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True
        json_encoders = {
            decimal.Decimal: float,
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


class ValidatedUser(BaseValidatedModel):
    """Validated user model"""
    nome: str = Field(..., min_length=2, max_length=100)
    email: str = Field(...)
    telefone: Optional[str] = None
    cpf: Optional[str] = None
    
    @validator('nome')
    def validate_nome(cls, v):
        return DataSanitizer.sanitize_string(v, max_length=100)
    
    @validator('email')
    def validate_email(cls, v):
        return SecurityValidators.validate_email(v)
    
    @validator('telefone')
    def validate_telefone(cls, v):
        if v:
            return SecurityValidators.validate_phone(v)
        return v
    
    @validator('cpf')
    def validate_cpf(cls, v):
        if v and not CPFValidator.validate(v):
            raise ValueError("Invalid CPF")
        return v


class ValidatedTransaction(BaseValidatedModel):
    """Validated transaction model"""
    descricao: str = Field(..., min_length=1, max_length=200)
    valor: decimal.Decimal = Field(...)
    data_lancamento: date = Field(...)
    categoria_id: int = Field(...)
    conta_id: int = Field(...)
    
    @validator('descricao')
    def validate_descricao(cls, v):
        return DataSanitizer.sanitize_string(v, max_length=200)
    
    @validator('valor')
    def validate_valor(cls, v):
        return FinancialValidators.validate_amount(v, min_value=-1000000, max_value=1000000)
    
    @validator('data_lancamento')
    def validate_data_lancamento(cls, v):
        return BusinessRuleValidators.validate_transaction_date(v)


# Decorator for automatic validation
def validate_input(validator_class: Type[BaseValidatedModel]):
    """Decorator to automatically validate input using Pydantic model"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Validate kwargs against the model
            try:
                validated_data = validator_class(**kwargs)
                # Replace kwargs with validated data
                kwargs.update(validated_data.dict())
                return func(*args, **kwargs)
            except ValidationError as e:
                raise ValidationError(f"Validation failed: {str(e)}")
        return wrapper
    return decorator


# Validation utilities
def validate_batch(data_list: List[Dict], validator_class: Type[BaseValidatedModel]) -> List[Dict]:
    """Validate a batch of data"""
    validated_list = []
    errors = []
    
    for i, data in enumerate(data_list):
        try:
            validated = validator_class(**data)
            validated_list.append(validated.dict())
        except ValidationError as e:
            errors.append(f"Item {i}: {str(e)}")
    
    if errors:
        raise ValidationError(f"Batch validation failed: {'; '.join(errors)}")
    
    return validated_list


def sanitize_user_input(data: Dict) -> Dict:
    """Sanitize all user input in a dictionary"""
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = DataSanitizer.sanitize_string(value)
        elif isinstance(value, (int, float)):
            try:
                sanitized[key] = DataSanitizer.sanitize_number(value)
            except ValidationError:
                sanitized[key] = value
        elif isinstance(value, dict):
            sanitized[key] = sanitize_user_input(value)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_user_input(item) if isinstance(item, dict) else item for item in value]
        else:
            sanitized[key] = value
    
    return sanitized 