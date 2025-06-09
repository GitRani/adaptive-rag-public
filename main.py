from utils.logger.logger import setup_logging
from graph.checkpointer import get_checkpointer_sqlite, get_checkpointer_postgre
from graph.workflow import build_workflow
from routers import api

from fastapi import FastAPI, Response
from fastapi.responses import RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html

from dotenv import load_dotenv
from pathlib import Path


import uvicorn
import logging
import os
import uuid


load_dotenv()

logging.getLogger("pdfminer").setLevel(logging.WARNING)

LOG_PATH = os.getenv('LOG_PATH')
LOG_MAX_BYTES = os.getenv('LOG_MAX_BYTES')
LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT'))
LOG_INTERVAL = int(os.getenv('LOG_INTERVAL'))
LOG_WHEN = os.getenv('LOG_WHEN')
LOG_LEVEL = os.getenv('LOG_LEVEL')

setup_logging(
    log_path = LOG_PATH,
    log_max_bytes = LOG_MAX_BYTES,
    log_backup_count = LOG_BACKUP_COUNT,
    log_when = LOG_WHEN,
    interval = LOG_INTERVAL,
    log_level = LOG_LEVEL,
    debug = False
)

logger = logging.getLogger(__name__)

# langgraph.json 있는 위치에서 langgraph dev 시, 서버 실행됨.
# 추가) langgraph dev는 PostgresSaver를 지원한다고 함. SqliteSaver 쓰지 말자...

graph = build_workflow()

# # -------------- 실행 --------------
# if __name__ == "__main__":
#     # 체크포인터 나중에 설정 예정
#     # config = {"configurable": {"thread_id": uuid.uuid4()}}
#     initial_input = {"question": '''현업의 업종을 판단할 때 공무직 및 공공근로 등 단기간 근로자를 포함하여 채용인원이 가장 많은 상위 2~3개 부서의 현업업무의 업종을 주된 업종으로 판단하여 산업안전보건법을 적용 가능한지?'''}  

#     logger.info("워크플로우 실행 시작")
#     result = app.invoke(initial_input)
#     # state = app.get_state()

app = FastAPI(docs_url=None)
app.include_router(api.router, prefix='/api')

@app.get("/")
async def main():
    return RedirectResponse('/docs')


@app.get('/swagger_css')
def swagger_css():    
    with open(Path(Path(__file__).parent / "templates" / "swagger" / "swagger-ui.css"),'rt',encoding='utf-8') as f:        
        swagger_css = f.read()    
    return Response(swagger_css,headers={"Content-type":"text/css"})


@app.get('/swagger_js')
def swagger_js():   
    with open(Path(Path(__file__).parent / "templates" / "swagger" /"swagger-ui-bundle.js"),'rt',encoding='utf-8') as f:        
        swagger_js = f.read()    
    return Response(swagger_js,headers={"Content-type":"text/javascript"})


@app.get("/docs")
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Rani's Swagger",
        swagger_js_url="/swagger_js",
        swagger_css_url="/swagger_css"
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)