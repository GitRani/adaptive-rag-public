from typing import TypedDict, Annotated, List
from langgraph.graph.message import add_messages

from schemas.fastapi_schema import HumanInfo

class AgentState(TypedDict):
    question: Annotated[str, "question"]
    generate_message: Annotated[str, "llm generated answer"]
    documents: Annotated[List[str], "context"]
    # messages 값 추가 (아직 미구현)
    messages: Annotated[List, add_messages]
    # 무한루프 방지용 상태값 설정 (아직 미구현)
    limit: int
    human_info: HumanInfo
    