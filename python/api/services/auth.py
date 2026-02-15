import os
import json
import jwt
import requests
from fastapi import HTTPException, Header


issuer = os.environ["AUTH_URL"].rstrip("/")
client_id = os.environ.get("AUTH_CLIENT_ID")

config_url = f"{issuer}/.well-known/openid-configuration"
try:
  config_response = requests.get(config_url)
  config_response.raise_for_status()
  config = config_response.json()
except Exception as e:
  raise Exception(f"Failed to fetch OIDC config from {config_url}: {e}. Response error {getattr(config_response, 'text', '')}")

jwks_url = config.get("jwks_uri")
token_issuer = config.get("issuer", issuer)
if not jwks_url:
  raise Exception(f"OIDC config missing jwks_uri at {config_url}")

try:
  jwks_response = requests.get(jwks_url)
  jwks_response.raise_for_status()
  jwks = jwks_response.json()
except Exception as e:
  raise Exception(f"Failed to fetch OIDC JWKS from {jwks_url}: {e}. Response error {getattr(jwks_response, 'text', '')}")


def _get_public_key(token_header: dict):
  key = None
  for k in jwks.get("keys", []):
    if k.get("kid") == token_header.get("kid"):
      key = k
      break
  if not key:
    raise HTTPException(status_code=401, detail="Invalid token")
  return jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))


def _token_roles(decoded_token: dict):
  roles = set()
  if "roles" in decoded_token and isinstance(decoded_token["roles"], list):
    roles.update(decoded_token["roles"])
  if "scope" in decoded_token and isinstance(decoded_token["scope"], str):
    roles.update(decoded_token["scope"].split())
  if "scp" in decoded_token:
    scp = decoded_token["scp"]
    if isinstance(scp, list):
      roles.update(scp)
    elif isinstance(scp, str):
      roles.update(scp.split())
  if "groups" in decoded_token and isinstance(decoded_token["groups"], list):
    roles.update(decoded_token["groups"])
  if client_id and "resource_access" in decoded_token:
    access = decoded_token["resource_access"].get(client_id, {})
    if "roles" in access:
      roles.update(access["roles"])
  return roles


class TokenVerifier:
  def __init__(self, roles: list = []):
    self.roles = roles

  def __call__(self, authorization: str = Header(None)):
    if not authorization:
      raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
      token = authorization.split(" ")[1]
      header = jwt.get_unverified_header(token)
      public_key = _get_public_key(header)

      options = {"verify_aud": bool(client_id)}
      decode_kwargs = {
        "algorithms": [header.get("alg")],
        "issuer": token_issuer,
        "options": options
      }
      if client_id:
        decode_kwargs["audience"] = client_id

      decoded_token = jwt.decode(token, public_key, **decode_kwargs)

      if self.roles:
        token_roles = _token_roles(decoded_token)
        for role in self.roles:
          if role not in token_roles:
            raise HTTPException(status_code=401, detail=f"Role [{role}] is required.")

      return decoded_token

    except jwt.ExpiredSignatureError:
      raise HTTPException(status_code=401, detail="Token expired")

    except jwt.InvalidTokenError:
      raise HTTPException(status_code=401, detail="Invalid token")