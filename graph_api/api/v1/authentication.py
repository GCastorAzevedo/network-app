import jwt
from fastapi import Depends, APIRouter, HTTPException, Security, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from typing import Annotated
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, ValidationError
from pwdlib import PasswordHash
from jwt.exceptions import InvalidTokenError

# openssl rand -hex 32
SECRET_KEY = "a4d04de77d7d87915b977587f2d56ad5340267f0b61f25138d1cb63b30da4dbe"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


route = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="v1/auth/token",
    scopes={"me": "Read information about the current user.", "items": "Read items."},
)
password_hash = PasswordHash.recommended()


fake_users_db = {
    "johndoe": {
        "name": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$e/7ugisQS7W+PIrAMUljfg$2kP1D/V3eJ0yRvbR+tE8oRbz4defcQUX5Z8OVIfZJog",
        "disable": False,
    },
    "alice": {
        "name": "alice",
        "full_name": "Alice Chains",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret",
        "disable": True,
    },
    "bob": {
        "name": "bob",
        "fill_name": "Bob Marloy",
        "email": "threes@littlebirds.com",
        "hashed_password": "fakehashedsecret",
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
    nodes: list[str] = []
    full_name: str | None = None
    disabled: bool | None = None


class UserDBRecord(User):
    hashed_password: str


def get_user(db, username: str) -> UserDBRecord | None:
    if username in db:
        user_dict = db[username]
        return UserDBRecord(**user_dict)


class InvalidCredentials(HTTPException):
    def __init__(self, headers: dict = {"WWW-Authenticate": "Bearer"}):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
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
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise InvalidCredentials(headers)
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(username=username, scopes=token_scopes)
    except (InvalidTokenError, ValidationError):
        raise InvalidCredentials(headers)
    user = get_user(fake_users_db, username=token_data.username)
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


def get_password_hash(password: str):
    return password_hash.hash(password)


def verify_password(plain_password: str | bytes, hashed_password: str | bytes):
    return password_hash.verify(plain_password, hashed_password)


def authenticate_user(
    fake_db: dict, username: str, password: str
) -> tuple[bool, UserDBRecord | None]:
    user = get_user(fake_db, username)
    if user is None:
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


@route.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    authenticated, user = authenticate_user(
        fake_users_db, form_data.username, form_data.password
    )
    if not authenticated or user is None:
        raise InvalidCredentials()
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


@route.get("/users/me/items")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]
