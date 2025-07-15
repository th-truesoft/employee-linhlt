from typing import Optional, List
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# OAuth2 Schemas
class OAuth2ClientCredentials(BaseModel):
    client_id: str
    client_secret: str
    grant_type: str = "client_credentials"
    scope: Optional[str] = None


class OAuth2AuthorizationCode(BaseModel):
    client_id: str
    client_secret: str
    grant_type: str = "authorization_code"
    code: str
    redirect_uri: str
    scope: Optional[str] = None


class OAuth2RefreshToken(BaseModel):
    client_id: str
    client_secret: str
    grant_type: str = "refresh_token"
    refresh_token: str
    scope: Optional[str] = None


class OAuth2TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    organization_id: str


class OAuth2TokenIntrospection(BaseModel):
    active: bool
    scope: Optional[str] = None
    client_id: Optional[str] = None
    username: Optional[str] = None
    organization_id: Optional[str] = None
    token_type: Optional[str] = None
    exp: Optional[int] = None
    iat: Optional[int] = None
    sub: Optional[str] = None


class OAuth2Client(BaseModel):
    client_id: str
    client_name: str
    organization_id: str
    scopes: List[str]
    redirect_uris: List[str]
    grant_types: List[str]
    is_active: bool = True
    client_secret: Optional[str] = None  # Only returned on creation


class OAuth2ClientCreate(BaseModel):
    client_name: str
    organization_id: str
    scopes: List[str] = ["read", "write"]
    redirect_uris: List[str] = []
    grant_types: List[str] = [
        "client_credentials",
        "authorization_code",
        "refresh_token",
    ]


class OAuth2Scope(BaseModel):
    name: str
    description: str
