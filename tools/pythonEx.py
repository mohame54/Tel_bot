from .base import BaseTool
from typing import List, Optional
import io
import sys
import threading
from . import (
    PYTHON_EX_DOC,
    add_docstring
)


def _run_placeHolder(
    code_str:str,
    output_list: List[str],
    error_list: List[str],
):
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()

    try:
        exec(code_str)
        # Store the output and errors in the provided lists
        output_list.append(sys.stdout.getvalue())
        error_list.append(sys.stderr.getvalue())
    except Exception as e:
        # Capture any exceptions and their traceback
        error_list.append(str(e))
        error_list.append(sys.stderr.getvalue())
    finally:
        # Reset stdout and stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr



class PythonEx(BaseTool):
    def __init__(
        self,
        tool_name:Optional[str] = None,
        description: str | None = "Python Code Excution"
    ):
        super().__init__(description)
        self.tool_name = "PythonEx" if tool_name is None else tool_name


    def _run(self, code_str:str) -> str:
        outputs = []
        errors = []
        # Create a thread to run the code string
        code_thread = threading.Thread(
            target=_run_placeHolder, args=(code_str, outputs, errors)
        )

        code_thread.start()

        code_thread.join()

        captured_output = outputs[0] if outputs else ""
        if captured_output:
            return f"\nOutput: \n{captured_output}"
        captured_errors = errors[0] if errors else "" 
        return f"\n Error: \n{captured_errors}"
    
    def _parse_code(self, code: str) -> str:

        if isinstance(code, list):
            code = "\n".join(code)

        code = code.strip()
        
        if code.startswith("```") and code.endswith("```"):
            lines = code.splitlines()
            if lines[0].strip().startswith("```") and lines[-1].strip().startswith("```"):
                code = "\n".join(lines[1:-1])
            else:
                code = code[3:-3].strip()

        if ";" in code:
            code = code.replace(";", "\n")
        
        return str(code)
    
    add_docstring(PYTHON_EX_DOC)
    def __call__(self, code_str: str) -> str:
        code_str = self._parse_code(code_str)
        return self._run(code_str)
