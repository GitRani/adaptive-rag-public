import os
import psycopg2
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def postgre_db_connect():

    logger.info(os.getenv("POSTGRE_HOST"))    

    return psycopg2.connect(
        dbname=os.getenv("POSTGRE_NAME"),
        user=os.getenv("POSTGRE_USER"),
        host=os.getenv("POSTGRE_HOST"),
        port=os.getenv("POSTGRE_PORT"),
        password=os.getenv("POSTGRE_PASSWORD")
    )


def query_execute(conn, sql, data_tuple):
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, data_tuple)
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
        return result, columns
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        return None, None


def keyword_refinement(keyword_info):
    keyword_list = keyword_info.split(':')
    keyword_list = [keyword.split()[-1] for keyword in keyword_list][:-1]
    keyword_list = [keyword.replace("'", "") for keyword in keyword_list]
    return '&'.join([keyword for keyword in keyword_list if len(keyword) >= 2])


def keyword_search(user_query):
    get_keyword_sql = "SELECT to_tsvector('simple', %s);"
    # detail query
    # search_tsvector_sql = '''
    # SELECT TF0.FILE_NM, TF2.cont, TF2.cont_tsvector, ts_rank(cont_tsvector, to_tsquery('korean', %s)) AS rank
    # FROM TRAGFILE0102 TF2
    # INNER JOIN TRAGFILE0100 TF0
    # ON TF0.FILE_SEQ = TF2.FILE_SEQ
    # WHERE cont_tsvector @@ to_tsquery('korean', %s);
    # '''

    # simple query
    search_tsvector_sql = '''
    SELECT cont_tsvector, ts_rank(cont_tsvector, to_tsquery('simple', %s)) AS rank
    FROM TRAGFILE0102
    WHERE cont_tsvector @@ to_tsquery('simple', %s);
    '''

    conn = postgre_db_connect()
    try:
        keyword_info, _ = query_execute(conn, get_keyword_sql, (user_query,))
        if not keyword_info:
            print("No keyword info found.")
            return None

        keyword_info = keyword_info[0][0]
        keyword_condition = keyword_refinement(keyword_info)
        print('==== condition ==== :: ', keyword_condition)

        result, columns = query_execute(conn, search_tsvector_sql, (keyword_condition, keyword_condition,))
        if result is None:
            print("No search result found.")
            return None

        return pd.DataFrame(result, columns=columns)
    finally:
        conn.close()
        print('DB 연결 종료!')
