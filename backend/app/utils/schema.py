from typing import Optional, List
from pydantic import BaseModel,HttpUrl
from datetime import datetime
from IPython.core.display import Markdown
from typing import Type
# if image as type
# from typing import Any
# import os
# from pydantic import constr, validator



# Authorisation response models
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class SignUpRequest(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None


# Node response models
class NodeBase(BaseModel):
    node_id: int
    labels: list


class Node(NodeBase):
    properties: Optional[dict] = None


class Nodes(BaseModel):
    nodes: List[Node]


# User response models
class User(BaseModel):
    username: str
    full_name: Optional[str] = None
    joined: Optional[datetime] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


# Relationship response models
class Relationship(BaseModel):
    relationship_id: int
    relationship_type: str
    source_node: Node
    target_node: Node
    properties: Optional[dict] = None


# Query response model
class Query(BaseModel):
    response: list
    
class card(BaseModel):
    title:str
    # content: type[Markdown]
    content:str
    image_caption: str
    image_link:HttpUrl

    # image_path: constr(regex=r'.*\.(jpg|jpeg|png|gif)$')

    # @validator('image_path')
    # def check_image_path(cls, value: Any) -> Any:
    #     # Check if it's a valid URL
    #     try:
    #         result = urlparse(value)
    #         if all([result.scheme, result.netloc]):
    #             return value
    #     except ValueError:
    #         pass

    #     # Check if it's a valid file path
    #     if os.path.isfile(value) and value.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
    #         return value
        
    #     raise ValueError('Invalid image path or URL')

class card_batch(BaseModel):
    cards:List[card]