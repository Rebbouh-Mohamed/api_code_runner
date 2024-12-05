from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
import uuid
import shutil
import tempfile
import asyncio

app = FastAPI()

class CodeExecutionRequest(BaseModel):
    language: str
    stdin: str
    code: str


# Map languages to their corresponding commands for execution
LANGUAGE_COMMANDS = {
    "python": "python3",
    "c": "gcc",
    "cpp": "g++",
    "java": "javac",
    "javascript": "node"
}

@app.post("/run-code")
async def run_code(request: CodeExecutionRequest):
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp(prefix="temp_code_")

    try:
        # Define file extensions for each language
        file_extension_map = {
            "python": ".py",
            "c": ".c",
            "cpp": ".cpp",
            "java": ".java",
            "javascript": ".js"
        }

        # Check if the language is supported
        if request.language not in file_extension_map:
            raise HTTPException(status_code=400, detail="Unsupported language")

        file_extension = file_extension_map[request.language]
        file_name = f"Main{file_extension}"
        file_path = os.path.join(temp_dir, file_name)

        # Write the code to the file
        with open(file_path, "w") as code_file:
            code_file.write(request.code)

        # Prepare the execution command
        if request.language == "python":
            command = [LANGUAGE_COMMANDS["python"], file_path]

        elif request.language == "javascript":
            command = [LANGUAGE_COMMANDS["javascript"], file_path]

        elif request.language == "c":
            executable = os.path.join(temp_dir, "a.out")
            compile_command = [LANGUAGE_COMMANDS["c"], file_path, "-o", executable]
            compile_process = await asyncio.create_subprocess_exec(
                *compile_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            _, compile_stderr = await compile_process.communicate()
            if compile_process.returncode != 0:
                raise HTTPException(status_code=400, detail=compile_stderr.decode().strip())
            command = [executable]

        elif request.language == "cpp":
            executable = os.path.join(temp_dir, "a.out")
            compile_command = [LANGUAGE_COMMANDS["cpp"], file_path, "-o", executable]
            compile_process = await asyncio.create_subprocess_exec(
                *compile_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            _, compile_stderr = await compile_process.communicate()
            if compile_process.returncode != 0:
                raise HTTPException(status_code=400, detail=compile_stderr.decode().strip())
            command = [executable]

        elif request.language == "java":
            compile_command = [LANGUAGE_COMMANDS["java"], file_path]
            compile_process = await asyncio.create_subprocess_exec(
                *compile_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=temp_dir
            )
            _, compile_stderr = await compile_process.communicate()
            if compile_process.returncode != 0:
                raise HTTPException(status_code=400, detail=compile_stderr.decode().strip())
            class_name = os.path.splitext(file_name)[0]
            command = ["java", "-cp", temp_dir, class_name]

        else:
            raise HTTPException(status_code=400, detail="Unsupported language")

        # Run the command and capture output
        process = await asyncio.create_subprocess_exec(
            *command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=temp_dir
        )

        stdout, stderr = await process.communicate(input=request.stdin.encode())

        # Return the output
        return {
            "stdout": stdout.decode().strip(),
            "stderr": stderr.decode().strip(),
            "exit_code": process.returncode,
        }

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during compilation or execution: {e.stderr.decode()}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup the temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)
