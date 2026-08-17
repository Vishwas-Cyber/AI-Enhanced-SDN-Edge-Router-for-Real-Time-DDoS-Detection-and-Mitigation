from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal
import json
import os
import secrets

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

ROOT=Path(__file__).resolve().parents[1]
TOPOLOGY=ROOT/"configs/topology.json"
EVENTS=ROOT/"results/events.jsonl"

app=FastAPI(title="SDN Sentinel API",version="1.0.0",description="Authorized SDN security telemetry API")

class LoginRequest(BaseModel):
    username:str
    password:str

class TokenResponse(BaseModel):
    access_token:str
    token_type:str="bearer"
    role:str

class Node(BaseModel):
    id:str=Field(min_length=1,max_length=64,pattern=r"^[A-Za-z0-9_-]+$")
    kind:Literal["host","switch","router","controller"]
    label:str
    detail:str=""

class Link(BaseModel):
    source:str
    target:str
    state:Literal["healthy","control","attack"]="healthy"
    pps:float=Field(default=0,ge=0)

class Topology(BaseModel):
    nodes:list[Node]
    links:list[Link]

TOKENS={}
USERS={"admin":{"password":os.getenv("SDN_ADMIN_PASSWORD","change-me-now"),"role":"admin"},"analyst":{"password":os.getenv("SDN_ANALYST_PASSWORD","change-me-now"),"role":"analyst"}}


def auth(authorization:str|None=Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401,detail="Bearer token required")
    record=TOKENS.get(authorization[7:])
    if not record or record["expires"]<datetime.now(timezone.utc):
        raise HTTPException(status_code=401,detail="Invalid or expired token")
    return record


def admin(user=Depends(auth)):
    if user["role"]!="admin": raise HTTPException(status_code=403,detail="Admin role required")
    return user

@app.get("/health")
def health(): return {"status":"ok","service":"sdn-sentinel-api"}

@app.post("/auth/login",response_model=TokenResponse)
def login(body:LoginRequest):
    user=USERS.get(body.username)
    if not user or not secrets.compare_digest(user["password"],body.password):
        raise HTTPException(status_code=401,detail="Invalid credentials")
    token=secrets.token_urlsafe(32); TOKENS[token]={"username":body.username,"role":user["role"],"expires":datetime.now(timezone.utc)+timedelta(hours=8)}
    return TokenResponse(access_token=token,role=user["role"])

@app.get("/topology",response_model=Topology)
def get_topology(user=Depends(auth)):
    data=json.loads(TOPOLOGY.read_text()) if TOPOLOGY.exists() else {"nodes":[],"links":[]}
    return data

@app.put("/topology",response_model=Topology)
def put_topology(data:Topology,user=Depends(admin)):
    ids={n.id for n in data.nodes}
    if any(link.source not in ids or link.target not in ids or link.source==link.target for link in data.links):
        raise HTTPException(status_code=422,detail="Links must reference distinct existing nodes")
    TOPOLOGY.write_text(json.dumps(data.model_dump(),indent=2))
    return data

@app.get("/events")
def get_events(limit:int=100,user=Depends(auth)):
    limit=max(1,min(limit,1000)); rows=[]
    if EVENTS.exists():
        for line in EVENTS.read_text().splitlines()[-limit:]:
            try: rows.append(json.loads(line))
            except json.JSONDecodeError: pass
    return {"count":len(rows),"events":rows}
