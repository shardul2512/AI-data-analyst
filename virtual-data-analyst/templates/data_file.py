import gradio as gr
from functions import example_question_generator, chatbot_with_fc
from data_sources import process_data_upload
from utils import message_dict
import ast

def run_example(input):
    return input

def example_display(input):
    if input == None:
        display = True
    else:
        display = False
    return [gr.update(visible=display),gr.update(visible=display),gr.update(visible=display),gr.update(visible=display)]

with gr.Blocks() as demo:
    description = gr.HTML("""
                        <!-- Header -->
                        <div class="max-w-4xl mx-auto mb-12 text-center">
                            <div class="bg-blue-50 border border-blue-200 rounded-lg max-w-2xl mx-auto">
                                <h2 class="font-semibold text-blue-800 ">
                                    <i class="fas fa-info-circle mr-2"></i>Supported Files
                                </h2>
                                <div class="flex flex-wrap justify-center gap-3 pb-4 text-blue-700">
                                    <span class="tooltip">
                                        <i class="fas fa-file-csv mr-1"></i>CSV
                                        <span class="tooltip-text">Comma-separated values</span>
                                    </span>
                                    <span class="tooltip">
                                        <i class="fas fa-file-alt mr-1"></i>TSV
                                        <span class="tooltip-text">Tab-separated values</span>
                                    </span>
                                    <span class="tooltip">
                                        <i class="fas fa-file-alt mr-1"></i>TXT
                                        <span class="tooltip-text">Text files</span>
                                    </span>
                                    <span class="tooltip">
                                        <i class="fas fa-file-excel mr-1"></i>XLS/XLSX
                                        <span class="tooltip-text">Excel spreadsheets</span>
                                    </span>
                                    <span class="tooltip">
                                        <i class="fas fa-file-code mr-1"></i>XML
                                        <span class="tooltip-text">XML documents</span>
                                    </span>
                                    <span class="tooltip">
                                        <i class="fas fa-file-code mr-1"></i>JSON
                                        <span class="tooltip-text">JSON data files</span>
                                    </span>
                                </div>
                            </div>
                        </div>
                          """, elem_classes="description_component")
    example_file_1 = gr.File(visible=False, value="samples/bank_marketing_campaign.csv")
    example_file_2 = gr.File(visible=False, value="samples/online_retail_data.csv")
    example_file_3 = gr.File(visible=False, value="samples/tb_illness_data.csv")
    with gr.Row():
        example_btn_1 = gr.Button(value="Try Me: bank_marketing_campaign.csv", elem_classes="sample-btn bg-gradient-to-r from-purple-500 to-indigo-600 text-white p-6 rounded-lg text-left hover:shadow-lg", size="md", variant="primary")
        example_btn_2 = gr.Button(value="Try Me: online_retail_data.csv", elem_classes="sample-btn bg-gradient-to-r from-purple-500 to-indigo-600 text-white p-6 rounded-lg text-left hover:shadow-lg", size="md", variant="primary")
        example_btn_3 = gr.Button(value="Try Me: tb_illness_data.csv", elem_classes="sample-btn bg-gradient-to-r from-purple-500 to-indigo-600 text-white p-6 rounded-lg text-left hover:shadow-lg", size="md", variant="primary")

    file_output = gr.File(label="Data File (CSV, TSV, TXT, XLS, XLSX, XML, JSON)", show_label=True, elem_classes="file_marker drop-zone border-2 border-dashed border-gray-300 rounded-lg hover:border-primary cursor-pointer bg-gray-50 hover:bg-blue-50 transition-colors duration-300", file_types=['.csv','.xlsx','.txt','.json','.ndjson','.xml','.xls','.tsv'])
    example_btn_1.click(fn=run_example, inputs=example_file_1, outputs=file_output)
    example_btn_2.click(fn=run_example, inputs=example_file_2, outputs=file_output)
    example_btn_3.click(fn=run_example, inputs=example_file_3, outputs=file_output)
    file_output.change(fn=example_display, inputs=file_output, outputs=[example_btn_1, example_btn_2, example_btn_3, description])

    @gr.render(inputs=file_output)
    def data_options(filename, request: gr.Request):
        print(filename)
        if request.session_hash not in message_dict:
            message_dict[request.session_hash] = {}
        message_dict[request.session_hash]['file_upload'] = None
        if filename:
            process_message = process_upload(filename, request.session_hash)
            gr.HTML(value=process_message[1], padding=False)
            if process_message[0] == "success":
                if "bank_marketing_campaign" in filename:
                    example_questions = [
                                            ["Describe the dataset"],
                                            ["What levels of education have the highest and lowest average balance?"],
                                            ["What job is most and least common for a yes response from the individuals, not counting 'unknown'?"],
                                            ["Can you generate a bar chart of education vs. average balance?"],
                                            ["Can you generate a table of levels of education versus average balance, percent married, percent with a loan, and percent in default?"],
                                            ["Can we predict the relationship between the number of contacts performed before this campaign and the average balance?"],
                                            ["Can you plot the number of contacts performed before this campaign versus the duration and use balance as the size in a bubble chart?"]
                                        ]
                elif "online_retail_data" in filename:
                    example_questions = [
                                            ["Describe the dataset"],
                                            ["What month had the highest revenue?"],
                                            ["Is revenue higher in the morning or afternoon?"],
                                            ["Can you generate a line graph of revenue per month?"],
                                            ["Can you generate a table of revenue per month?"],
                                            ["Can we predict how time of day affects transaction value in this data set?"],
                                            ["Can you plot revenue per month with size being the number of units sold that month in a bubble chart?"]
                                        ]
                else:
                    try:
                        generated_examples = ast.literal_eval(example_question_generator(request.session_hash))
                        example_questions = [
                                                ["Describe the dataset"]
                                            ]
                        for example in generated_examples:
                            example_questions.append([example])
                    except Exception as e:
                        print("DATA FILE QUESTION GENERATION ERROR")
                        print(e)
                        example_questions = [
                                            ["Describe the dataset"],
                                            ["List the columns in the dataset"],
                                            ["What could this data be used for?"],
                                        ]
                parameters = gr.Textbox(visible=False, value=request.session_hash)
                bot = gr.Chatbot(type='messages', label="CSV Chat Window", render_markdown=True, sanitize_html=False, show_label=True, render=False, visible=True, elem_classes="chatbot")
                chat = gr.ChatInterface(
                                    fn=chatbot_with_fc,
                                    type='messages',
                                    chatbot=bot,
                                    title="Chat with your data file",
                                    concurrency_limit=None,
                                    examples=example_questions,
                                    additional_inputs=parameters
                                    )
                
    def process_upload(upload_value, session_hash):
        if upload_value:
            process_message = process_data_upload(upload_value, session_hash)
        return process_message
                    

if __name__ == "__main__":
    demo.launch()    