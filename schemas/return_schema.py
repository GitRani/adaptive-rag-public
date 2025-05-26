# 라우팅 관련 스키마는 정해진 결과 값을 명확히 제공해야 하기 때문에 스키마를 구현한다.
from pydantic import BaseModel, Field
from typing import Literal

class RouteQuery(BaseModel):
    '''질문을 보고 가장 적합한 노드로 이동시킵니다.'''

    next_node: Literal["search", "vector", "generate"] = Field(
        description="web_search/retrieve/generate 노드로 갈 지 질문을 보고 선택합니다."
    )

class GradeDocuments(BaseModel):
    '''검색된 문서가 질문으로 해결 가능한 내용인지에 대한 여부를 판단합니다.'''

    pass_yn: Literal["Y", "N"] = Field(
        description="문서가 질문으로 해결 가능한 내용인지에 따라 'Y' 또는 'N' 로 답합니다."
    )

class GradeHallucinations(BaseModel):
    '''생성된 답변이 hallucination 현상이 있는지에 대한 여부를 판단합니다. '''

    pass_yn: Literal["Y", "N"] = Field(
        description="생성된 답변이 사실인지에 따라 'Y' 또는 'N' 로 답합니다."
    )

class GradeQuestionAnswer(BaseModel):
    '''생성된 답변이 질문과 관련이 있는지에 대한 여부를 판단합니다.'''

    pass_yn: Literal["Y", "N"] = Field(
        description="답변이 질문을 해결할 수 있는 지에 따라 'Y' 또는 'N' 로 답합니다."
    )

