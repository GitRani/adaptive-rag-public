Adaptive RAG 실습

1.
- basic code ref : https://github.com/teddylee777/langchain-kr/blob/main/17-LangGraph/02-Structures/07-LangGraph-Adaptive-RAG.ipynb
- FastAPI / LangGraph / LangSmith / LangChain / Milvus(예정) / Docker(예정) 등... 


2. (25.05.26 기준 디렉토리 정보)
adaptive-rag-public/ 
│
├── chains/                   # 체인 관련 로직 (재사용 가능한 체인 정의)
│   ├── __init__.py
│   ├── rag_chain.py          # RAG 체인
│
├── tools/                    # 외부 도구 관련 (Tavily 등)
│   ├── __init__.py
│   └── web_search.py         # 웹 검색 도구 (Tavily 기반)
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
│   └── workflow.py           # 전체 워크플로우 구성
│
├── schemas/                  # 데이터 스키마 정의 (입력/출력 형식)
│   ├── __init__.py
│   ├── fastapi_schema.py     # fastapi 결과 스키마
│   ├── web_search_schema.py  # 웹 검색 결과 스키마
│   ├── state_schema.py       # 그래프 상태 스키마
│   └── return_value_schema.py # 각 노드의 반환 값 스키마
│
├── unit_test/                  # Jupyter Notebook Unit Test 
│   ├── test.ipynb
│
├── utils/                    # Jupyter Notebook Unit Test 
│   ├── logger                # 로깅 파일
│   └── utils.py               # 로직 파일
│
│
├── configs/                  # 설정 파일 (모델, 프롬프트 등)
│   ├── __init__.py
│   ├── prompt                # 프롬포트 yaml 파일들
│   └── model_config.py       # 모델 초기화 설정
│
│── langgraph.json            # LangGraph Server 실행 정보(Dependency 등)
├── main.py                   # 워크플로우 실행 진입점
└── requirements.txt          # 필요한 패키지 목록



3.
To-do
- FAISS -> Milvus 변경
- Dockerizing
- batch structure
- postgresaver


4.
Execute Server Info
- langgraph dev (langgraph.json 위치에서 실행)
- uvicorn main:app --reload (main.py 위치에서 실행)