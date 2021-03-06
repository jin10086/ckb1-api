import os
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional, List
import motor.motor_asyncio

app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient()
db = client.college

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class TokenModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    address: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Jane Doe",
                "address": "ckt1qyqyqg9gehfs8ymc95vttuhh6qdp6m8x25sq8wldnk",
            }
        }


@app.post("/api/create_token", response_description="Add new token", response_model=TokenModel)
async def create_token(token: TokenModel = Body(...)):
    token = jsonable_encoder(token)
    token['amount'] = 100000000
    new_token = await db["token"].insert_one(token)
    created_token = await db["token"].find_one({"_id": new_token.inserted_id})
    ret = { "status": 1, "name": created_token['name'], "amount": created_token['amount'], "txhash": "", }
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=ret)

@app.get(
    "/api/gettoken/{address}", response_description="Get a token info", response_model=TokenModel
)
async def show_token(address: str):
    token = await db["token"].find_one({"address": address})
    if token is not None:
        return token

    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": 0, "msg": "address not found"})
