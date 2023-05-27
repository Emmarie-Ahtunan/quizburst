from pydantic import BaseModel

class quiz(BaseModel):
    topic:str
    id:int
    question:str
    ans:str=""
    done:bool