"""Vercel entrypoint: exposes the FastAPI `app`."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI

from earnsure.routes import router

app = FastAPI(title="EarnSure API", docs_url="/api/docs", openapi_url="/api/openapi.json")
app.include_router(router)


@app.get("/api/ping")
def ping():
    return {"ok": True}
