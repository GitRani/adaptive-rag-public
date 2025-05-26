# Adaptive RAG 실습

## 개요
이 프로젝트는 Adaptive RAG(Retrieval-Augmented Generation) 구현을 위한 실습 프로젝트입니다. 
다양한 기술 스택을 활용하여 워크플로우를 구성하며, LangGraph를 중심으로 RAG 체인을 구현합니다.

- **참고 코드**: [LangChain-KR Adaptive RAG](https://github.com/teddylee777/langchain-kr/blob/main/17-LangGraph/02-Structures/07-LangGraph-Adaptive-RAG.ipynb)
- **사용 기술**:
  - FastAPI
  - LangGraph
  - LangSmith
  - LangChain
  - Milvus (예정)
  - Docker (예정)

## 필자가 진행/생각한 구축 순서 (정답은 아님..)

- langgraph 초안을 그려놓는다.
- 어떤 값이 들어오고 나가는지 정의
(클래스명이나 데이터 변수를 정의해야 할 듯.)

- 기본적인 상태 스키마 정의 + 다른 리턴 타입 스키마 정의 + FastAPI 쓰는 경우 스키마 정의
* 교착 상태에 빠지지 않도록 제어하는 상태도 필요할 것으로 보임.
 예시) 웹검색과 리트리버 검색이 그래프에 있을 때 
 리트리버에 관련없는 질문 시 / 웹검색 결과는 리트리버 검색에 없는 내용일 것이므로 / 리트리버에서 잘못된 결과를 반환하고 / 관련없음 체크 시 다시 리트리버 / 무한루프

 - node, edges, workflow 기본 껍데기는 만들어 놓기. 일단 안에는 빈 깡통 상태로!
 - 체인 별 필요한 프롬포트 작성해서 prompts 밑에 yaml로 구성하기
 
- 벡터 DB 로직 만들기

- 생성형을 사용하는 체인 만들기
 → chain 별 단위 테스트 필요

**체인을 노드 전용 / 엣지 전용 체크해놓으면 좋음

- 노드에 로직 구현
- 엣지에 로직 구현

- 로그 붙이기

- LangGraph 통합 테스트 (단위 테스트가 완료되었다는 가정 하에 진행 / LangGraph Studio 이용)
- LangGraph 모듈 -> FastAPI -> Docker 확장....


## 디렉토리 구조 (2025.05.26 기준)
```plaintext
adaptive-rag-public/
│
├── routers/                   # FastAPI
│   ├── api.py
│
├── chains/                   # 체인 관련 로직 (재사용 가능한 체인 정의)
│   ├── __init__.py
│   ├── rag_chain.py          # RAG 체인
│
├── tools/                    # 외부 도구 관련 (Tavily 등)
│   ├── __init__.py
│   ├── web_search.py         # 웹 검색 도구 (Tavily 기반)
│
├── vectorstore/              # 벡터 DB 관련 (임베딩 및 검색)
│   ├── __init__.py
│   ├── pdf.py                # PDF -> 텍스트 변환 및 임베딩
│
├── graph/                    # LangGraph 워크플로우 정의
│   ├── __init__.py
│   ├── nodes.py              # 노드 정의 (web_search, generate, transform_query 등)
│   ├── edges.py              # 조건부 라우팅 로직 (add_conditional, 라우팅 함수)
│   ├── checkpointer.py       # 메모리 정의 (PostgreSaver, SqliteSaver)
│   ├── workflow.py           # 전체 워크플로우 구성
│
├── schemas/                  # 데이터 스키마 정의 (입력/출력 형식)
│   ├── __init__.py
│   ├── fastapi_schema.py     # FastAPI 결과 스키마
│   ├── web_search_schema.py  # 웹 검색 결과 스키마
│   ├── state_schema.py       # 그래프 상태 스키마
│   ├── return_value_schema.py # 각 노드의 반환 값 스키마
│
├── unit_test/                # Jupyter Notebook Unit Test
│   ├── test.ipynb
│
├── utils/                    # 유틸리티 및 로깅
│   ├── logger               # 로깅 파일
│   ├── utils.py             # 로직 파일
│
├── configs/                  # 설정 파일 (모델, 프롬프트 등)
│   ├── __init__.py
│   ├── prompt               # 프롬프트 yaml 파일들
│   ├── model_config.py      # 모델 초기화 설정
│
├── langgraph.json            # LangGraph Server 실행 정보 (Dependency 등)
├── main.py                   # 워크플로우 실행 진입점
└── requirements.txt          # 필요한 패키지 목록



3.
To-do
- FAISS -> Milvus 변경
- Dockerizing (Dockefile, docker-compose)
- batch structure
- postgresaver
- managing message stack (improving state schema)
- infinite loop remove



4.
Execute Server Info
- langgraph dev (langgraph.json 위치에서 실행)
- uvicorn main:app --reload (main.py 위치에서 실행)


