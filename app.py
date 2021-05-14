import os
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional, List
import motor.motor_asyncio

app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient()
db = client.college


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


@app.post("/create_token", response_description="Add new token", response_model=TokenModel)
async def create_token(token: TokenModel = Body(...)):
    token = jsonable_encoder(token)
    token['amount'] = 100000000
    new_token = await db["token"].insert_one(token)
    created_token = await db["token"].find_one({"_id": new_token.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_token)
