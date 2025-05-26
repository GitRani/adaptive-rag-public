from schemas.return_schema import (
    RouteQuery, 
    GradeDocuments,
    GradeHallucinations, 
    GradeQuestionAnswer    
)
from config.model_config import Claude

from langchain_core.prompts import ChatPromptTemplate, load_prompt
from langchain_core.output_parsers import StrOutputParser
from pathlib import Path

# (EDGE) start 분기 부분 : 생성형 판단
def vector_websearch_chain():
    vector_websearch_prompt = load_prompt(Path(__file__).parent.parent / 'config/prompts/rag-route-vector-websearch-prompt.yaml')

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", vector_websearch_prompt.template),
            ("human", "{question}")
        ]
    )
    structed_llm = Claude(schema=RouteQuery).get_structed_model()
    
    return prompt | structed_llm


# (NODE) generate 노드 : 생성형 문구 생성
def generate_chain():
    prompt = load_prompt(Path(__file__).parent.parent / 'config/prompts/rag-generate-prompt.yaml')

    llm = Claude().get_model()

    return prompt | llm | StrOutputParser()


# (EDGE) generate 분기 : 생성형 판단
def grade_hallucination_chain():
    hallucination_check_prompt = load_prompt(Path(__file__).parent.parent / 'config/prompts/rag-route-grade-hallucination-prompt.yaml')

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", hallucination_check_prompt.template),
            ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation}")
        ]
    )
    structed_llm = Claude(schema=GradeHallucinations).get_structed_model()

    return prompt | structed_llm


# (EDGE) generate 분기 : 생성형 판단
def grade_answer_chain():
    grade_answer_prompt = load_prompt(Path(__file__).parent.parent / 'config/prompts/rag-route-grade-answer.yaml')

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", grade_answer_prompt.template),
            ("human", "User question: \n\n {question} \n\n LLM generation: {generation}")
        ]
    )
    structed_llm = Claude(schema=GradeQuestionAnswer).get_structed_model()

    return prompt | structed_llm


# (NODE) transform_query 노드 : 생성형 문구 생성
def rewrite_query_chain():
    rewrite_query_prompt = load_prompt(Path(__file__).parent.parent / 'config/prompts/rag-rewrite-query-prompt.yaml')

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", rewrite_query_prompt.template),
            ("human", "{question}")
        ]
    )
    llm = Claude().get_model()

    return prompt | llm


# (NODE) grade_documents 분기 : 생성형 판단
def grade_documents_chain():
    grade_documents_prompt = load_prompt(Path(__file__).parent.parent / 'config/prompts/rag-route-grade-documents-prompt.yaml')

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", grade_documents_prompt.template),
            ("human", "Retrieved document: \n\n {document} \n\n User question: {question}")
        ]
    )
    structed_llm = Claude(schema=GradeDocuments).get_structed_model()

    return prompt | structed_llm



