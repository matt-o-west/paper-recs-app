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

from dotenv import load_dotenv
load_dotenv()

#------------------------------------------------------------------------
class GroqProcesser():
    def __init__(self, papers: Papers):
        '''1. From the front end, we’ll receive a list of DOIs that the user has submitted.'''
        self.papers = papers #[DOI, DOI, DOI...]
    
    def fill_in_blanks(self):
        '''2. For each DOI…
            We can get its name + abstract from the CrossRef API 
            We can get a list of articles that cite this paper and a list of articles referenced by this paper'''
        for paper in self.papers:
            doi = paper["doi"]
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
    
    def identify_common_dois():
        '''
        3. Send multiple json payload to the LLM and ask it to identify DOIs that overlap between the papers
        '''
        pass

    def identify_important_papers():
        '''
        4. Iterate through DOIs, use OpenCitations API to see how many times it was referenced. Use this to identify the most important papers?
        '''
        pass

    def find_additional_papers():
        '''
        5. If we don’t have at least 5 papers after going through the previous step, then ask the LLM to recommend X number of papers related to the names of each of the papers the user submitted
        '''
        pass
    
    def return_recommendations():
        pass