from flask import Flask, request, jsonify
import subprocess
import tempfile
import os
import re
import shutil

app = Flask(__name__)

# Regex to extract class name
class_name_pattern = r'class\s+(\w+)'

@app.route('/run_code', methods=['POST'])
def run_code():
    data = request.get_json()
    code = data.get('code')
    language = data.get('language')

    file_ext = {
        "python": "py",
        "java": "java",
        "php": "php",
        "cpp": "cpp",
        "js": "js"
    }

    if language not in file_ext:
        return jsonify({"error": "Unsupported language"}), 400

    try:
        # Create a temporary directory to avoid file name collisions
        with tempfile.TemporaryDirectory() as temp_dir:
            if language == "java":
                # Extract the class name using regex
                match = re.search(class_name_pattern, code)
                if match:
                    class_name = match.group(1)
                else:
                    return jsonify({"error": "No class found in the Java code"}), 400

                # Save the Java code in the temporary directory with the correct class name
                filename = os.path.join(temp_dir, f"{class_name}.java")
                with open(filename, 'w') as temp_file:
                    temp_file.write(code)

            else:
                # For other languages, use tempfile
                filename = os.path.join(temp_dir, f"code.{file_ext[language]}")
                with open(filename, 'w') as temp_file:
                    temp_file.write(code)

            # Run the code based on the language
            if language == "python":
                result = subprocess.run(['python3', filename], capture_output=True, text=True, timeout=10)
            elif language == "java":
                # Compile the Java file
                compile_res = subprocess.run(['javac', filename], capture_output=True, text=True)
                if compile_res.returncode != 0:
                    return jsonify({"output": compile_res.stdout, "error": compile_res.stderr})
                # Run the compiled Java class
                result = subprocess.run(['java', class_name], capture_output=True, text=True, timeout=10)
            elif language == "php":
                result = subprocess.run(['php', filename], capture_output=True, text=True, timeout=10)
            elif language == "cpp":
                output_file = filename[:-4]  # Remove the .cpp extension
                compile_res = subprocess.run(['gcc', filename, '-o', output_file], capture_output=True, text=True)
                if compile_res.returncode != 0:
                    return jsonify({"output": compile_res.stdout, "error": compile_res.stderr})
                result = subprocess.run([f'./{output_file}'], capture_output=True, text=True, timeout=10)
            elif language == "js":
                result = subprocess.run(['node', filename], capture_output=True, text=True, timeout=10)

            return jsonify({"output": result.stdout, "error": result.stderr})

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Code execution timed out"}), 408
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
