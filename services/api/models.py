from pydantic import BaseModel
from typing import List
#------------------------------------------------------------------------
'''
  _____   _____   _   _  _ _____ ___ ___   __  __  ___  ___  ___ _    ___ 
 | _ \ \ / /   \ /_\ | \| |_   _|_ _/ __| |  \/  |/ _ \|   \| __| |  / __|
 |  _/\ V /| |) / _ \| .` | | |  | | (__  | |\/| | (_) | |) | _|| |__\__ \
 |_|   |_| |___/_/ \_\_|\_| |_| |___\___| |_|  |_|\___/|___/|___|____|___/
'''
class Paper(BaseModel):
    id: int = None
    doi: str
    name: str = None
    abstract: str = None
    references: List[str] = [] #list of DOIs
    cited_by: List[str] = []

class Papers(BaseModel):
    papers: List[Paper]

