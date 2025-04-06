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

    #-----------------------------------
    '''2. For each DOI…
            We can get its name + abstract from the CrossRef API 
            We can get a list of articles that cite this paper and a list of articles referenced by this paper'''
    async def fill_task(self, 
                   name, work_queue, 
                   api_name: str, url: str, 
                   subroutine = None, extra_param = None,
                   token: str = None):
        timer = Timer(text=f"Task {name} elapsed time: {{:.1f}}")
       
        async with aiohttp.ClientSession() as session:
            
            while not work_queue.empty():
                paper = await work_queue.get()
                doi = paper.doi
                doi_url = doi.replace("/", "%2F")
                url = f'{url}{doi_url}'
                print(f"Task {name} getting URL: {doi}")

                headers = None
                if token:
                    headers = {"authorization": token}
                
                timer.start()
                async with session.get(url, headers=headers) as response:
                    r = response
                    if r.status == 200:
                        js = await r.json()
                    else:
                        print(r.status)
                        raise HTTPException(status_code=502, detail=f"{doi} not found in {api_name} API")
                    
                    if subroutine:
                        subroutine(js, paper, extra_param)
                
                timer.stop()


    #-----------------------------------
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


    #-----------------------------------
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
        print(chat_completion.choices[0].message.content)

        papers = (chat_completion.choices[0].message.content).split()
        self.recommendations.extend(papers)
        print(self.recommendations)
        return papers
        

    #-----------------------------------
    async def return_recommendations(self):
        """
        Step 1
        """
        # Create the queue of work
        cr_queue = asyncio.Queue()
        occ_queue = asyncio.Queue()
        ocr_queue = asyncio.Queue()

        # Put some work in the queue
        for paper in self.papers:
            await cr_queue.put(paper)
            await occ_queue.put(paper)
            await ocr_queue.put(paper)
        
        # Create a list to hold all tasks
        tasks = []
        task_marker = 0

        for _ in range(len(self.papers)):
            tasks.append(
                asyncio.create_task(self.fill_task(str(task_marker), cr_queue, "CrossRef", "https://api.crossref.org/works/", self.get_name_and_abstract)))
            task_marker += 1

            tasks.append(
                asyncio.create_task(self.fill_task(str(task_marker), occ_queue, "OpenCitations", "https://opencitations.net/index/api/v2/citations/doi:", self.add_related_paper_dois, "citing", self.oc_api_key)))
            task_marker += 1
            
            tasks.append(
                asyncio.create_task(self.fill_task(str(task_marker), ocr_queue, "OpenCitations", "https://opencitations.net/index/api/v2/references/doi:", self.add_related_paper_dois, "cited", self.oc_api_key)))
            task_marker += 1


        # Run the tasks
        with Timer(text="\nTotal elapsed time: {:.1f}"):

            await asyncio.gather(
                #I need to have a large number of these running or else missing data occurs
                *tasks
            )
        
        """
        Step 2
        """

        self.identify_common_dois()
        self.identify_important_papers()
        
        if len(self.recommendations) != 5:
            self.find_additional_papers()
        
        results_queue = asyncio.Queue()

        results = [Paper(doi=doi) for doi in self.recommendations]
        for paper in results:
            await results_queue.put(paper)
        
        #Add names and abstracts to the papers
        task_marker = 0
        tasks = []
        for _ in range(len(results)):
            tasks.append(
                asyncio.create_task(self.fill_task(str(task_marker), results_queue, "CrossRef", "https://api.crossref.org/works/", self.get_name_and_abstract)))
            task_marker += 1
        
        # Run the tasks
        with Timer(text="\nTotal elapsed time: {:.1f}"):

            await asyncio.gather(
                #I need to have a large number of these running or else missing data occurs
                *tasks
            )

        print(results)
        return results

    #------------------------------------------------------------------------
    #HELPER FUNCTIONS
    def get_name_and_abstract(self, js, paper: Paper, ignore=None):
        #The ignore param is only for the async function
        if 'title' in js["message"]:
            paper.name = js["message"]["title"]
            
        if 'abstract' in js["message"]:
            paper.abstract = js["message"]["abstract"]
    
    def add_related_paper_dois(self, js, paper: Paper, relation: str):
        #The "cited" and "citing" keys have a string with multiple ID types associated with it
        if relation == "cited":
            lst = paper.references
        elif relation == "citing":
            lst = paper.cited_by
        else:
            raise Exception("Unrecognized relationship")

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

    # with Timer(text="\nTotal elapsed time: {:.1f}"):
    #     papers = [
    #         Paper(doi= "10.1677/erc.1.0978"),
    #         Paper(doi="10.1016/j.gde.2006.12.005"),
    #         Paper(doi="10.1093/jnci/djg123"),
    #     ]
    #     gp = GroqProcesser(papers)
    #     print(gp.return_recommendations())

    papers = [
            Paper(doi= "10.1677/erc.1.0978"),
            Paper(doi="10.1016/j.gde.2006.12.005"),
            Paper(doi="10.1093/jnci/djg123"),]
    gp = GroqProcesser(papers)
    asyncio.run(gp.return_recommendations())
    print(gp.recommendations)
