import psycopg2
import os
from utils import TEMP_DIR

def connect_sql_db(url, sql_user, sql_port, sql_pass, sql_db_name, session_hash):
    try:
        conn = psycopg2.connect(
            database=sql_db_name,
            user=sql_user,
            password=sql_pass,
            host=url,  # e.g., "localhost" or an IP address
            port=sql_port  # default is 5432
        )
        print("Connected to PostgreSQL")
    
        # Create a cursor object to execute SQL queries
        cur = conn.cursor()
        # Example: Execute a query
        cur.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""")
        table_tuples = cur.fetchall()
        table_names = []
        for table in table_tuples:
            table_names.append(table[0])

        print(table_names)
    
        # Close the cursor and connection
        cur.close()
        conn.close()
        print("Connection closed.")

        session_path = 'sql'

        dir_path = TEMP_DIR / str(session_hash) / str(session_path)
        os.makedirs(dir_path, exist_ok=True)

        return ["success","<p style='color:green;text-align:center;font-size:18px;'>SQL database connected successful</p>", table_names]
    except Exception as e:
        print("UPLOAD ERROR")
        print(e)
        return ["error",f"<p style='color:red;text-align:center;font-size:18px;font-weight:bold;'>ERROR: {e}</p>"]
        
