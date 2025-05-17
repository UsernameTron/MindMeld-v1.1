from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import tempfile
import os
import uuid
import shutil
from pathlib import Path
from typing import Dict, Any, List
import json
import asyncio
import logging

# Import agents
from packages.agents.advanced_reasoning.agents import (
    TestGeneratorAgent, DependencyAgent, CodeAnalyzerAgent,
    CodeDebuggerAgent, CodeRepairAgent, IntegratedCodebaseOptimizer
)

app = FastAPI(title="MindMeld API", version="1.0.0")
logger = logging.getLogger("mindmeld")

# Storage for background tasks
TASK_RESULTS = {}

@app.post("/api/analyze_file")
async def analyze_file(file: UploadFile):
    """Analyze a single file for issues."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    try:
        analyzer = CodeAnalyzerAgent(os.path.dirname(tmp_path))
        content = analyzer.analyze().get(tmp_path)
        debugger = CodeDebuggerAgent()
        diagnostics = debugger.locate_bugs(content)
        return {
            "filename": file.filename,
            "diagnostics": diagnostics,
            "has_issues": "SyntaxError" in diagnostics
        }
    finally:
        os.unlink(tmp_path)

@app.post("/api/repair_file")
async def repair_file(file: UploadFile):
    """Repair a file with syntax errors."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    try:
        analyzer = CodeAnalyzerAgent(os.path.dirname(tmp_path))
        content = analyzer.analyze().get(tmp_path)
        debugger = CodeDebuggerAgent()
        diagnostics = debugger.locate_bugs(content)
        repairer = CodeRepairAgent()
        fixed_content = repairer.generate_fix(content, diagnostics)
        # Write fixed content to a new file for testing
        with tempfile.NamedTemporaryFile(delete=False, suffix="_fixed.py") as fixed_tmp:
            fixed_tmp.write(fixed_content.encode('utf-8'))
            fixed_path = fixed_tmp.name
        # Test if the fix works
        fix_successful = repairer.test_solution(fixed_path)
        os.unlink(fixed_path)
        return {
            "filename": file.filename,
            "original_diagnostics": diagnostics,
            "fixed_content": fixed_content,
            "fix_successful": fix_successful
        }
    finally:
        os.unlink(tmp_path)

@app.post("/api/generate_tests")
async def generate_tests(file: UploadFile, background_tasks: BackgroundTasks):
    """Generate tests for a module (async background task)."""
    task_id = str(uuid.uuid4())
    TASK_RESULTS[task_id] = {"status": "processing"}
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    background_tasks.add_task(
        _generate_tests_background, task_id, tmp_path, file.filename
    )
    return {"task_id": task_id, "status": "processing"}

async def _generate_tests_background(task_id: str, file_path: str, filename: str):
    """Background task for test generation."""
    try:
        generator = TestGeneratorAgent()
        tests = generator.generate_tests(file_path)
        TASK_RESULTS[task_id] = {
            "status": "completed",
            "filename": filename,
            "tests": tests
        }
    except Exception as e:
        logger.exception(f"Error generating tests for {filename}")
        TASK_RESULTS[task_id] = {
            "status": "error",
            "filename": filename,
            "error": str(e)
        }
    finally:
        os.unlink(file_path)

@app.get("/api/task/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of a background task."""
    if task_id not in TASK_RESULTS:
        raise HTTPException(status_code=404, detail="Task not found")
    return TASK_RESULTS[task_id]
