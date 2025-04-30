stats_tools = [
        {
        "type": "function",
            "function": {
                "name": "regression_func",
                "description": f"""This a tool to calculate regressions on our data source that we are querying.
                We can run queries with our 'sql_query_func' function and they will be available to use in this function via the query.csv file that is generated.
                Returns a dictionary of values that includes a regression_summary and a regression chart (which is an iframe displaying the
                linear regression in chart form and should be shown to the user).""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "independent_variables": {
                            "type": "array",
                            "description": f"""An array of strings that states the independent variables in our data set which should be column names in our query.csv file that is generated
                            in the 'sql_query_func' function. This will allow us to identify the data to use for our independent variables.
                            Infer this from the user's message.""",
                            "items": {
                                "type": "string",
                            }
                        },
                        "dependent_variable": {
                            "type": "string",
                            "description": f"""A string that states the dependent variables in our data set which should be a column name in our query.csv file that is generated
                            in the 'sql_query_func' function. This will allow us to identify the data to use for our dependent variables.
                            Infer this from the user's message.""",
                            "items": {
                                "type": "string",
                            }
                        },
                        "category": {
                            "type": "string",
                            "description": f"""An optional column in our query.csv file that contain a parameter that will define the category for the data. 
                            Do not send value if no category is needed or specified. This category must be present in our query.csv file to be valid.""",
                            "items": {
                                "type": "string",
                            }
                        }
                    },
                    "required": ["independent_variables","dependent_variable"],
                },
            }, 
        }    
]