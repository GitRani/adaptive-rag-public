from fastapi import APIRouter
from schemas.fastapi_schema import HumanInfo
from graph.workflow import build_workflow

import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/generate")
async def generate_graph(human_info: HumanInfo):
    logger.info(f'======== [API] INPUT :: {human_info} ========')

    workflow = build_workflow()
    config = {"configurable": {"thread_id": uuid.uuid4()}}
    initial_input = {"question": human_info.query}
    graph_result = workflow.invoke(initial_input)

    logger.info(f'======== [API] GRAPH RESULT :: \n {graph_result} ========')

    return graph_result