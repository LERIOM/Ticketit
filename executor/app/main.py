"""Initial authenticated health endpoint; business routes come later."""

import os
import secrets
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    version: Literal["1.0"] = "1.0"


def create_app() -> FastAPI:
    # No default credential: a missing server secret never authorizes a request.
    expected_key = os.environ.get("EXECUTOR_API_KEY", "")

    def authenticate(key: str | None = Security(api_key_header)) -> None:
        if not expected_key or not key or not secrets.compare_digest(
            key.encode("utf-8"), expected_key.encode("utf-8")
        ):
            raise HTTPException(status_code=401, detail="Invalid or missing API key")

    application = FastAPI(
        title="executor",
        version="1.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        dependencies=[Depends(authenticate)],
    )

    @application.get("/v1/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse()

    return application


app = create_app()
