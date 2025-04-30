from typing import List
import plotly.io as pio
import plotly.express as px
import pandas as pd
from utils import TEMP_DIR
import os
import ast
from dotenv import load_dotenv

load_dotenv()

root_url = os.getenv("ROOT_URL")

def llm_chart_data_scrub(data, layout):
   #Processing data to account for variation from LLM
   data_list = []
   layout_dict = {}

   if isinstance(data, list):
      data_list = data
   else:
      data_list.append(data) 

   false_replace = [':false', ': false']
   false_value = ':False'   
   true_replace = [':true', ': true']
   true_value = ':True' 

   data_dict = {}   
   for data_obj in data_list:   
      if isinstance(data_obj, str):
         data_obj = data_obj.replace("\n", "")
         for replace in false_replace:
            data_obj = data_obj.replace(replace, false_value)
         for replace in true_replace:
            data_obj = data_obj.replace(replace, true_value)
         print(data_obj)
         data_dict = ast.literal_eval(data_obj)
      else:
         data_dict = data_obj

   if layout and isinstance(layout, list):
      layout_obj = layout[0]
   else:
      layout_obj = layout

   if layout_obj and isinstance(layout_obj, str):
      for replace in false_replace:
         layout_obj = layout_obj.replace(replace, false_value)
      for replace in true_replace:
         layout_obj = layout_obj.replace(replace, true_value)
      print(layout_obj)
      layout_dict = ast.literal_eval(layout_obj)
   else:
      layout_dict = layout_obj

   return data_dict, layout_dict

def scatter_chart_fig(df, x_column: List[str], y_column: str, category: str="", trendline: str="", 
                      trendline_options: List[dict]=[{}], marginal_x: str="", marginal_y: str="",
                      size: str=""):
   
   function_args = {"data_frame":df, "x":x_column, "y":y_column}

   if category:
      function_args["color"] = category
   if trendline:
      function_args["trendline"] = trendline
   if marginal_x:
      function_args["marginal_x"] = marginal_x
   if marginal_y:
      function_args["marginal_y"] = marginal_y
   if size:
      df.loc[df[size] < 0, size] = 0
      function_args["size"] = size   
   if trendline_options:
      trendline_options_dict = {}
      if trendline_options and isinstance(trendline_options, list):
         trendline_options_obj = trendline_options[0]
      else:
         trendline_options_obj = trendline_options

      if trendline_options_obj and isinstance(trendline_options_obj, str):
         trendline_options_dict = ast.literal_eval(trendline_options_obj)
      else:
         trendline_options_dict = trendline_options_obj
      function_args["trendline_options"] = trendline_options_dict

   fig = px.scatter(**function_args)  

   return fig

def scatter_chart_generation_func(x_column: List[str], y_column: str, session_hash, session_folder, data: List[dict]=[{}], layout: List[dict]=[{}], 
                                  category: str="", trendline: str="", trendline_options: List[dict]=[{}], marginal_x: str="", marginal_y: str="",
                                  size: str="", **kwargs):
   try:
      dir_path = TEMP_DIR / str(session_hash) / str(session_folder)
      chart_path = f'{dir_path}/chart.html'
      csv_query_path = f'{dir_path}/query.csv'

      df = pd.read_csv(csv_query_path)

      initial_graph = scatter_chart_fig(df, x_column=x_column, y_column=y_column, 
                              category=category, trendline=trendline, trendline_options=trendline_options,
                              marginal_x=marginal_x, marginal_y=marginal_y, size=size)
      
      fig = initial_graph.to_dict()

      print(data)
      print(layout)

      data_dict,layout_dict = llm_chart_data_scrub(data,layout)

      #Applying stylings and settings generated from LLM
      if layout_dict:
         fig["layout"] = layout_dict

      data_ignore = ["x","y","type"]

      if size:
         data_ignore.append("marker")

      for key, value in data_dict.items():
         if key not in data_ignore:
            for data_item in fig["data"]:
               data_item[key] = value
   
      pio.write_html(fig, chart_path, full_html=False)

      chart_url = f'{root_url}/gradio_api/file/temp/{session_hash}/{session_folder}/chart.html'

      iframe = 'Please display this iframe: <div style=overflow:auto;><iframe\n    scrolling="yes"\n    width="1000px"\n    height="500px"\n    src="' + chart_url + '"\n    frameborder="0"\n    allowfullscreen\n></iframe>\n</div>'

      return {"reply": iframe}

   except Exception as e:
      print("SCATTER PLOT ERROR")
      print(e)
      reply = f"""There was an error generating the Plotly Scatter Plot from {x_column}, {y_column}, {data}, and {layout}
            The error is {e},
            You should probably try again.
            """
      return {"reply": reply}
   
def line_chart_generation_func(x_column: str, y_column: str, session_hash, session_folder, data: List[dict]=[{}], layout: List[dict]=[{}], 
                                  category: str="", **kwargs):
   try:
      dir_path = TEMP_DIR / str(session_hash) / str(session_folder)
      chart_path = f'{dir_path}/chart.html'
      csv_query_path = f'{dir_path}/query.csv'

      df = pd.read_csv(csv_query_path)

      function_args = {"data_frame":df, "x":x_column, "y":y_column}

      if category:
         function_args["color"] = category

      initial_graph = px.line(**function_args)  

      fig = initial_graph.to_dict()

      data_dict,layout_dict = llm_chart_data_scrub(data,layout)

      print(data_dict)
      print(layout_dict)

      #Applying stylings and settings generated from LLM
      if layout_dict:
         fig["layout"] = layout_dict

      for key, value in data_dict.items():
         if key not in ["x","y","type"]:
            for data_item in fig["data"]:
               data_item[key] = value

      print(fig)       
   
      pio.write_html(fig, chart_path, full_html=False)

      chart_url = f'{root_url}/gradio_api/file/temp/{session_hash}/{session_folder}/chart.html'

      iframe = 'Please display this iframe: <div style=overflow:auto;><iframe\n    scrolling="yes"\n    width="1000px"\n    height="500px"\n    src="' + chart_url + '"\n    frameborder="0"\n    allowfullscreen\n></iframe>\n</div>'

      return {"reply": iframe}

   except Exception as e:
      print("LINE CHART ERROR")
      print(e)
      reply = f"""There was an error generating the Plotly Line Chart from {x_column}, {y_column}, {data}, and {layout}
            The error is {e},
            You should probably try again.
            """
      return {"reply": reply}

def bar_chart_generation_func(x_column: str, y_column: str, session_hash, session_folder, data: List[dict]=[{}], layout: List[dict]=[{}], 
                                  category: str="", facet_row: str="", facet_col: str="", **kwargs):
   try:
      dir_path = TEMP_DIR / str(session_hash) / str(session_folder)
      chart_path = f'{dir_path}/chart.html'
      csv_query_path = f'{dir_path}/query.csv'

      df = pd.read_csv(csv_query_path)

      function_args = {"data_frame":df, "x":x_column, "y":y_column}

      if category:
         function_args["color"] = category
      if facet_row:
         function_args["facet_row"] = facet_row
      if facet_col:
         function_args["facet_col"] = facet_col

      initial_graph = px.bar(**function_args)  

      fig = initial_graph.to_dict()

      data_dict,layout_dict = llm_chart_data_scrub(data,layout)

      print(data_dict)
      print(layout_dict)

      #Applying stylings and settings generated from LLM
      if layout_dict:
         fig["layout"] = layout_dict

      for key, value in data_dict.items():
         if key not in ["x","y","type"]:
            for data_item in fig["data"]:
               data_item[key] = value

      print(fig)       
   
      pio.write_html(fig, chart_path, full_html=False)

      chart_url = f'{root_url}/gradio_api/file/temp/{session_hash}/{session_folder}/chart.html'

      iframe = 'Please display this iframe: <div style=overflow:auto;><iframe\n    scrolling="yes"\n    width="1000px"\n    height="500px"\n    src="' + chart_url + '"\n    frameborder="0"\n    allowfullscreen\n></iframe>\n</div>'

      return {"reply": iframe}

   except Exception as e:
      print("BAR CHART ERROR")
      print(e)
      reply = f"""There was an error generating the Plotly Bar Chart from {x_column}, {y_column}, {data}, and {layout}
            The error is {e},
            You should probably try again.
            """
      return {"reply": reply}

def pie_chart_generation_func(values: str, names: str, session_hash, session_folder, data: List[dict]=[{}], layout: List[dict]=[{}], **kwargs):
   try:
      dir_path = TEMP_DIR / str(session_hash) / str(session_folder)
      chart_path = f'{dir_path}/chart.html'
      csv_query_path = f'{dir_path}/query.csv'

      df = pd.read_csv(csv_query_path)

      function_args = {"data_frame":df, "values":values, "names":names}

      initial_graph = px.pie(**function_args)  

      fig = initial_graph.to_dict()

      data_dict,layout_dict = llm_chart_data_scrub(data,layout)

      print(data_dict)
      print(layout_dict)

      #Applying stylings and settings generated from LLM
      if layout_dict:
         fig["layout"] = layout_dict

      for key, value in data_dict.items():
         if key not in ["x","y","type"]:
            for data_item in fig["data"]:
               data_item[key] = value

      print(fig)       
   
      pio.write_html(fig, chart_path, full_html=False)

      chart_url = f'{root_url}/gradio_api/file/temp/{session_hash}/{session_folder}/chart.html'

      iframe = 'Please display this iframe: <div style=overflow:auto;><iframe\n    scrolling="yes"\n    width="1000px"\n    height="500px"\n    src="' + chart_url + '"\n    frameborder="0"\n    allowfullscreen\n></iframe>\n</div>'

      return {"reply": iframe}

   except Exception as e:
      print("PIE CHART ERROR")
      print(e)
      reply = f"""There was an error generating the Plotly Pie Chart from {values}, {names}, {data}, and {layout}
            The error is {e},
            You should probably try again.
            """
      return {"reply": reply}
   
def histogram_generation_func(x_column: str, session_hash, session_folder, y_column: str="", data: List[dict]=[{}], layout: List[dict]=[{}], histnorm: str="", category: str="",
                              histfunc: str="", **kwargs):   
   try:
      dir_path = TEMP_DIR / str(session_hash) / str(session_folder)
      chart_path = f'{dir_path}/chart.html'
      csv_query_path = f'{dir_path}/query.csv'

      df = pd.read_csv(csv_query_path)

      print(x_column)

      function_args = {"data_frame":df, "x":x_column}

      if y_column:
         function_args["y"] = y_column
      if histnorm:
         function_args["histnorm"] = histnorm
      if category:
         function_args["color"] = category
      if histfunc:
         function_args["histfunc"] = histfunc

      initial_graph = px.histogram(**function_args)  

      fig = initial_graph.to_dict()

      data_dict,layout_dict = llm_chart_data_scrub(data,layout)

      print(data_dict)
      print(layout_dict)

      #Applying stylings and settings generated from LLM
      if layout_dict:
         fig["layout"] = layout_dict

      for key, value in data_dict.items():
         if key not in ["x","y","type"]:
            for data_item in fig["data"]:
               data_item[key] = value

      print(fig)       
   
      pio.write_html(fig, chart_path, full_html=False)

      chart_url = f'{root_url}/gradio_api/file/temp/{session_hash}/{session_folder}/chart.html'

      iframe = 'Please display this iframe: <div style=overflow:auto;><iframe\n    scrolling="yes"\n    width="1000px"\n    height="500px"\n    src="' + chart_url + '"\n    frameborder="0"\n    allowfullscreen\n></iframe>\n</div>'

      return {"reply": iframe}

   except Exception as e:
      print("HISTOGRAM ERROR")
      print(e)
      reply = f"""There was an error generating the Plotly Histogram from {x_column}.
            The error is {e},
            You should probably try again.
            """
      return {"reply": reply}

def table_generation_func(session_hash, session_folder, **kwargs):
    print("TABLE GENERATION")
    try: 
        dir_path = TEMP_DIR / str(session_hash) / str(session_folder)
        csv_query_path = f'{dir_path}/query.csv'
        table_path = f'{dir_path}/table.html'

        df = pd.read_csv(csv_query_path)

        html_table = df.to_html()
        print(html_table[:1000])

        with open(table_path, "w") as file:
         file.write(html_table)

        table_url = f'{root_url}/gradio_api/file/temp/{session_hash}/{session_folder}/table.html'

        iframe = 'Please display this iframe: <div style=overflow:auto;><iframe\n scrolling="yes"\n    width="1000px"\n    height="500px"\n    src="' + table_url + '"\n    frameborder="0"\n    allowfullscreen\n></iframe>\n</div>'
        print(iframe)
        return {"reply": iframe}
    
    except Exception as e:
      print("TABLE ERROR")
      print(e)
      reply = f"""There was an error generating the Pandas DataFrame table results.
              The error is {e},
              You should probably try again.
              """
      return {"reply": reply}    
