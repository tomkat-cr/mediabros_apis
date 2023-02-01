import datetime
from typing import Union
from pydantic import BaseModel

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from .model_users import fetch_user_by_entryname, User, UserInDB
from .settings import settings
from .utility_password import verify_password
from .utility_general import log_debug, log_warning


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user(username: str):
    try:
        fields = {'_id': 0}
        resultset = fetch_user_by_entryname('username', username, fields)
        if not resultset['error'] and resultset['found']:
            log_debug('get_user is OK and will return User(**)')
            return User(**resultset['resultset'])
    except Exception as err:
        log_debug(f'get_user ERROR: {str(err)}')


def get_user_hashed_password(username: str):
    try:
        # fields = {'username': 1, 'hashed_password': 1, '_id': 0}
        fields = {'_id': 0}
        resultset = fetch_user_by_entryname('username', username, fields)
        if not resultset['error'] and resultset['found']:
            log_debug(
                'get_user_hashed_password.resultset:' +
                f" {str(resultset['resultset'])}"
            )
            response = UserInDB(**resultset['resultset'])
            log_debug(
                'get_user_hashed_password.response:' +
                f" {str(response)}"
            )
            return response
    except Exception as err:
        log_debug(f'get_user_hashed_password ERROR: {str(err)}')


def authenticate_user(username: str, password: str):
    log_debug(f'authenticate_user.username: {username}, password: {password}')
    try:
        user = get_user_hashed_password(username)
        log_debug(f'authenticate_user.user: {user}')
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        log_debug('authenticate_user: ALL CLEAR OK')
        return user
    except Exception as err:
        log_debug(f'authenticate_user ERROR: {str(err)}')


def create_access_token(
    data: dict,
    expires_delta: Union[datetime.timedelta, None] = None
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    log_debug(f'login_for_access_token.form_data = {form_data}')
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        log_warning("ERROR on login: Incorrect username or password")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        access_token_expires = datetime.timedelta(
            minutes=float(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        access_token = create_access_token(
             data={"sub": user.username}, expires_delta=access_token_expires
        )
        response = {
            "access_token": access_token, "token_type": "bearer"
        }
        log_debug(f'login_for_access_token.response = {response}')
        return response
    except Exception as err:
        log_debug(f'login_for_access_token ERROR: {str(err)}')
