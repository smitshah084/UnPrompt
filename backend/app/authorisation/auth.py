# General packages and modules
from datetime import datetime, timedelta, timezone
from typing import Optional
import time

# FastAPI modules for authorisation
from fastapi import Depends, APIRouter, HTTPException, status # type: ignore
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm # type: ignore


# Modules for encryption and security
from jose import JWTError, jwt 
from passlib.context import CryptContext # type: ignore


# Import utilities functions, configuration and schemas
from app.utils.environment import Config
from app.utils.db import neo4j_driver
from app.utils.schema import Token, TokenData, User, UserInDB


# Set the API Router
router = APIRouter()

# Generate password hash
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def create_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, password_hash):
    return pwd_context.verify(plain_password, password_hash)


# Search the database for user with specified username
def get_user(username: str):
    query = f'MATCH (a:User) WHERE a.username = \'{username}\' RETURN a'

    with neo4j_driver.session() as session:
        user_in_db = session.run(query)
        user_data = user_in_db.data()[0]['a']
        return UserInDB(**user_data)


# Authenticate user by checking they exist and that the password is correct
def authenticate_user(username, password):
    # First, retrieve the user by the email provided
    user = get_user(username)
    if not user:
        return False

    # If present, verify password against password hash in database
    password_hash = user.hashed_password
    username = user.username

    return user if verify_password(password, password_hash) else False


# Create access token, required for OAuth2 flow
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, Config.SECRET_KEY, algorithm=Config.ALGORITHM)


# Decrypt the token and retrieve the username from payload
async def get_current_user(token: str = Depends(oauth2_scheme)):
    print('in get_current_user')
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as e:
        raise credentials_exception from e
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# Confirm that user is not disabled as a user
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    print('in get current active user')
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Endpoint for token authorisation
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Endpoint for creating first user, at launch with appliaction password rather than user credentials
@router.post('/launch_user')
async def first_user(username: str,
                     password: str,
                     full_name: Optional[str] = None):
                    #  application_password: str,

    # Check application password is correct
    # if application_password != Config.APP_PASSWORD and False:
    #     denial = HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Incorrect application password, please try again.",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    #     time.sleep(1)
    #     return denial

    # Create dictionary of new user attributes
    attributes = {
        'username': username,
        'full_name': full_name,
        'hashed_password': create_password_hash(password),
        'joined': str(datetime.now(timezone.utc)),
        'disabled': False,
    }

    # Write Cypher query and run against the database
    cypher_search = 'MATCH (user:User) WHERE user.username = $username RETURN user'
    cypher_create = 'CREATE (user:User $params) RETURN user'

    with neo4j_driver.session() as session:
        # First, run a search of users to determine if username is already in use
        check_users = session.run(query=cypher_search, parameters={'username': username})

        # Return error message if username is already in the database
        if check_users.data():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Operation not permitted, user with username {username} already exists.",
                headers={"WWW-Authenticate": "Bearer"}
            )

        response = session.run(query=cypher_create, parameters={'params': attributes})
        user_data = response.data()[0]['user']
    return User(**user_data)


from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Form, Request


templates = Jinja2Templates(directory="Frontend/public")

@router.get('/')
async def login_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})