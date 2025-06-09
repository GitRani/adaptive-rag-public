from pymilvus import MilvusClient
from sentence_transformers import SentenceTransformer

import pandas as pd
import logging
import os
import json

logger = logging.getLogger(__name__)

def milvus_db_connect():

    host = os.getenv("MILVUS_HOST")
    port = os.getenv("MILVUS_PORT")

    return MilvusClient(
        uri=f"http://{host}:{port}"
    )


def semantic_search(user_query, search_num):
    json_data = []
    collection_name = "tragfile0102"
    # 1. 텍스트를 벡터로 바꾸기
    model = SentenceTransformer("BAAI/bge-m3")
    query_vector = model.encode(user_query).tolist()

    # 2. milvus 연결
    milvus_client = milvus_db_connect()

    # 3. 벡터 검색
    results = milvus_client.search(
        collection_name=collection_name,
        data=[query_vector],
        anns_field="embed_vector",
        search_params={"metric_type": "COSINE", "params": {"nprobe": 10}},
        limit=search_num,
        output_fields=["id", "file_seq", "passage_seq", "file_name", "content", "page_no"]
    )

    logger.info(f'======== [Milvus] Results :: {results} ========')

    # 4. 검색 결과의 타입은 hit 객체여서 json으로 변환하는 작업이 필요하다. (hit는 dict와 같이 참조할 수 없으므로 아래와 같이 참조함)
    json_data = [
        {
            "id": data.id,
            "score": data.distance,
            "file_name": data.entity["file_name"],
            "content": data.entity["content"],
            "page_numbers": data.entity["page_no"],                
            "metadata": {
                "search_type": "vector",
                "file_seq": data.entity["file_seq"],
                "passage_seq": data.entity["passage_seq"],
                "regist_id": "unknown",
                "regist_dt": "",
                "modify_dt": ""
            }
        }
    for data in results[0]]

    return json_data

