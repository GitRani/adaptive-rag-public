from pydantic import BaseModel

class HumanInfo(BaseModel):
    query: str
    retrieve_cnt: int