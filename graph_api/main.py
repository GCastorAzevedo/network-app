import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from graph_api.api.v1.api import route as api_v1_route

app = FastAPI(
    title="Network App API",
    docs_url="/docs",
    openapi_url="/docs/openapi.json",
    swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
    swagger_ui_init_oauth={
        "clientId": os.getenv("AUTH0_CLIENT_ID"),
        "scopes": ["openid"],
        "usePkceWithAuthorizationCodeGrant": True,
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8964",
        "https://localhost:8964",
        "http://localhost:8080",
        "https://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_route, prefix="/v1")
