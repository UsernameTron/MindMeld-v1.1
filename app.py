import asyncio
import json
import logging
import os
import shutil
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

# Import agents
from packages.agents.advanced_reasoning.agents import (
    CodeAnalyzerAgent,
    CodeDebuggerAgent,
    CodeRepairAgent,
    DependencyAgent,
    IntegratedCodebaseOptimizer,
    TestGeneratorAgent,
)

# Import agent input types
from packages.agents.AgentFactory import AGENT_INPUT_TYPES
from schema_validator import normalize_agent_output, validate_agent_output

app = FastAPI(title="MindMeld API", version="1.0.0")
logger = logging.getLogger("mindmeld")

# Storage for background tasks
TASK_RESULTS = {}


@app.post("/api/analyze_file")
async def analyze_file(file: UploadFile):
    """Analyze a single file for issues."""
    # Validate file input
    if not file.filename:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "error": {"message": "No file provided", "type": "ValidationError"},
            },
        )

    # Create a job ID for tracing
    job_id = str(uuid.uuid4())
    start_time = time.time()

    with tempfile.NamedTemporaryFile(
        delete=False, suffix=Path(file.filename).suffix
    ) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # Validate that the file exists and is not a directory
        file_path = Path(tmp_path)
        if not file_path.exists():
            return JSONResponse(
                status_code=400,
                content=normalize_agent_output(
                    {"error": f"File not found: {tmp_path}"},
                    "CodeAnalyzerAgent",
                    file.filename,
                    int(time.time()),
                    time.time() - start_time,
                    job_id,
                ),
            )
        if file_path.is_dir():
            return JSONResponse(
                status_code=400,
                content=normalize_agent_output(
                    {"error": f"Expected file but received directory: {tmp_path}"},
                    "CodeAnalyzerAgent",
                    file.filename,
                    int(time.time()),
                    time.time() - start_time,
                    job_id,
                ),
            )

        # Execute the analysis
        analyzer = CodeAnalyzerAgent(os.path.dirname(tmp_path))
        content = analyzer.analyze().get(tmp_path)
        debugger = CodeDebuggerAgent()
        diagnostics = debugger.locate_bugs(content)

        # Normalize the response
        result = {
            "filename": file.filename,
            "diagnostics": diagnostics,
            "has_issues": "SyntaxError" in diagnostics,
        }

        # Return normalized response
        normalized = normalize_agent_output(
            result,
            "CodeAnalyzerAgent",
            file.filename,
            int(time.time()),
            time.time() - start_time,
            job_id,
        )
        return normalized

    except Exception as e:
        logger.exception(f"Error analyzing file {file.filename}")
        error_result = normalize_agent_output(
            {"error": str(e), "type": e.__class__.__name__},
            "CodeAnalyzerAgent",
            file.filename,
            int(time.time()),
            time.time() - start_time,
            job_id,
        )
        return JSONResponse(status_code=500, content=error_result)
    finally:
        os.unlink(tmp_path)


@app.post("/api/repair_file")
async def repair_file(file: UploadFile):
    """Repair a file with syntax errors."""
    # Validate file input
    if not file.filename:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "error": {"message": "No file provided", "type": "ValidationError"},
            },
        )

    # Create a job ID for tracing
    job_id = str(uuid.uuid4())
    start_time = time.time()

    with tempfile.NamedTemporaryFile(
        delete=False, suffix=Path(file.filename).suffix
    ) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # Validate that the file exists and is not a directory
        file_path = Path(tmp_path)
        if not file_path.exists():
            return JSONResponse(
                status_code=400,
                content=normalize_agent_output(
                    {"error": f"File not found: {tmp_path}"},
                    "CodeRepairAgent",
                    file.filename,
                    int(time.time()),
                    time.time() - start_time,
                    job_id,
                ),
            )
        if file_path.is_dir():
            return JSONResponse(
                status_code=400,
                content=normalize_agent_output(
                    {"error": f"Expected file but received directory: {tmp_path}"},
                    "CodeRepairAgent",
                    file.filename,
                    int(time.time()),
                    time.time() - start_time,
                    job_id,
                ),
            )

        analyzer = CodeAnalyzerAgent(os.path.dirname(tmp_path))
        content = analyzer.analyze().get(tmp_path)
        debugger = CodeDebuggerAgent()
        diagnostics = debugger.locate_bugs(content)
        repairer = CodeRepairAgent()
        fixed_content = repairer.generate_fix(content, diagnostics)

        # Write fixed content to a new file for testing
        with tempfile.NamedTemporaryFile(delete=False, suffix="_fixed.py") as fixed_tmp:
            fixed_tmp.write(fixed_content.encode("utf-8"))
            fixed_path = fixed_tmp.name

        # Test if the fix works
        fix_successful = repairer.test_solution(fixed_path)
        os.unlink(fixed_path)

        # Normalize the response
        result = {
            "filename": file.filename,
            "original_diagnostics": diagnostics,
            "fixed_content": fixed_content,
            "fix_successful": fix_successful,
        }

        # Return normalized response
        normalized = normalize_agent_output(
            result,
            "CodeRepairAgent",
            file.filename,
            int(time.time()),
            time.time() - start_time,
            job_id,
        )
        return normalized

    except Exception as e:
        logger.exception(f"Error repairing file {file.filename}")
        error_result = normalize_agent_output(
            {"error": str(e), "type": e.__class__.__name__},
            "CodeRepairAgent",
            file.filename,
            int(time.time()),
            time.time() - start_time,
            job_id,
        )
        return JSONResponse(status_code=500, content=error_result)
    finally:
        os.unlink(tmp_path)


@app.post("/api/generate_tests")
async def generate_tests(file: UploadFile, background_tasks: BackgroundTasks):
    """Generate tests for a module (async background task)."""
    # Validate file input
    if not file.filename:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "error": {"message": "No file provided", "type": "ValidationError"},
            },
        )

    # Create task ID and job ID for tracing
    task_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())
    timestamp = int(time.time())

    # Initialize the task status
    TASK_RESULTS[task_id] = normalize_agent_output(
        {"status": "processing"},
        "TestGeneratorAgent",
        file.filename,
        timestamp,
        0.0,
        job_id,
    )

    with tempfile.NamedTemporaryFile(
        delete=False, suffix=Path(file.filename).suffix
    ) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    # Validate that the file exists and is not a directory
    file_path = Path(tmp_path)
    if not file_path.exists():
        error_result = normalize_agent_output(
            {"error": f"File not found: {tmp_path}"},
            "TestGeneratorAgent",
            file.filename,
            timestamp,
            0.0,
            job_id,
        )
        TASK_RESULTS[task_id] = error_result
        return {"task_id": task_id, "status": "error"}

    if file_path.is_dir():
        error_result = normalize_agent_output(
            {"error": f"Expected file but received directory: {tmp_path}"},
            "TestGeneratorAgent",
            file.filename,
            timestamp,
            0.0,
            job_id,
        )
        TASK_RESULTS[task_id] = error_result
        return {"task_id": task_id, "status": "error"}

    # Start background task with validated input
    background_tasks.add_task(
        _generate_tests_background, task_id, tmp_path, file.filename, job_id
    )

    return {"task_id": task_id, "status": "processing"}


async def _generate_tests_background(
    task_id: str, file_path: str, filename: str, job_id: str
):
    """Background task for test generation."""
    start_time = time.time()
    timestamp = int(start_time)

    try:
        # Check if file type is supported
        if not any(
            file_path.endswith(ext) for ext in [".py", ".js", ".ts", ".jsx", ".tsx"]
        ):
            error_result = normalize_agent_output(
                {"error": f"Unsupported file type: {file_path}"},
                "TestGeneratorAgent",
                filename,
                timestamp,
                time.time() - start_time,
                job_id,
            )
            TASK_RESULTS[task_id] = error_result
            return

        # Execute the generator
        generator = TestGeneratorAgent()
        tests = generator.generate_tests(file_path)

        # Normalize the result
        result = {"filename": filename, "tests": tests}

        normalized = normalize_agent_output(
            result,
            "TestGeneratorAgent",
            filename,
            timestamp,
            time.time() - start_time,
            job_id,
        )
        normalized["status"] = "completed"
        TASK_RESULTS[task_id] = normalized

    except Exception as e:
        logger.exception(f"Error generating tests for {filename}")
        error_result = normalize_agent_output(
            {"error": str(e), "type": e.__class__.__name__},
            "TestGeneratorAgent",
            filename,
            timestamp,
            time.time() - start_time,
            job_id,
        )
        TASK_RESULTS[task_id] = error_result
    finally:
        # Clean up the temporary file
        try:
            os.unlink(file_path)
        except Exception as e:
            logger.warning(f"Could not remove temporary file {file_path}: {e}")


@app.get("/api/task/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of a background task."""
    if task_id not in TASK_RESULTS:
        error_result = normalize_agent_output(
            {"error": "Task not found", "type": "NotFoundError"},
            "TaskService",
            task_id,
            int(time.time()),
            0.0,
            str(uuid.uuid4()),
        )
        return JSONResponse(status_code=404, content=error_result)

    return TASK_RESULTS[task_id]
