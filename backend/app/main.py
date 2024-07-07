# Import main FastAPI modules
from fastapi import FastAPI, Depends # type: ignore


# Internal packages
from app.authorisation import auth
from app.authorisation.auth import get_current_active_user
from app.user_management import users
from app.graph import crud
from app.query import cypher
from app.content import content_delivery


app = FastAPI(title='Fast-graph',
              description='API built for Neo4j with FastAPI',
              version="0.1",
              docs_url='/docs',
              redoc_url='/redoc')

app.include_router(
    auth.router,
    prefix='/auth',
    tags=['Authorisation']
)

app.include_router(
    content_delivery.router,
    prefix='/content',
    tags=['Content'],
    dependencies=[Depends(get_current_active_user)]
)

app.include_router(
    users.router,
    prefix='/users',
    tags=['Users'],
    dependencies=[Depends(get_current_active_user)]
)

app.include_router(
    crud.router,
    prefix='/graph',
    tags=['Graph Objects'],
    dependencies=[Depends(get_current_active_user)]
)

app.include_router(
    cypher.router,
    tags=['Query Database'],
    dependencies=[Depends(get_current_active_user)]
)

