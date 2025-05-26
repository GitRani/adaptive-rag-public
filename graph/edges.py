# 라우팅 로직 함수 정의
from schemas.state_schema import AgentState
from chains.rag_chain import (
    vector_websearch_chain,
    grade_hallucination_chain,
    grade_answer_chain
)
import logging

logger = logging.getLogger(__name__)

def route_vector_or_websearch(state: AgentState):
    '''vector로 갈 지, web search로 갈 지 결정하는 edge'''
    logger.info('======== [EDGE] ROUTE_VECTOR_OR_WEBSEARCH ========')
    question = state['question']
    decision = vector_websearch_chain().invoke({"question": question}).next_node

    if decision == 'search':
        logger.info('======== [ROUTE] SEARCH ========')
        return 'search'
    elif decision == "vector":
        logger.info('======== [ROUTE] VECTOR ========')
        return 'vector'
    else:
        logger.info('======== [ROUTE] GENERATE ========')
        return 'generate'


def route_hallucination_check(state: AgentState):
    '''Hallucination 여부 및 Question과의 relevance 여부를 체크한다.'''
    logger.info('======== [EDGE] ROUTE_HALLUCINATION_CHECK ========')
    question = state['question']
    generation = state['generate_message']
    documents = state['documents']

    first_decision = grade_hallucination_chain().invoke({"documents": documents, "generation": generation}).pass_yn
    logger.info(f'======== [LOG] FIRST DECISION :: {first_decision} ========') 

    if first_decision == 'Y':
        second_decision = grade_answer_chain().invoke({"question": question, "generation": generation}).pass_yn
        logger.info(f'======== [LOG] SECOND DECISION :: {second_decision} ========')   

        if second_decision == 'Y':
            logger.info('======== [ROUTE] RELEVANT ========')
            return "relevant"
        else:
            logger.info('======== [ROUTE] IRRELEVANT ========')
            return "irrelevant"
    else:
        logger.info('======== [ROUTE] HALLUCINATION ========')
        return "hallucination"


def route_generate_by_relevance(state: AgentState):
    logger.info('======== [EDGE] ROUTE_GENERATE_BY_RELEVANCE ========')
    documents = state['documents']
    logger.info(f'======== [LOG] LENGTH OF DOCUMENTS :: {len(documents)} ========')

    if len(documents) == 0:
        logger.info('======== [ROUTE] IRRELEVANT ========')
        return "irrelevant"
    else:
        logger.info('======== [ROUTE] RELEVANT ========')
        return "relevant"
