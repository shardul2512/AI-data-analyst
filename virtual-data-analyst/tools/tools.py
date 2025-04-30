import sqlite3
import psycopg2
from .stats_tools import stats_tools
from .chart_tools import chart_tools
from utils import TEMP_DIR

def data_file_tools_call(session_hash):
    dir_path = TEMP_DIR / str(session_hash)
    connection = sqlite3.connect(f'{dir_path}/file_upload/data_source.db')
    print("Querying Database in Tools.py");
    cur=connection.execute('select * from data_source')
    columns = [i[0] for i in cur.description]
    print("COLUMNS 2")
    print(columns)
    cur.close()
    connection.close()

    column_string = (columns[:625] + '..') if len(columns) > 625 else columns

    tools_calls = [
        {
            "type": "function",
            "function": {
                "name": "sql_query_func",
                "description": f"""This is a tool useful to query a SQLite table called 'data_source' with the following Columns: {column_string}.
                There may also be more columns in the table if the number of columns is too large to process. 
                This function also saves the results of the query to csv file called query.csv.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "queries": {
                            "type": "array",
                            "description": "The query to use in the search. Infer this from the user's message. It should be a question or a statement",
                            "items": {
                                "type": "string",
                            }
                        }
                    },
                    "required": ["queries"],
                },
            },
        },
    ]

    tools_calls.extend(chart_tools)
    tools_calls.extend(stats_tools)

    return tools_calls

def sql_tools_call(db_tables):
    
    table_string = (db_tables[:625] + '..') if len(db_tables) > 625 else db_tables
        
    tools_calls = [
        {
            "type": "function",
            "function": {
                "name": "sql_query_func",
                "description": f"""This is a tool useful to query a PostgreSQL database with the following tables, {table_string}.
                There may also be more tables in the database if the number of columns is too large to process.
                This function also saves the results of the query to csv file called query.csv.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "queries": {
                            "type": "array",
                            "description": "The PostgreSQL query to use in the search. Infer this from the user's message. It should be a question or a statement",
                            "items": {
                                "type": "string",
                            }
                        }
                    },
                    "required": ["queries"],
                },
            },
        },
    ]

    tools_calls.extend(chart_tools)
    tools_calls.extend(stats_tools)

    return tools_calls