# 노드 관련 함수 정의
from langchain_core.documents import Document
from langchain_core.messages import AIMessage
from schemas.state_schema import AgentState
from schemas.fastapi_schema import HumanInfo
from tools.search import tavily_search
from chains.rag_chain import (
    generate_chain,
    rewrite_query_chain,
    grade_documents_chain
)
from utils.postgresql import keyword_search
from utils.milvus import semantic_search
from utils.reranker import rerank_search

from vectorstore.pdf import PDFRetrievalChain
from pathlib import Path

import os
import logging
import re

logger = logging.getLogger(__name__)

def web_search(human_info: HumanInfo, state: AgentState):
    '''웹 검색을 반환하는 노드'''
    logger.info('======== [NODE] WEB_SEARCH ========')
    web_search_results = tavily_search(max_results=human_info.retrieve_search_cnt).invoke(state['question'])

    document_list = [
        Document(
            page_content=result["content"],
            metadata={
                "source": result["url"]
            }
        )
        for result in web_search_results
    ]
    return {"documents": document_list}


def generate(state: AgentState):
    '''답변을 생성하는 노드'''
    logger.info('======== [NODE] GENERATE ========')
    logger.info(state)
    question = state['question']
    documents = state.get('documents', '')

    generation = generate_chain().invoke({"question": question, "context": documents})

    # deepseek 전처리
    generation = re.sub(r"<think>.*?</think>", "", generation, flags=re.DOTALL).strip()

    logger.info(f'======== [NODE] GENERATION :: {generation} ========')
    
    return {
        "generate_message": generation,
        "messages": AIMessage(content=generation),
        "documents": documents if documents != '' else ''
    }


def transform_query(state: AgentState):
    '''Question을 다시 작성하는 노드'''
    logger.info('======== [NODE] TRANSFORM QUERY ========')
    question = state['question']

    improv_question = rewrite_query_chain().invoke({"question": question})

    logger.info(f'======== [NODE] IMPROVED QUERY :: {improv_question}========')

    return {"question": improv_question}


def retrieve(state: AgentState):
    '''Retrieve한 Document를 반환하는 노드'''
    logger.info('======== [NODE] RETRIEVE ========')
    question = state['question']
    pdf_path = os.path.join(Path(__file__).parent.parent, "data", "pdf", "지방자치단체 산안법 적용 (산재예방정책과-3018 (2018.07.06. 시행).pdf")

    # (예외처리) AIMessage 객체면, 그 안의 필드로 들어가 있을 것이므로, content를 참조하게끔 한다.
    if isinstance(question, AIMessage):
        question = question.content

    logger.info(f'======== [NODE][RETRIEVE] Question: {question} ========')

    # PDFRetrieval 사용 시 해제 (지금은 쓰지 않음)
    # pdf_retriever = PDFRetrievalChain(search_num=5, source_uris=[pdf_path]).create_chain()
    # documents = pdf_retriever.invoke(question)

    keyword_json = keyword_search(question, search_num=3)
    semantic_json = semantic_search(question, search_num=3)

    hybrid_search_len = len(keyword_json) + len(semantic_json)
    
    if hybrid_search_len == 0:
        return {"documents": []}
    else:
        logger.info(f'======== [API] SEARCH NUM :: {hybrid_search_len} ========')

        results = rerank_search(question, keyword_json, semantic_json, search_num=3)

        document_list = [
            Document(
                page_content=result["content"],
                metadata={
                    "file_name": result["file_name"],
                    "page_numbers": result["page_numbers"]
                }
            )
            for result in results
        ]

        logger.info(f'====== [DOCUMENTS]{document_list} ========')

        return {"documents": document_list}


def grade_documents(state: AgentState):
    '''Retrieve된 Document 중 관련 있는 Document만 필터링하는 노드'''
    logger.info('======== [NODE] GRADE DOCUMENTS ========')
    question = state['question']
    documents = state['documents']
    filtered_docs = []

    for doc in documents[:5]:
        decision = grade_documents_chain().invoke({"question": question, "document": doc}).pass_yn

        if decision == "Y":
            logger.info('======== [NODE:CHECK] RELEVANT DOCUMENT ========')
            logger.info(doc)
            filtered_docs.append(doc)
        else:
            logger.info('======== [NODE:CHECK] IRRELEVANT DOCUMENT ========')
            logger.info(doc)

    return {"documents": filtered_docs}