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
from app import Paper, Papers
from typing import List

from dotenv import load_dotenv
load_dotenv()

#------------------------------------------------------------------------
class GroqProcesser():
    def __init__(self, papers: Papers):
        '''1. From the front end, we'll receive a list of Papers (with their DOIs) that the user has submitted.'''
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
        # Get the Groq API key from environment variables
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY environment variable not set")
        
        # Initialize the Groq client
        client = Groq(api_key=groq_api_key)
        
        # Convert papers to the format expected by the LLM
        papers_data = []
        for paper in self.papers:
            paper_dict = {
                "id": paper.id,
                "doi": paper.doi,
                "name": paper.name,
                "abstract": paper.abstract,
                "references": paper.references,
                "cited_by": paper.cited_by
            }
            papers_data.append(paper_dict)
        
        # Create the prompt for the LLM
        prompt = f"""
        Analyze the following list of academic papers and identify DOIs that appear in multiple papers (either in references or cited_by lists).
        For each overlapping DOI, explain why it's significant in the context of these papers.
        
        Papers data:
        {json.dumps(papers_data, indent=2)}
        
        Please provide your analysis in the following JSON format:
        {{
            "overlapping_dois": [
                {{
                    "doi": "DOI_VALUE",
                    "appears_in_papers": [PAPER_IDS],
                    "significance": "Explanation of why this paper is significant in the context of the provided papers"
                }}
            ],
            "analysis": "Overall analysis of the relationships between these papers"
        }}
        """
        
        # Call the Groq API
        try:
            completion = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",  # Using a model with large context window
                messages=[
                    {"role": "system", "content": "You are an expert in academic literature analysis. Your task is to identify overlapping references between papers and explain their significance."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Lower temperature for more focused responses
                max_completion_tokens=1024,
                top_p=1,
                stream=False,
                response_format={"type": "json_object"},
                stop=None,
            )
            
            # Parse the response
            response_text = completion.choices[0].message.content
            
            # Extract the JSON part from the response
            try:
                # Find JSON content between curly braces
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    result = json.loads(json_str)
                    return result
                else:
                    raise ValueError("No valid JSON found in the response")
            except json.JSONDecodeError:
                # If the response isn't valid JSON, return it as is
                return {"raw_response": response_text}
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error calling Groq API: {str(e)}")

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
        

    def find_additional_papers(self):
        '''
        5. GROQ: If we don't have at least 5 papers after going through the previous step, then ask the LLM to recommend X number of papers related to the names of each of the papers the user submitted
        '''
        pass
    
    def return_recommendations(self):
        pass

    #------------------------------------------------------------------------
    def validate(self):
        """
        Validate that all required data is present for processing.
        Returns True if valid, raises HTTPException if not.
        """
        if not self.papers:
            raise HTTPException(status_code=400, detail="No papers provided")
        
        for paper in self.papers:
            if not paper.doi:
                raise HTTPException(status_code=400, detail="Paper missing DOI")
        
        return True
        
