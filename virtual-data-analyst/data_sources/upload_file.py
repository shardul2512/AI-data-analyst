import pandas as pd
import sqlite3
import csv
import json
import time
import os
import re
from utils import TEMP_DIR

def is_file_done_saving(file_path):
    try:
        with open(file_path, 'r') as f:
            contents = f

        if contents:
            return True
        else:
            return False
    except PermissionError:
        return False

def get_delimiter(file_path, bytes = 4096):
    sniffer = csv.Sniffer()
    data = open(file_path, "r").read(bytes)
    delimiter = sniffer.sniff(data).delimiter
    return delimiter

def read_file(file):
    if file.endswith(('.csv', '.tsv', '.txt')) :
        df = pd.read_csv(file, sep=get_delimiter(file))
    elif file.endswith('.json'):
        with open(file, 'r') as f:
            contents = json.load(f)
        df = pd.json_normalize(contents)
    elif file.endswith('.ndjson'):
        with open(file, 'r') as f:
            contents = f.read()
        data = [json.loads(str(item)) for item in contents.strip().split('\n')]
        df = pd.json_normalize(data)
    elif file.endswith('.xml'):
        df = pd.read_xml(file)
    elif file.endswith(('.xls','xlsx')):
        df = pd.read_excel(file)
    else:
        raise ValueError(f'Unsupported filetype: {file}')
    return df

def process_data_upload(data_file, session_hash):
    try:
        total_time = 0
        while not is_file_done_saving(data_file):
            total_time += .5
            time.sleep(.5)
            if total_time > 10:
                break
            
        df = read_file(data_file)

        # Read each sheet and store data in a DataFrame
        #data = df.parse(sheet_name)
        # Process the data as needed
        # ...
        df.columns = df.columns.str.replace(' ', '_')
        df.columns = df.columns.str.replace('/', '_')

        for column in df.columns:
            if type(column) is str:
                if "date" in column.lower() or "time" in column.lower():
                    try: 
                        df[column] = pd.to_datetime(df[column])
                    except:
                        pass
                if 'year' in column.lower():
                    try: 
                        df[column] = pd.to_datetime(df[column], format='%Y')
                    except:
                        pass
            if df[column].dtype == 'object' and isinstance(df[column].iloc[0], list):
                df[column] = df[column].explode()

        session_path = 'file_upload'

        dir_path = TEMP_DIR / str(session_hash) / str(session_path)
        os.makedirs(dir_path, exist_ok=True)

        connection = sqlite3.connect(f'{dir_path}/data_source.db')
        print("Opened database successfully");
        print(df.columns)

        df.to_sql('data_source', connection, if_exists='replace', index = False)
        
        connection.commit()
        connection.close()

        return ["success","<p style='color:green;text-align:center;font-size:18px;'>Data upload successful</p>"]
    except Exception as e:
        print("UPLOAD ERROR")
        print(e)
        return ["error",f"<p style='color:red;text-align:center;font-size:18px;font-weight:bold;'>ERROR: {e}</p>"]