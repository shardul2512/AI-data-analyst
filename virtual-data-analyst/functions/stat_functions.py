
import pandas as pd
from typing import List
from utils import TEMP_DIR
import plotly.express as px
import plotly.io as pio
import os
from functions import scatter_chart_fig
from dotenv import load_dotenv

load_dotenv()

root_url = os.getenv("ROOT_URL")

def regression_func(independent_variables: List[str], dependent_variable: str, session_hash, session_folder, category: str='', **kwargs):
    print("LINEAR REGRESSION CALCULATION")
    print(independent_variables)
    print(dependent_variable)
    try:
        dir_path = TEMP_DIR / str(session_hash) / str(session_folder)
        chart_path = f'{dir_path}/chart.html'
        csv_query_path = f'{dir_path}/query.csv'

        df = pd.read_csv(csv_query_path)

        if category in df.columns:
           fig = scatter_chart_fig(df=df, x_column=independent_variables,y_column=dependent_variable, 
                                    category=category,trendline="ols")
        else:
           fig = scatter_chart_fig(df=df,x_column=independent_variables,y_column=dependent_variable, 
                                    trendline="ols")

        pio.write_html(fig, chart_path, full_html=False)

        chart_url = f'{root_url}/gradio_api/file/temp/{session_hash}/{session_folder}/chart.html'

        iframe = 'Please display this iframe: <div style=overflow:auto;><iframe\n    scrolling="yes"\n    width="1000px"\n    height="500px"\n    src="' + chart_url + '"\n    frameborder="0"\n    allowfullscreen\n></iframe>\n</div>'

        results_frame = px.get_trendline_results(fig)

        print("RESULTS")
        print(results_frame)
        print(results_frame.at[0, 'px_fit_results'])
        results = results_frame.at[0, 'px_fit_results']
        print(results.summary())

        return {"reply": '{"regression_summary": %s, "regression_chart": %s' % (str(results.summary()), str(iframe))} 
    
    except Exception as e:
      print("LINEAR REGRESSION ERROR")
      print(e)
      reply = f"""There was an error generating the linear regression calculation from {independent_variables} and {dependent_variable}
              The error is {e},
              You should probably try again.
              """
      return {"reply": reply}
