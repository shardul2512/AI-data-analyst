from typing import List
from haystack import component
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
import sqlite3
import psycopg2
from utils import TEMP_DIR

@component
class SQLiteQuery:

    def __init__(self, sql_database: str):
      self.connection = sqlite3.connect(sql_database, check_same_thread=False)

    @component.output_types(results=List[str], queries=List[str])
    def run(self, queries: List[str], session_hash):
        print("ATTEMPTING TO RUN SQLITE QUERY")
        dir_path = TEMP_DIR / str(session_hash)
        results = []
        for query in queries:
          result = pd.read_sql(query, self.connection)
          result.to_csv(f'{dir_path}/file_upload/query.csv', index=False)
          results.append(f"{result}")
        self.connection.close()
        return {"results": results, "queries": queries}
    


def sqlite_query_func(queries: List[str], session_hash, **kwargs):
    dir_path = TEMP_DIR / str(session_hash)
    sql_query = SQLiteQuery(f'{dir_path}/file_upload/data_source.db')
    try:
      result = sql_query.run(queries, session_hash)
      if len(result["results"][0]) > 1000:
        print("QUERY TOO LARGE")
        return {"reply": "query result too large to be processed by llm, the query results are in our query.csv file. If you need to display the results directly, perhaps use the table_generation_func function."}
      else:   
        return {"reply": result["results"][0]}

    except Exception as e:
      reply = f"""There was an error running the SQL Query = {queries}
              The error is {e},
              You should probably try again.
              """
      return {"reply": reply}
    
@component
class PostgreSQLQuery:

    def __init__(self, url: str, sql_port: int, sql_user: str, sql_pass: str, sql_db_name: str):
      self.connection = psycopg2.connect(
            database=sql_db_name,
            user=sql_user,
            password=sql_pass,
            host=url,  # e.g., "localhost" or an IP address
            port=sql_port  # default is 5432
        )

    @component.output_types(results=List[str], queries=List[str])
    def run(self, queries: List[str], session_hash):
        print("ATTEMPTING TO RUN POSTGRESQL QUERY")
        dir_path = TEMP_DIR / str(session_hash)
        results = []
        for query in queries:
          print(query)
          result = pd.read_sql_query(query, self.connection)
          result.to_csv(f'{dir_path}/sql/query.csv', index=False)
          results.append(f"{result}")
        self.connection.close()
        return {"results": results, "queries": queries}
    


def sql_query_func(queries: List[str], session_hash, db_url, db_port, db_user, db_pass, db_name, **kwargs):
    sql_query = PostgreSQLQuery(db_url, db_port, db_user, db_pass, db_name)
    try:
      result = sql_query.run(queries, session_hash)
      print("RESULT")
      print(result)
      if len(result["results"][0]) > 1000:
        print("QUERY TOO LARGE")
        return {"reply": "query result too large to be processed by llm, the query results are in our query.csv file. If you need to display the results directly, perhaps use the table_generation_func function."}
      else:   
        return {"reply": result["results"][0]}

    except Exception as e:
      reply = f"""There was an error running the SQL Query = {queries}
              The error is {e},
              You should probably try again.
              """
      print(reply)
      return {"reply": reply}
