import jwt
import os
from pydantic import BaseModel, ValidationError
from fastapi import Depends, APIRouter, HTTPException, Security, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from typing import Annotated
from datetime import datetime, timedelta, timezone
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

# >> openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
HASHED_PASSWORD = os.getenv("HASHED_PASSWORD")

fake_users_db = {
    "alice": {
        "name": "alice",
        "fill_name": "Alice Chains",
        "email": "alicechains@someserver.com",
        "hashed_password": HASHED_PASSWORD,
        "disabled": True,
    },
    "bob": {
        "name": "bob",
        "fill_name": "Bob Marloy",
        "email": "threes@littlebirds.com",
        "hashed_password": HASHED_PASSWORD,
        "disabled": False,
    },
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []


class User(BaseModel):
    name: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={"me": "Read information about the current user.", "items": "Read items."},
)

route = APIRouter()


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, name: str):
    if name in db:
        return UserInDB(**db[name])


def authenticate_user(
    fake_db, username: str, password: str
) -> tuple[bool, UserInDB | None]:
    user = get_user(fake_db, username)
    if not user:
        return False, None
    if not verify_password(password, user.hashed_password):
        return False, None
    return True, user


def create_access_token(data: dict, ttl: timedelta | None = None) -> str:
    data_to_encode = data.copy()
    if ttl:
        expire = datetime.now(timezone.utc) + ttl
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    data_to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (InvalidTokenError, ValidationError):
        raise credentials_exception

    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Security(get_current_user, scopes=["me"])],
):
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


# TODO: replace by Auth0
@route.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    authenticated, user = authenticate_user(
        fake_users_db, form_data.username, form_data.password
    )
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )
    access_token_ttl = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.name, "scopes": form_data.scopes}, ttl=access_token_ttl
    )
    return Token(access_token=access_token, token_type="bearer")


@route.get("/users/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


# @route.get("/users/me/items/")
# async def read_own_items(
#     current_user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
# ):
#     return [{"item_id": "Foo", "owner": current_user.username}]


# @route.get("/status/")
# async def read_system_status(current_user: Annotated[User, Depends(get_current_user)]):
#     return {"status": "ok"}
