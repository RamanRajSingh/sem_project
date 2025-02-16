from flask import Flask, render_template, jsonify, request
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import os

app = Flask(__name__)

# Load and execute a specific cell from Jupyter Notebook
notebook_path = "your_notebook.ipynb"

def load_notebook():
    with open(notebook_path, "r", encoding="utf-8") as f:
        return nbformat.read(f, as_version=4)

def execute_cell(cell_index):
    notebook = load_notebook()
    executor = ExecutePreprocessor(timeout=600, kernel_name="python3")
    
    executed_cells = notebook.cells[:cell_index + 1]
    notebook.cells = executed_cells

    try:
        executor.preprocess(notebook, {'metadata': {'path': os.path.dirname(notebook_path)}})
        output_text = []
        
        for output in notebook.cells[cell_index].outputs:
            if 'text' in output:
                output_text.append(output['text'])
            elif 'text/plain' in output.get('data', {}):
                output_text.append(output['data']['text/plain'])
        
        return "\n".join(output_text) if output_text else "No Output"
    
    except Exception as e:
        return f"Error executing cell {cell_index}: {str(e)}"

@app.route("/")
def home():
    return "Flask Server is Running!"

@app.route("/run-cell/<int:cell_index>")
def run_cell(cell_index):
    output = execute_cell(cell_index)
    return jsonify({"output": output})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
