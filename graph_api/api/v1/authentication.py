import jwt
import os
from fastapi import Depends, APIRouter, HTTPException, Security, status
from fastapi.security import (
    SecurityScopes,
)
from typing import Annotated
from pydantic import BaseModel, ValidationError
from jwt.exceptions import InvalidTokenError
import httpx
from fastapi.security import OAuth2
from fastapi.openapi.models import OAuthFlows, OAuthFlowImplicit


route = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []


class User(BaseModel):
    id: str
    name: str
    email: str | None = None
    nodes: list[str] = []
    full_name: str | None = None
    disabled: bool | None = None


class IdentityProvider:
    issuer: str
    audience: str

    async def get_public_key(self, kid: str) -> str:
        raise NotImplementedError()

    async def verify_token(self, token: str, headers: dict) -> dict:
        raise NotImplementedError()

    async def get_user(self, user_id: str) -> User | None:
        raise NotImplementedError()

    async def get_oauth2_scheme(self, scopes: dict) -> OAuth2:
        raise NotImplementedError()


class Auth0provider(IdentityProvider):
    def __init__(self):
        super().__init__()
        self.grant_type = "client_credentials"
        self.client_id = os.getenv("AUTH0_CLIENT_ID")
        self.client_secret = os.getenv("AUTH0_CLIENT_SECRET")

        auth0_domain = os.getenv("AUTH0_DOMAIN")
        base_url = f"https://{auth0_domain}"

        self.issuer = base_url
        self.audience = (
            os.getenv("AUTH0_API_AUDIENCE")
            or f"https://{os.getenv('AUTH0_DOMAIN')}/api/v2/"
            or f"https://whollygrid.com"
        )
        self.authorize_url = f"{base_url}/authorize"
        self.token_url = f"{base_url}/oauth/token"
        self.users_url = f"{base_url}/api/v2/users"
        self.jwt_url = f"{base_url}/.well-known/jwks.json"

    async def get_public_key(self, kid: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(self.jwt_url)
            jwks = response.json()
            for key in jwks["keys"]:
                if key["kid"] == kid:
                    return key
        raise InvalidCredentials()

    async def verify_token(self, token: str, headers: dict) -> dict:
        try:
            unverified = jwt.decode(token, options={"verify_signature": False})
            kid = unverified.get("kid")

            public_key_data = await self.get_public_key(kid)
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(public_key_data)

            payload = jwt.decode(
                token,
                public_key,
                algorithms=[os.getenv("AUTH0_ALGORITHM")],
                audience=self.audience,
                issuer=self.issuer,
            )
            return payload
        except InvalidTokenError as e:
            raise InvalidCredentials(headers)
        except ValidationError:
            raise InvalidCredentials(headers)

    async def get_user(self, user_id: str) -> User | None:
        """Fetch user from Identity Provider API."""
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                self.token_url,
                json={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "audience": self.audience,
                    "grant_type": self.grant_type,
                },
            )
            access_token = token_response.json()["access_token"]
            user_response = await client.get(
                f"{self.users_url}/{user_id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            auth0_user: dict = user_response.json()
            return User(
                id=user_id,
                name=auth0_user.get("nickname", auth0_user.get("email")),
                email=auth0_user.get("email"),
                full_name=auth0_user.get("name"),
                disabled=auth0_user.get("blocked", False),
            )

    def get_oauth2_scheme(self, scopes: dict) -> OAuth2:
        """Create OAuth2 scheme with authorization code flow."""
        return OAuth2(
            flows=OAuthFlows(
                implicit=OAuthFlowImplicit(
                    authorizationUrl=self.authorize_url, scopes=scopes
                )
            )
        )


identity_provider = Auth0provider()
oauth2_scheme = identity_provider.get_oauth2_scheme(
    scopes={
        "openid": "OpenID",
        "profile": "Profile",
        "email": "Email",
        "me": "Read information about the current user.",
        "items": "Read items.",
    }
)


class InvalidCredentials(HTTPException):
    def __init__(self, headers: dict = {"WWW-Authenticate": "Bearer"}):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authentication credentials",
            headers=headers,
        )


class InsufficientPermissions(HTTPException):
    def __init__(self, headers: dict = {"WWW-Authenticate": "Bearer"}):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions",
            headers=headers,
        )


async def get_current_user(
    security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    headers = {"WWW-Authenticate": authenticate_value}

    payload = await identity_provider.verify_token(token, headers)
    username = payload.get("sub")
    if username is None:
        raise InvalidCredentials(headers)

    # token_scopes = payload.get("scopes", [])
    token_scopes = payload.get("scope", "").split()
    token_data = TokenData(username=username, scopes=token_scopes)

    user = await identity_provider.get_user(user_id=token_data.username)
    if user is None:
        raise InvalidCredentials(headers)

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise InsufficientPermissions(headers)
    return user


async def get_current_active_user(
    current_user: Annotated[User, Security(get_current_user, scopes=["me"])],
):
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


@route.get("/users/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@route.get("/users/me/items")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.name}]
