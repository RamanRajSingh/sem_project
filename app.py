from flask import Flask, render_template, jsonify, request
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import os

app = Flask(__name__)

# Load the notebook
notebook_path = "index.ipynb"

def load_notebook():
    with open(notebook_path, "r", encoding="utf-8") as f:
        return nbformat.read(f, as_version=4)

# Execute a specific cell by index
def execute_cell(cell_index):
    notebook = load_notebook()
    executor = ExecutePreprocessor(timeout=600, kernel_name="python3")

    # Execute only up to the requested cell
    executed_cells = notebook.cells[1:cell_index + 2]
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
def index():
    notebook = load_notebook()
    total_cells = len(notebook.cells)
    return render_template("index.html", total_cells=total_cells)

@app.route("/run-cell/<int:cell_index>")
def run_cell(cell_index):
    output = execute_cell(cell_index)
    return jsonify({"output": output})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
