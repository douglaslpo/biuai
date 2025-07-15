from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr, Field, validator
import re

class TenantBase(BaseModel):
    """Schema base para tenant"""
    name: str = Field(..., min_length=2, max_length=100)
    slug: Optional[str] = Field(None, min_length=2, max_length=100)
    domain: Optional[str] = Field(None, max_length=255)
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)
    features: Optional[Dict[str, bool]] = Field(default_factory=dict)
    meta_info: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('slug')
    def validate_slug(cls, v):
        if v and not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug deve conter apenas letras minúsculas, números e hífen')
        return v
    
    @validator('domain')
    def validate_domain(cls, v):
        if v and not re.match(r'^[a-z0-9.-]+\.[a-z]{2,}$', v):
            raise ValueError('Domínio inválido')
        return v

class TenantCreate(TenantBase):
    """Schema para criar tenant"""
    slug: str = Field(..., min_length=2, max_length=100)
    admin_email: EmailStr
    admin_password: str = Field(..., min_length=8)

class TenantUpdate(TenantBase):
    """Schema para atualizar tenant"""
    pass

class TenantModuleBase(BaseModel):
    """Schema base para módulo do tenant"""
    name: str
    display_name: str
    is_active: bool
    is_configured: bool
    settings: Dict[str, Any]
    features_enabled: List[str]
    activated_at: datetime
    trial_ends_at: Optional[datetime]
    subscription_ends_at: Optional[datetime]

    class Config:
        orm_mode = True

class TenantModuleActivate(BaseModel):
    """Schema para ativar módulo"""
    trial: bool = Field(default=False)

class TenantResponse(TenantBase):
    """Schema para resposta de tenant"""
    id: int
    is_active: bool
    max_users: int
    max_storage_gb: int
    trial_ends_at: Optional[datetime]
    subscription_ends_at: Optional[datetime]
    last_billing_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    modules: List[TenantModuleBase]

    class Config:
        orm_mode = True 