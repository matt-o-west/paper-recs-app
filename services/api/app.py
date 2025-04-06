## Fast API server
from fastapi import FastAPI, HTTPException
from typing import Union, List, Optional
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
import uvicorn
import json
import groq
import os

# Load the env variables
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js port here to allow CORS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Paper(BaseModel):
    doi: str
    name: Optional[str] = None
    abstract: Optional[str] = None
    references: List[str] = []
    cited_by: List[str] = []

class Papers(BaseModel):
    papers: List[Paper]

class PaperInput(BaseModel):
    papers: List[str]

# Test Endpoints
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

# Mock API endpoint
@app.post("/recommendations/", response_model=Papers)
async def recommend_papers(paper_input: PaperInput):
    # Log the received DOIs
    print(f"Received DOIs: {paper_input.papers}")
    
    # Mock response with two static papers
    mock_papers = Papers(
        papers=[
            Paper(
                doi="doi:10.1145/3383313.3412243",
                name="Deep Learning-based Document Modeling for Personalized Content Recommendation",
                abstract="In this paper, we present a deep learning-based approach to document modeling for personalized recommendation systems. We leverage neural embeddings to capture semantic relationships between documents and user preferences.",
                references=["doi:10.1109/TPAMI.2020.2992393", "doi:10.1145/3397271.3401063"],
                cited_by=["doi:10.1145/3383313.3412244", "doi:10.1145/3383313.3412245"]
            ),
            Paper(
                doi="doi:10.1109/TPAMI.2020.2992393",
                name="Graph Neural Networks: A Review of Methods and Applications",
                abstract="Graph Neural Networks (GNNs) have been widely studied in various domains including social networks, knowledge graphs, recommendation, and natural language processing.",
                references=["doi:10.1145/3383313.3412243"],
                cited_by=["doi:10.1145/3397271.3401063", "doi:10.1145/3383313.3412245"]
            )
        ]
    )

    return mock_papers

print("Starting FastAPI server...")

if __name__ == "__main__":
    print("Server will be available at http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)