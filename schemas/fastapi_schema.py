from pydantic import BaseModel
from typing import List, Any, Optional

class HumanInfo(BaseModel):
    query: str
    retrieve_cnt: int

class SearchInfo(BaseModel):
    query: str
    search_num: int

class ResponseModel(BaseModel):
    success: bool
    message: str
    version: Optional[str] = None
    data: Any = None
