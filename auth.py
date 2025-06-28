from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import APIKeyHeader
from passlib.hash import bcrypt
from jose import jwt, JWTError
from db import db
import uuid

router = APIRouter()
SECRET = "SECRET_KEY"

# ✅ This makes Swagger show the "Authorize" button
oauth2_scheme = APIKeyHeader(name="Authorization")

# ✅ This is the ONLY get_current_user you need
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        user = await db.users.find_one({"_id": payload["sub"]})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/register")
async def register(data: dict):
    if await db.users.find_one({"email": data["email"]}):
        raise HTTPException(400, "Email already used")
    user_id = str(uuid.uuid4())
    hashed_pw = bcrypt.hash(data["password"])
    await db.users.insert_one({
        "_id": user_id,
        "email": data["email"],
        "password": hashed_pw
    })
    return {"msg": "Registered"}

@router.post("/login")
async def login(data: dict):
    user = await db.users.find_one({"email": data["email"]})
    if not user or not bcrypt.verify(data["password"], user["password"]):
        raise HTTPException(401, "Invalid credentials")
    token = jwt.encode({"sub": user["_id"]}, SECRET, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}
