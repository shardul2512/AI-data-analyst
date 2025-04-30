from utils import TEMP_DIR, message_dict
import gradio as gr
import templates.data_file as data_file, templates.sql_db as sql_db

import os
from getpass import getpass
from dotenv import load_dotenv

load_dotenv()

def delete_db(req: gr.Request):
    import shutil
    dir_path = TEMP_DIR / str(req.session_hash)
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
        message_dict[req.session_hash] = {}

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass("Enter OpenAI API key:")

css= ".file_marker .large{min-height:50px !important;} .padding{padding:0;} .description_component{overflow:visible !important;}"
head = """<meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Virtual Data Analyst</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <!-- Custom Styles -->
    <link rel="stylesheet" href="/gradio_api/file=assets/styles.css">
    """

theme = gr.themes.Base(primary_hue="sky", secondary_hue="slate",font=[gr.themes.GoogleFont("Inter"), "Inter", "sans-serif"]).set(
    button_primary_background_fill="#3B82F6",
    button_secondary_background_fill="#6B7280",
)

from pathlib import Path
gr.set_static_paths(paths=[Path.cwd().absolute()/"assets"])

with gr.Blocks(theme=theme, css=css, head=head, delete_cache=(3600,3600)) as demo:
    header = gr.HTML("""
                        <!-- Header -->
                        <header class="max-w-4xl mx-auto mb-12 text-center">
                            <h1 class="text-4xl font-bold text-gray-900 mb-4">Virtual Data Analyst</h1>
                            <p class="text-lg text-gray-600 mb-6">
                                A powerful tool for data analysis, visualizations, and insights
                            </p>
                        </header>
                        <!-- Main Content -->
                        <main class="max-w-4xl mx-auto">
                            <!-- Features Preview -->
                            <div class="mt-12 grid md:grid-cols-3 gap-6" style="margin-bottom:3px !important;">
                                <div class="feature-card bg-white p-6 rounded-lg shadow-md">
                                    <i class="feature-icon fas fa-chart-line text-primary text-2xl mb-4"></i>
                                    <h3 class="font-semibold text-gray-800 mb-2">Advanced Analytics</h3>
                                    <p class="text-gray-600 text-sm">Run SQL queries, perform regressions, and analyze results with ease</p>
                                </div>
                                <div class="feature-card bg-white p-6 rounded-lg shadow-md">
                                    <i class="feature-icon fas fa-chart-pie text-primary text-2xl mb-4"></i>
                                    <h3 class="font-semibold text-gray-800 mb-2">Rich Visualizations</h3>
                                    <p class="text-gray-600 text-sm">Create scatter plots, line charts, pie charts, and more</p>
                                </div>
                                <div class="feature-card bg-white p-6 rounded-lg shadow-md">
                                    <i class="feature-icon fas fa-magic text-primary text-2xl mb-4"></i>
                                    <h3 class="font-semibold text-gray-800 mb-2">Automated Insights</h3>
                                    <p class="text-gray-600 text-sm">Get instant insights and recommendations for your data</p>
                                </div>
                            </div>
                        </main>""")
    with gr.Tab("Data File"):    
        data_file.demo.render()
    with gr.Tab("SQL Database"):
        sql_db.demo.render()

    footer = gr.HTML("""<!-- Footer -->
        <footer class="max-w-4xl mx-auto mt-12 text-center text-gray-500 text-sm">
            <p>This application is under active development. For bugs or feedback, please open a discussion in the community tab.</p>
        </footer>""")

    demo.unload(delete_db)

## Uncomment the line below to launch the chat app with UI
demo.launch(debug=True, allowed_paths=["temp/","assets/"])