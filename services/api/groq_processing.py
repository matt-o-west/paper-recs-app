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
from fastapi import HTTPException
import requests
import json
import pprint

import os
from groq import Groq
from models import Paper, Papers
from typing import List

from dotenv import load_dotenv
load_dotenv()

from codetiming import Timer

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
            paper.id = id + 1 #Will make it easier for the LLM to distinguish between separate papers
            
            doi = paper.doi

            #---------------
            #   CROSS-REF
            #---------------
            #HOW-TO: https://gitlab.com/crossref/tutorials/intro-to-crossref-api-using-python, https://api.crossref.org/swagger-ui/index.html, https://www.crossref.org/documentation/retrieve-metadata/rest-api/
            doi_url = doi.replace("/", "%2F")
            url = f'https://api.crossref.org/works/{doi_url}'

            js = self.api_call(url, 'CrossRef')
            
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
            CITE_API_CALL = f"https://opencitations.net/index/api/v2/citations/doi:{doi}"
            HTTP_HEADERS = {"authorization": TOKEN}

            js = self.api_call(REF_API_CALL, 'OpenCitations', HTTP_HEADERS)
            self.add_related_paper_dois(js, "cited", paper.references)

            js = self.api_call(CITE_API_CALL, 'OpenCitations', HTTP_HEADERS)
            self.add_related_paper_dois(js, "citing", paper.cited_by)
    
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
        pass

    def find_additional_papers(self):
        '''
        5. GROQ: If we don’t have at least 5 papers after going through the previous step, then ask the LLM to recommend X number of papers related to the names of each of the papers the user submitted
        '''
        pass
    
    def return_recommendations(self):
        pass

    #------------------------------------------------------------------------
    #HELPER FUNCTIONS
    def api_call(self, url: str, api_name: str, http_headers: str = None):
        if http_headers:
            r = requests.get(url)
        else:
            r = requests.get(url, headers = http_headers)
        print(f"The status code is: {r.status_code}")

        if r.status_code == 200:
            js = r.json()
        else:
            raise HTTPException(status_code=502, detail=f"DOI not found in {api_name} API")
        
        return js
    
    def add_related_paper_dois(self, js, relation: str, lst: List[str]):
        #The "cited" and "citing" keys have a string with multiple ID types associated with it
        for item in js:
                citation = item[relation].split()
                for id_format in citation:
                    if id_format[0] == 'd':
                        lst.append(id_format[4:])
                        break

    def validate(self):
        pass

if __name__ == "__main__":
    with Timer(text="\nTotal elapsed time: {:.1f}"):
        papers = [
            Paper(doi= "10.1186/1756-8722-6-59"),
            Paper(doi="10.1046/j.1471-4159.2003.01615.x"),
            Paper(doi="10.2307/1941948")
        ]
        gp = GroqProcesser(papers)
        gp.fill_in_blanks()
        print(gp.papers)