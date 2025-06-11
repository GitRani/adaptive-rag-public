from fastapi import APIRouter
from fastapi.responses import JSONResponse

from schemas.fastapi_schema import HumanInfo, SearchInfo, ResponseModel
from graph.workflow import build_workflow
from utils.postgresql import keyword_search, postgre_db_connect, postgres_saver_setup
from utils.milvus import semantic_search
from utils.reranker import rerank_search

import uuid
import logging
import psycopg

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/generateGraph", tags=["GraphUnitTest"])
async def generate_graph(human_info: HumanInfo):
    logger.info(f'======== [API] INPUT :: {human_info} ========')
    try:
        conn = postgre_db_connect()
        logger.info("======== [API] PostgreSQL connection successful ========")

        checkpointer = postgres_saver_setup(conn)

        logger.info("======== [API] PostgreSQL saver setup successful ========")
        
        workflow = build_workflow(checkpointer=checkpointer)

        logger.info("======== [API] building workflow successful ========")

    except Exception as e:
        print(f"Connection failed: {e}")
        raise

    if human_info.memory:
        config = {"configurable": {"thread_id": "fixed-thread-id"}}
    else:
        config = {"configurable": {"thread_id": uuid.uuid4()}}
    
    # 중복된 부분 해소해야 됨. 소스코드 수정 많이 해야 되어서 일단 내버려 둠.
    initial_input = {
        "question": human_info.query, 
        "search_num": human_info.retrieve_search_cnt,
        "human_info": {
            "query": human_info.query,
            "retrieve_limit_cnt": human_info.retrieve_limit_cnt,
            "retrieve_search_cnt": human_info.retrieve_search_cnt,
            "memory": True
         }
    }

    graph_result = workflow.invoke(initial_input, config=config)
    
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
    
    hybrid_search_len = len(keyword_json) + len(semantic_json)
    
    if hybrid_search_len == 0:
        return ResponseModel(success="N", message="검색 결과가 없습니다.", data=[])
    else:
        logger.info(f'======== [API] SEARCH NUM :: {hybrid_search_len} ========')
        return ResponseModel(success="Y", message="하이브리드 검색을 완료했습니다.", version="1.0", data=rerank_search(query, keyword_json, semantic_json, search_num))





    
    
