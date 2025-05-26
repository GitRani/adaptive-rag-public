from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

# sqlitesaver 쓰는 방법 (근데 langgraph dev 에서 못씀)
def get_checkpointer_sqlite(db_path):
    """체크포인터 초기화 함수"""
    # SqliteSaver를 직접 초기화
    conn = sqlite3.connect(db_path, check_same_thread=False)
    saver = SqliteSaver(conn)
    return saver

# postgre 쓰는 방법 (향후 붙일 예정)
def get_checkpointer_postgre(db_path):
    ''