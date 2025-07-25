from flask import Flask, request, jsonify, render_template
import subprocess
import tempfile
import os

app = Flask(__name__, template_folder="templates")

def analyze_error(error_message):
    suggestions = []

    if "SyntaxError" in error_message:
        suggestions.append("🔧 Check for missing colons, parentheses, or incorrect syntax.")
    elif "NameError" in error_message:
        suggestions.append("🔍 Make sure all variables/functions are defined before use.")
    elif "TypeError" in error_message:
        suggestions.append("⚠️ Check if you're using the correct data types.")
    elif "IndexError" in error_message:
        suggestions.append("📏 You're trying to access an invalid index in a list.")
    elif "IndentationError" in error_message:
        suggestions.append("🧱 Ensure consistent indentation (4 spaces recommended).")
    elif "ZeroDivisionError" in error_message:
        suggestions.append("➗ You're dividing by zero — check your denominator.")
    elif "ModuleNotFoundError" in error_message:
        suggestions.append("📦 Module not found — install it using pip.")
    elif "ImportError" in error_message:
        suggestions.append("🧩 Double-check module names and their installation.")
    else:
        suggestions.append("💡 Check the syntax and logic of your code carefully.")

    return suggestions

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_code():
    code = request.json.get('code', '')
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name

    try:
        result = subprocess.run(['python', temp_path], capture_output=True, text=True, timeout=10)
        output = result.stdout
        error = result.stderr

        if result.returncode != 0:
            suggestions = analyze_error(error)
            return jsonify({'output': output, 'error': error, 'suggestions': suggestions})
        return jsonify({'output': output})
    except subprocess.TimeoutExpired:
        return jsonify({
            'output': '',
            'error': 'Execution timed out.',
            'suggestions': ['Avoid infinite loops or long-running operations.']
        })
    finally:
        os.remove(temp_path)

if __name__ == '__main__':
    app.run(debug=True)
