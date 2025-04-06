'''
 _______    ___           _______.___________.    ___      .______    __  
|   ____|  /   \         /       |           |   /   \     |   _  \  |  | 
|  |__    /  ^  \       |   (----`---|  |----`  /  ^  \    |  |_)  | |  | 
|   __|  /  /_\  \       \   \       |  |      /  /_\  \   |   ___/  |  | 
|  |    /  _____  \  .----)   |      |  |     /  _____  \  |  |      |  | 
|__|   /__/     \__\ |_______/       |__|    /__/     \__\ | _|      |__|
'''
#------------------------------------------------------------------------
#IMPORTS AND SET UP
from fastapi.middleware.cors import CORSMiddleware
from typing import Union, List
from dotenv import load_dotenv
from methods import Paper, Papers
from pydantic import BaseModel
from typing import List
#------------------------------------------------------------------------
import requests
import uvicorn
import json
from fastapi import FastAPI, HTTPException
import groq_processing 

# Load the env variables
load_dotenv()

app = FastAPI()

origins = [
    #url of frontend server
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware, 
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])

#In-Memory Database: Not an actual database, just an instance of a dictionary that'll go away when the user exits out
memory_db = {"papers": [], "recommended": []}

#------------------------------------------------------------------------
'''
  _____ ___ ___ _____ ___ _  _  ___ 
 |_   _| __/ __|_   _|_ _| \| |/ __|
   | | | _|\__ \ | |  | || .` | (_ |
   |_| |___|___/ |_| |___|_|\_|\___|
'''
# Test Endpoints
@app.get("/")
def read_root():
    return memory_db

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
'''
  ___ _  _ ___    ___  ___ ___ _  _ _____ ___ 
 | __| \| |   \  | _ \/ _ \_ _| \| |_   _/ __|
 | _|| .` | |) | |  _/ (_) | || .` | | | \__ \
 |___|_|\_|___/  |_|  \___/___|_|\_| |_| |___/
'''

#----------
#   GET
#----------

#Return all recommended papers; this function is asynchronous because external APIs will be called within it (a process that takes time)
@app.get("/recommendations", response_model=Papers)
async def get_recommended():

    return Papers(papers = memory_db["recommended"])

#----------
#   POST
#----------

#Adds multiple papers
@app.post("/papers", response_model=Papers)
def add_papers(papers: Papers):

    memory_db["papers"].append(papers["papers"])

    return papers

#------------------------------------------------------------------------

print("Starting FastAPI server...")

if __name__ == "__main__":
    print("Server will be available at http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
