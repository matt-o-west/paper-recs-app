## Fast API server
from fastapi import FastAPI, HTTPException
from typing import Union
from dotenv import load_dotenv
import requests
import uvicorn
import json
import groq
import os

# Load the env variables
load_dotenv()

app = FastAPI()

# Test Endpoints
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


print("Starting FastAPI server...")

if __name__ == "__main__":
    print("Server will be available at http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)