from fastapi import APIRouter
from schemas.fastapi_schema import HumanInfo
from graph.workflow import build_workflow
from utils.postgresql import keyword_search
from fastapi.responses import JSONResponse
from utils.milvus import *

import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/generateGraph")
async def generate_graph(human_info: HumanInfo):
    logger.info(f'======== [API] INPUT :: {human_info} ========')

    workflow = build_workflow()
    config = {"configurable": {"thread_id": uuid.uuid4()}}
    initial_input = {"question": human_info.query}
    graph_result = workflow.invoke(initial_input)

    logger.info(f'======== [API] GRAPH RESULT :: \n {graph_result} ========')

    return graph_result


@router.post("/postgreInsert")
async def postgre_db_insert(file_path):
    logger.info(f'======== [API] INPUT :: {file_path} ========')
    ''


@router.post("/keywordSearch")
async def postgre_db_search(user_query):
    logger.info(f'======== [API] INPUT :: {user_query} ========')
    return keyword_search(user_query)

@router.post("/semanticSearch")
async def milvus_db_search(user_query):
    logger.info(f'======== [API] INPUT :: {user_query} ========')
    mc = milvus_db_connect()
    print(mc)
    return "1"


