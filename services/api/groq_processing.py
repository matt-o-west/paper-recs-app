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

import os
from groq import Groq
from models import Paper, Papers
from typing import List

from dotenv import load_dotenv
load_dotenv()

from codetiming import Timer
import asyncio
import aiohttp

#------------------------------------------------------------------------
class GroqProcesser():
    def __init__(self, papers: Papers):
        '''1. From the front end, we'll receive a list of Papers (with their DOIs) that the user has submitted.'''
        self.papers = papers
        self.common_dois = []
        self.recommendations = []

        self.groq_api_key = os.environ.get("GROQ_API_KEY")
        if not self.groq_api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY environment variable not set")
        
        self.oc_api_key = os.environ.get("OC_API_KEY")
        if not self.oc_api_key:
            raise HTTPException(status_code=500, detail="OC_API_KEY environment variable not set")
    
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
            

            REF_API_CALL = f"https://opencitations.net/index/api/v2/references/doi:{doi}"
            CITE_API_CALL = f"https://opencitations.net/index/api/v2/citations/doi:{doi}"
            HTTP_HEADERS = {"authorization": self.oc_api_key}

            js = self.api_call(REF_API_CALL, 'OpenCitations', HTTP_HEADERS)
            self.add_related_paper_dois(js, "cited", paper.references)

            js = self.api_call(CITE_API_CALL, 'OpenCitations', HTTP_HEADERS)
            self.add_related_paper_dois(js, "citing", paper.cited_by)
    
    def identify_common_dois(self):
        '''
        3. GROQ: Send multiple json payload/file to the LLM and ask it to identify DOIs that overlap between the papers
        '''
        # Get the Groq API key from environment variables - Done in __init__
        
        # Initialize the Groq client
        client = Groq(api_key=self.groq_api_key)
        
        # Convert papers to the format expected by the LLM
        papers_data = []
        for paper in self.papers:
            paper_dict = {
                "id": paper.id,
                "doi": paper.doi,
                "name": paper.name,
                "abstract": paper.abstract,
                "references": paper.references[:75],
                "cited_by": paper.cited_by[:75]
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
    
                    self.common_dois = result['overlapping_dois']
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

        for paper in self.common_dois:
            doi = paper["doi"]
            
            API_CALL = f"https://opencitations.net/api/v1/citation-count/{doi}"
            HTTP_HEADERS = {"authorization": self.oc_api_key}

            response = requests.get(API_CALL, headers=HTTP_HEADERS)
            if response.status_code == 200:
                data = response.json()
                if data and 'count' in data[0]:
                    citation_count = data[0]['count']
                    citation_number[doi] = citation_count

        top_5_papers = sorted(citation_number, key=lambda doi: citation_number[doi], reverse=True)[:5]
        
        self.recommendations = top_5_papers
        print(self.recommendations)
        return top_5_papers

    def find_additional_papers(self):
        '''
        5. GROQ: If we don't have at least 5 papers after going through the previous step, then ask the LLM to recommend X number of papers related to the names of each of the papers the user submitted
        '''
        num_papers_needed = 5 - len(self.recommendations)
        paper_names = [paper.name for paper in self.papers]

        client = Groq( api_key=self.groq_api_key)

        chat_completion = client.chat.completions.create(
            messages=[
                # Set an optional system message. This sets the behavior of the
                # assistant and can be used to provide specific instructions for
                # how it should behave throughout the conversation.
                {
                    "role": "system",
                    "content": "you are an expert scientific researcher who will help recommend papers to me."
                },
                # Set a user message for the assistant to respond to.
                {
                    "role": "user",
                    "content": f"Recommended papers related to {paper_names} that are not already in the list. Please provide {num_papers_needed} papers. Return the DOIs only in the form of a string with spaces between each DOI.",
                }
            ],
            model="llama-3.3-70b-versatile",
        )

        papers = (chat_completion.choices[0].message.content).split()
        self.recommendations.extend(papers)
        print(self.recommendations)
        return papers
        
    
    def return_recommendations(self):
        self.fill_in_blanks()
        self.identify_common_dois()
        self.identify_important_papers()
        
        if len(self.recommendations) != 5:
            self.find_additional_papers()
        
        result = []
        for paper in self.recommendations:
            result.append(Paper(doi=paper))
        
        return result

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
    
    def validate(papers: Papers):
        '''Validate the DOIs using the OpenCitations API and CrossRef API'''

        invalid_papers = []
        valid_papers = []

        for paper in papers:
            doi = paper.doi
            API_CALL = f"https://opencitations.net/api/v1/citation-count/{doi}"
            HTTP_HEADERS = {"authorization": "feebb3c7-2e1f-4337-a7fb-c32a773cba1a"}
            response = requests.get(API_CALL, headers=HTTP_HEADERS)
            if response.status_code != 200:
                invalid_papers.append(doi)
            else:
                valid_papers.append(paper)
        
        for paper in valid_papers:
            doi = paper.doi
            doi_url = doi.replace("/", "%2F")
            url = f'https://api.crossref.org/works/{doi_url}'
            r = requests.get(url)
            if r.status_code != 200:
                invalid_papers.append(doi)
        
        return invalid_papers

if __name__ == "__main__":
    with Timer(text="\nTotal elapsed time: {:.1f}"):
        papers = [
            Paper(doi= "10.1677/erc.1.0978"),
            Paper(doi="10.1016/j.gde.2006.12.005"),
            Paper(doi="10.1093/jnci/djg123"),
        ]
        gp = GroqProcesser(papers)
        print(gp.return_recommendations())
