from fastapi import APIRouter
from fastapi.responses import JSONResponse

from schemas.fastapi_schema import HumanInfo, SearchInfo, ResponseModel
from graph.workflow import build_workflow
from utils.postgresql import keyword_search
from utils.milvus import semantic_search

import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/generateGraph", tags=["GraphUnitTest"])
async def generate_graph(human_info: HumanInfo):
    logger.info(f'======== [API] INPUT :: {human_info} ========')

    workflow = build_workflow()
    config = {"configurable": {"thread_id": uuid.uuid4()}}
    initial_input = {"question": human_info.query}
    graph_result = workflow.invoke(initial_input)

    logger.info(f'======== [API] GRAPH RESULT :: \n {graph_result} ========')

    return ResponseModel(success=True, message="그래프를 성공적으로 실행했습니다", version="1.0", data=graph_result)


@router.post("/postgreInsert", tags=["DBUnitTest"])
async def postgre_db_insert(file_path):
    logger.info(f'======== [API] INPUT :: {file_path} ========')
    ''


@router.post("/keywordSearch", tags=["DBUnitTest"])
async def postgre_db_search(search_info: SearchInfo):
    query = search_info.query
    search_num = search_info.search_num

    return ResponseModel(success="Y", message="키워드 검색을 완료했습니다.", version="1.0", data=keyword_search(query, search_num))


@router.post("/semanticSearch", tags=["DBUnitTest"])
async def milvus_db_search(search_info: SearchInfo):
    query = search_info.query
    search_num = search_info.search_num
    
    return ResponseModel(success="Y", message="벡터 검색을 완료했습니다.", version="1.0", data=semantic_search(query, search_num))


@router.post("/hybridSearch", tags=["DBUnitTest"])
async def hybrid_db_search(search_info: SearchInfo):
    query = search_info.query
    search_num = search_info.search_num

    keyword_json = keyword_search(query, search_num)
    semantic_json = semantic_search(query, search_num)
    
    if len(keyword_json) + len(semantic_json) == 0:
        return ResponseModel(success="N", message="검색 결과가 없습니다.")
    else:
        json_data = {
            
        }





    
    
