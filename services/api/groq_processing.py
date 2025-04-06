'''
.______        ___       ______  __  ___  _______ .__   __.  _______  
|   _  \      /   \     /      ||  |/  / |   ____||  \ |  | |       \ 
|  |_)  |    /  ^  \   |  ,----'|  '  /  |  |__   |   \|  | |  .--.  |
|   _  <    /  /_\  \  |  |     |    <   |   __|  |  . `  | |  |  |  |
|  |_)  |  /  _____  \ |  `----.|  .  \  |  |____ |  |\   | |  '--'  |
|______/  /__/     \__\ \______||__|\__\ |_______||__| \__| |_______/
'''
#------------------------------------------------------------------------
#IMPORTS AND SET UP
from fastapi import FastAPI, HTTPException
import requests
import json
import pprint

import os
from groq import Groq
from services.api.app import Paper, Papers
from typing import List
from app.py import memory_db

from dotenv import load_dotenv
load_dotenv()

#------------------------------------------------------------------------
class GroqProcesser():
    def __init__(self, papers: Papers):
        '''1. From the front end, we’ll receive a list of Papers (with their DOIs) that the user has submitted.'''
        self.papers = papers
    
    def fill_in_blanks(self):
        '''2. For each DOI…
            We can get its name + abstract from the CrossRef API 
            We can get a list of articles that cite this paper and a list of articles referenced by this paper'''
        for id, paper in enumerate(self.papers):
            paper.id = id #Will make it easier for the LLM to distinguish between separate papers
            
            doi = paper["doi"]

            #---------------
            #   CROSS-REF
            #---------------
            #HOW-TO: https://gitlab.com/crossref/tutorials/intro-to-crossref-api-using-python, https://api.crossref.org/swagger-ui/index.html, https://www.crossref.org/documentation/retrieve-metadata/rest-api/
            doi_url = doi.replace("/", "%2F")
            url = f'https://api.crossref.org/works/{doi_url}'

            r = requests.get(url)
            print(f"The status code is: {r.status_code}")

            if r.status_code == 200:
                js = r.json()
            else:
                raise HTTPException(status_code=502, detail="DOI not found in CrossRef API")
            
            if 'title' in js["message"]:
                paper.name = js["message"]["title"]
            
            if 'abstract' in js["message"]:
                paper.abstract = js["message"]["abstract"]
            
            #---------------------
            #   OPEN-CITATIONS
            #---------------------
            #HOW-TO: https://opencitations.net/index/api/v2
            TOKEN = os.environ.get("OC_API_KEY")
            REF_API_CALL = f"https://opencitations.net/index/api/v2/references/doi:{doi}"
            CITE_API_CALL = f"https://opencitations.net/index/api/v2/citation/doi:{doi}"
            HTTP_HEADERS = {"authorization": TOKEN}

            r = requests.get(REF_API_CALL, headers=HTTP_HEADERS)
            print(f"The status code is: {r.status_code}")

            if r.status_code == 200:
                js = r.json()
            else:
                raise HTTPException(status_code=502, detail="DOI not found in OpenCitations API")
    
    def identify_common_dois(self):
        '''
        3. GROQ: Send multiple json payload/file to the LLM and ask it to identify DOIs that overlap between the papers
        '''
        '''
        JSON File will look like this
        [
            {
            id: 1
            doi: "DOI",
            name: "NAME",
            abstract: "ABSTRACT....",
            references: ["DOI1", "DOI2", "DOI3", ...],
            cited_by: ["DOI1", "DOI2", "DOI3", ...]
            },

            {
            id: 2
            doi: "DOI",
            name: "NAME",
            abstract: "ABSTRACT....",
            references: ["DOI1", "DOI2", "DOI3", ...],
            cited_by: ["DOI1", "DOI2", "DOI3", ...]
            },

            ...
        ]
        '''
        pass

    def identify_important_papers(self):
        '''
        4. Iterate through DOIs, use OpenCitations API to see how many times it was referenced. Use this to identify the most important papers?
        '''
        citation_number = {}
        for paper in self.paper:
            doi = paper["doi"]
            APICALL = f"https://opencitations.net/api/v1/citation-count/{doi}"
            HTTP_HEADERS = {"authorization": "feebb3c7-2e1f-4337-a7fb-c32a773cba1a"}
            response = get(APICALL, headers=HTTP_HEADERS)
            if response.status_code == 200:
                data = response.json()
                if data and 'count' in data[0]:
                    citation_count = data[0]['count']
                    citation_number[doi] = citation_count
                else:
                    raise HTTPException(response.status_code, detail="Citation Number not Found in OpenCitations Database.")
            else:
                    raise HTTPException(response.status_code, detail="Citation Number not Found in OpenCitations Database.")
        top_5_papers = dict(sorted(citation_number.items(), key=lambda item: item[1], reverse=True)[:5])
        paper_number = (len(top_5_papers))
        if paper_number == 5:
            return_recommendations(top_5_papers)
        else:
            find_additional_papers()
        pass

    def find_additional_papers(self):
        '''
        5. GROQ: If we don’t have at least 5 papers after going through the previous step, then ask the LLM to recommend X number of papers related to the names of each of the papers the user submitted
        '''
        pass
    
    def return_recommendations(self):
        pass

    #------------------------------------------------------------------------
    def validate(self):
        invalid_papers = []
        for paper in self.paper:
            doi = paper["doi"]
            APICALL = f"https://opencitations.net/api/v1/citation-count/{doi}"
            HTTP_HEADERS = {"authorization": "feebb3c7-2e1f-4337-a7fb-c32a773cba1a"}
            response = get(APICALL, headers=HTTP_HEADERS)
            if response.status_code != 200:
                invalid_papers.append(doi)
                raise HTTPException(status_code=502, detail="DOI not found in OpenCitations API")
        for paper in self.paper:
            doi = paper["doi"]
            doi_url = doi.replace("/", "%2F")
            url = f'https://api.crossref.org/works/{doi_url}'
            r = requests.get(url)
            if r.status_code != 200:
                raise HTTPException(status_code=502, detail="DOI not found in CrossRef API")
        if len(invalid_papers) > 1:
            return "Here is a list of invalid papers: {invalid_papers}"
        if len(invalid_papers) == 0:
            for paper in self.paper
                memory_db['papers'].append(paper)
            return self.paper
