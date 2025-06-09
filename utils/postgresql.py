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

        return result
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        return None, None


def keyword_refinement(keyword_info):
    keyword_list = keyword_info.split(':')
    keyword_list = [keyword.split()[-1] for keyword in keyword_list][:-1]
    keyword_list = [keyword.replace("'", "") for keyword in keyword_list]
    return '&'.join([keyword for keyword in keyword_list if len(keyword) >= 2])


def keyword_search(user_query, search_num):
    get_keyword_sql = "SELECT to_tsvector('simple', %s);"

    search_tsvector_sql = '''
    SELECT TR02.id, TR00.file_seq, TR02.passage_seq, file_nm, cont, page_no_chst, ts_rank(cont_tsvector, to_tsquery('simple', %s)) AS rank
    FROM TRAGFILE0100 TR00
    INNER JOIN TRAGFILE0102 TR02 
    ON TR00.file_seq = TR02.file_seq
    WHERE cont_tsvector @@ to_tsquery('simple', %s)
    LIMIT %s;

    '''

    conn = postgre_db_connect()
    try:
        keyword_info = query_execute(conn, get_keyword_sql, (user_query,))
        if not keyword_info:
            print("No keyword info found.")
            return None

        keyword_info = keyword_info[0][0]
        keyword_condition = keyword_refinement(keyword_info)
        print('==== condition ==== :: ', keyword_condition)


        
        result = query_execute(conn, search_tsvector_sql, (keyword_condition, keyword_condition, search_num))

        logger.info(f'======== [Postgres] Results :: {result} ========')
        
        json_data = [
            {
                "id": data[0],
                "score": data[6],
                "file_name": data[3],
                "content": data[4],
                "page_numbers": data[5],                
                "metadata": {
                    "search_type": "keyword",
                    "file_seq": data[1],
                    "passage_seq": data[2],
                    "regist_id": "unknown",
                    "regist_dt": "",
                    "modify_dt": ""
                }
            } 
        for data in result]

        if result is None:
            print("No search result found.")
            return None
        
        return json_data

    finally:
        conn.close()
        print('DB 연결 종료!')
