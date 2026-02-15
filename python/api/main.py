import copy
import os
import uvicorn
from fastapi import FastAPI, Depends, Query, Response, Header
from fastapi.responses import FileResponse
from fastapi_utils.tasks import repeat_every
from typing import Optional
from datetime import datetime

from api.services.glad import update_layers, get_meta, filter_dates
from api.services.auth import TokenVerifier
from api.services.util import generate_etag


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.state.layers_cache = {}

# Tasks
@app.on_event("startup")
@repeat_every(seconds=86400)
def task_update_tiles() -> None:
  app.state.layers_cache = update_layers()

# Routes
@app.head("/api/meta")
def head_root():
  return {"status": "OK"}

@app.get("/api/meta")
def get_root(_: dict = Depends(TokenVerifier()), 
             response: Response = None,
             if_none_match: str | None = Header(default=None)):
  meta = get_meta()
  # Cloudflare tunnel requires string ETag
  response.headers["ETag"] = f'"{generate_etag(meta)}"'
  
  if if_none_match in [response.headers["ETag"], f'W/{response.headers["ETag"]}']:
    return Response(status_code=304)
  else:
    return meta

@app.get("/api/layers")
def get_geojson(_: dict = Depends(TokenVerifier()), 
                date: Optional[datetime] = Query(None)):
  layers = copy.deepcopy(app.state.layers_cache)
  layers = filter_dates(layers, date=date)
  return layers

# Serve static files and SPA fallback
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
  """Serve static files or fallback to index.html for SPA routing"""
  file_path = os.path.join(static_dir, full_path)
  if os.path.isfile(file_path):
    return FileResponse(file_path)
  # Fallback to index.html for SPA routes (callback, etc)
  return FileResponse(os.path.join(static_dir, "index.html"))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000, reload=True)