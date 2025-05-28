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

from vectorstore.pdf import PDFRetrievalChain
from pathlib import Path

import os
import logging

logger = logging.getLogger(__name__)

def web_search(human_info: HumanInfo, state: AgentState):
    '''웹 검색을 반환하는 노드'''
    logger.info('======== [NODE] WEB_SEARCH ========')
    web_search_results = tavily_search(max_results=human_info.retrieve_cnt).invoke(state['question'])

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

    return {"question": improv_question}


def retrieve(state: AgentState):
    '''Retrieve한 Document를 반환하는 노드'''
    logger.info('======== [NODE] RETRIEVE ========')
    question = state['question']
    pdf_path = os.path.join(Path(__file__).parent.parent, "data", "pdf", "지방자치단체 산안법 적용 (산재예방정책과-3018 (2018.07.06. 시행).pdf")

    if isinstance(question, AIMessage):
        question = question.content

    logger.info(f'======== [NODE][RETRIEVE] Question: {question} ========')

    pdf_retriever = PDFRetrievalChain(search_num=5, source_uris=[pdf_path]).create_chain()
    documents = pdf_retriever.invoke(question)

    # log 확인
    for idx, doc in enumerate(documents):
        logger.info(f'[{idx} content] :: {doc}')
        logger.info('++++++++++++++++++++++++++++++')

    return {"documents": documents}


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