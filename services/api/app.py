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
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Union
from dotenv import load_dotenv


from groq_processing import GroqProcesser
import uvicorn
from models import Paper, Papers
import json
from fastapi.encoders import jsonable_encoder

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

gp = None 

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

#------------------------------------------------------------------------
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
    gp = GroqProcesser(memory_db["papers"])
    memory_db["recommended"] = await gp.get_recommendations()
    return Papers(papers = memory_db["recommended"], status_code=200)

#----------
#   POST
#----------

#Adds multiple papers
@app.post("/papers", response_model=Papers)
def add_papers(papers: Papers):
    
    invalid_papers = GroqProcesser.validate(papers.papers)

    if invalid_papers:
        return Papers(papers = invalid_papers, status_code=400)
    else:
        memory_db["papers"].append(papers.papers)
        return Papers(papers = papers.papers, status_code=200)

#------------------------------------------------------------------------

print("Starting FastAPI server...")

if __name__ == "__main__":
    # print("Server will be available at http://localhost:8000")
    # uvicorn.run(app, host="127.0.0.1", port=8000)

    papers = [
            Paper(doi= "10.1677/erc.1.0978"),
            Paper(doi="10.1016/j.gde.2006.12.005"),
            Paper(doi="10.1093/jnci/djg123"),
        ]
    
    print(add_papers(Papers(papers = papers)))
    

#------------------------------------------------------------------------
