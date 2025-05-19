"""
API service for MindMeld agents.

This module provides a FastAPI REST API for interacting with MindMeld agents.
"""
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import requests
from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE

# Import agent factory
from packages.agents.AgentFactory import AGENT_REGISTRY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path("logs") / f"api_{int(time.time())}.log")
    ]
)
logger = logging.getLogger("mindmeld_api")

# Initialize FastAPI app
app = FastAPI(
    title="MindMeld Agent API",
    description="API for interacting with MindMeld agents",
    version="1.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define models
class AgentRequest(BaseModel):
    """Request model for agent execution."""
    prompt: str = Field(..., description="The input to send to the agent")
    agent_name: str = Field(..., description="The name of the agent to use")
    max_retries: Optional[int] = Field(None, description="Maximum number of retries")
    timeout: Optional[int] = Field(None, description="Timeout in seconds")

class AgentResponse(BaseModel):
    """Response model for agent execution."""
    agent: str = Field(..., description="The name of the agent that processed the request")
    result: Any = Field(..., description="The result from the agent")
    execution_time: float = Field(..., description="Time taken to execute the agent in seconds")
    status: str = Field(..., description="Status of the execution")

class AgentListResponse(BaseModel):
    """Response model for listing available agents."""
    agents: List[str] = Field(..., description="List of available agent names")
    total: int = Field(..., description="Total number of available agents")

class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Health status")
    ollama_status: bool = Field(..., description="Whether Ollama is available")
    version: str = Field(..., description="API version")

# Dependency functions
async def check_ollama_available():
    """Check if Ollama service is available."""
    try:
        # Get Ollama host from environment variable with default
        ollama_url = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception:
        return False

# API routes
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check health status of the API and dependencies."""
    ollama_available = await check_ollama_available()
    
    return {
        "status": "healthy" if ollama_available else "degraded",
        "ollama_status": ollama_available,
        "version": "1.1.0",
    }

@app.get("/agents", response_model=AgentListResponse)
async def list_agents():
    """List all available agents."""
    agents = list(AGENT_REGISTRY.keys())
    
    return {
        "agents": agents,
        "total": len(agents),
    }

@app.post("/agents/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest, background_tasks: BackgroundTasks):
    """Run an agent with the provided prompt."""
    # Check if requested agent exists
    if request.agent_name not in AGENT_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Agent '{request.agent_name}' not found")
    
    # Check if Ollama is available
    ollama_available = await check_ollama_available()
    if not ollama_available:
        raise HTTPException(
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ollama service is not available. Make sure Ollama is running."
        )
    
    try:
        # Create agent
        agent_creator = AGENT_REGISTRY[request.agent_name]
        agent = agent_creator()
        
        # Log request
        logger.info(f"Running agent '{request.agent_name}' with prompt: {request.prompt[:50]}...")
        
        # Run agent
        start_time = time.time()
        result = agent.run(
            request.prompt,
            retries=request.max_retries,
            timeout=request.timeout
        )
        execution_time = time.time() - start_time
        
        # Check for error response
        if isinstance(result, dict) and "error" in result:
            logger.error(f"Agent '{request.agent_name}' failed: {result}")
            return {
                "agent": request.agent_name,
                "result": result,
                "execution_time": execution_time,
                "status": "error"
            }
        
        # Log success
        logger.info(f"Agent '{request.agent_name}' completed in {execution_time:.2f}s")
        
        return {
            "agent": request.agent_name,
            "result": result,
            "execution_time": execution_time,
            "status": "success"
        }
        
    except Exception as e:
        logger.exception(f"Error running agent '{request.agent_name}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error running agent: {str(e)}")


@app.post("/agents/async-run")
async def run_agent_async(request: AgentRequest, background_tasks: BackgroundTasks):
    """Run an agent asynchronously and return a job ID."""
    # This would be expanded with a proper job queue system in production
    # For now, we'll just return a response immediately
    
    # Check if requested agent exists
    if request.agent_name not in AGENT_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Agent '{request.agent_name}' not found")
    
    # Generate a job ID
    job_id = f"job_{int(time.time())}"
    
    # Run this in the background
    background_tasks.add_task(
        run_agent_background,
        job_id,
        request.agent_name,
        request.prompt,
        request.max_retries,
        request.timeout
    )
    
    return {"job_id": job_id, "status": "submitted"}


async def run_agent_background(
    job_id: str,
    agent_name: str,
    prompt: str,
    max_retries: Optional[int] = None,
    timeout: Optional[int] = None
):
    """Run an agent in the background and save results to a file."""
    try:
        # Create agent
        agent_creator = AGENT_REGISTRY[agent_name]
        agent = agent_creator()
        
        # Log job start
        logger.info(f"Started background job {job_id} for agent '{agent_name}'")
        
        # Run agent
        start_time = time.time()
        result = agent.run(prompt, retries=max_retries, timeout=timeout)
        execution_time = time.time() - start_time
        
        # Create output directory if it doesn't exist
        output_dir = Path("outputs") / "jobs"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save result to file
        output_file = output_dir / f"{job_id}.json"
        with open(output_file, "w") as f:
            json.dump({
                "job_id": job_id,
                "agent": agent_name,
                "prompt": prompt,
                "result": result,
                "execution_time": execution_time,
                "status": "error" if isinstance(result, dict) and "error" in result else "success",
                "completed_at": time.time()
            }, f, indent=2)
        
        logger.info(f"Completed background job {job_id} for agent '{agent_name}' in {execution_time:.2f}s")
        
    except Exception as e:
        logger.exception(f"Error in background job {job_id} for agent '{agent_name}': {str(e)}")
        
        # Save error to file
        output_dir = Path("outputs") / "jobs"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"{job_id}.json"
        with open(output_file, "w") as f:
            json.dump({
                "job_id": job_id,
                "agent": agent_name,
                "prompt": prompt,
                "error": str(e),
                "status": "error",
                "completed_at": time.time()
            }, f, indent=2)


@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get the status of an asynchronous job."""
    job_file = Path("outputs") / "jobs" / f"{job_id}.json"
    
    if not job_file.exists():
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    try:
        with open(job_file, "r") as f:
            job_data = json.load(f)
        
        return job_data
    
    except Exception as e:
        logger.exception(f"Error reading job file for {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving job data: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    # Get port from environment or use default
    port = int(os.environ.get("API_PORT", "8000"))
    
    # Run the API server
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=True  # Turn off in production
    )
