import copy
import os
import uvicorn
from fastapi import FastAPI, Depends, Query, Response, Header
from fastapi.staticfiles import StaticFiles
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
@app.head("/meta")
def head_root():
  return {"status": "OK"}

@app.get("/meta")
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

@app.get("/layers")
def get_geojson(_: dict = Depends(TokenVerifier()), 
                date: Optional[datetime] = Query(None)):
  layers = copy.deepcopy(app.state.layers_cache)
  layers = filter_dates(layers, date=date)
  return layers

# Mount static files (built frontend) in production
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
  app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000, reload=True)