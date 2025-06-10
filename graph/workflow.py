# nodes와 edges를 기반으로 workflow 정의
# memorysaver를 db 관리화 한다면 기능 이전 필요
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from schemas.state_schema import AgentState

from graph.edges import (
    route_vector_or_websearch, 
    route_hallucination_check,
    route_generate_by_relevance
)

from graph.nodes import (
    web_search,
    generate,
    transform_query,
    retrieve,
    grade_documents
)
import logging

logger = logging.getLogger(__name__)

# 나중에 memorysaver postgre 용 추가 예정
def build_workflow(checkpointer):
    workflow = StateGraph(AgentState)

    workflow.add_node("web_search", web_search)
    workflow.add_node("generate", generate)
    workflow.add_node("transform_query", transform_query)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("grade_documents", grade_documents)

    workflow.add_edge("web_search", "generate")
    workflow.add_edge("transform_query", "retrieve")
    workflow.add_edge("retrieve", "grade_documents")

    workflow.add_conditional_edges(
        START,
        route_vector_or_websearch,
        {
        "search": "web_search",
        "vector": "retrieve",
        "generate": "generate"
        }
    )
    workflow.add_conditional_edges(
        "generate",
        route_hallucination_check,
        {
        "hallucination": "generate",
        "relevant": END,
        "irrelevant": "transform_query"
        }
    )
    workflow.add_conditional_edges(
        "grade_documents",
        route_generate_by_relevance,
        {
        "relevant": "generate",
        "irrelevant": "transform_query"
        }
    )

    # return workflow.compile(checkpointer=memory)
    if checkpointer == '':
        return workflow.compile()
    else:
        return workflow.compile(checkpointer=checkpointer)



