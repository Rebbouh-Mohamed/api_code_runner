from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import tempfile
import os
import re

# Initialize the FastAPI app
app = FastAPI()

# Regex to extract class name for Java
class_name_pattern = r'class\s+(\w+)'

# Define request schema
class CodeRequest(BaseModel):
    code: str
    language: str

# Supported languages and their file extensions
file_ext = {
    "python": "py",
    "java": "java",
    "php": "php",
    "cpp": "cpp",
    "c": "c",
    "cs": "cs",
    "js": "js"
}

@app.post("/run_code")
async def run_code(request: CodeRequest):
    code = request.code
    language = request.language

    # Check if the language is supported
    if language not in file_ext:
        raise HTTPException(status_code=400, detail="Unsupported language")

    try:
        # Create a temporary directory to handle code execution
        with tempfile.TemporaryDirectory() as temp_dir:
            if language == "java":
                # Extract the class name using regex
                match = re.search(class_name_pattern, code)
                if match:
                    class_name = match.group(1)
                else:
                    raise HTTPException(status_code=400, detail="No class found in the Java code")

                # Save the Java code in the temporary directory with the correct class name
                filename = os.path.join(temp_dir, f"{class_name}.java")
                with open(filename, 'w') as temp_file:
                    temp_file.write(code)

            else:
                # For other languages, use a generic filename
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
                    return {"output": compile_res.stdout, "error": compile_res.stderr}
                # Run the compiled Java class
                result = subprocess.run(['java', '-cp', temp_dir, class_name], capture_output=True, text=True, timeout=10)
            elif language == "php":
                result = subprocess.run(['php', filename], capture_output=True, text=True, timeout=10)
            elif language == "cpp":
                output_file = os.path.join(temp_dir, "program")
                compile_res = subprocess.run(['g++', filename, '-o', output_file], capture_output=True, text=True)
                if compile_res.returncode != 0:
                    return {"output": compile_res.stdout, "error": compile_res.stderr}
                result = subprocess.run([output_file], capture_output=True, text=True, timeout=10)
            elif language == "c":
                output_file = os.path.join(temp_dir, "program")
                compile_res = subprocess.run(['gcc', filename, '-o', output_file], capture_output=True, text=True)
                if compile_res.returncode != 0:
                    return {"output": compile_res.stdout, "error": compile_res.stderr}
                result = subprocess.run([output_file], capture_output=True, text=True, timeout=10)
            elif language == "cs":
                # Save the compiled output as an executable in the same directory
                output_file = os.path.join(temp_dir, "Program.exe")
                compile_res = subprocess.run(['csc', '-out:' + output_file, filename], capture_output=True, text=True)
                if compile_res.returncode != 0:
                    return {"output": compile_res.stdout, "error": compile_res.stderr}
                # Run the executable
                result = subprocess.run([output_file], capture_output=True, text=True, timeout=10)
            elif language == "js":
                result = subprocess.run(['node', filename], capture_output=True, text=True, timeout=10)

            # Return the output and errors (if any)
            return {"output": result.stdout, "error": result.stderr}

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Code execution timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
