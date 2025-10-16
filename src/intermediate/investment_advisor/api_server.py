import os
import time
from typing import Dict, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from main import (
    analysis_crew,
    financial_crew,
    news_crew,
    run_crew_task,
    run_parallel_execution,
    run_sequential_execution,
    sequential_crew,
)
from pydantic import BaseModel

# FastAPI app initialization
app = FastAPI(
    title="Financial Analysis API",
    description="A FastAPI server for running financial analysis using CrewAI agents",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response
class AnalysisRequest(BaseModel):
    stock: str
    execution_mode: str = "parallel"  # "parallel" or "sequential"


class AnalysisResponse(BaseModel):
    status: str
    message: str
    execution_time: Optional[float] = None
    parallel_time: Optional[float] = None
    analysis_time: Optional[float] = None
    time_saved: Optional[float] = None
    task_id: Optional[str] = None


class TaskStatus(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict] = None
    execution_time: Optional[float] = None
    error: Optional[str] = None


# In-memory storage for task results
task_results = {}


async def run_analysis_background(task_id: str, stock: str, execution_mode: str):
    """Background task to run the analysis."""
    start_time = time.time()
    stock_input = {"stock": stock}

    task_results[task_id] = {
        "status": "running",
        "start_time": start_time,
        "stock": stock,
        "execution_mode": execution_mode,
    }

    if execution_mode == "parallel":
        parallel_time, analysis_time = run_parallel_execution(stock_input)

        end_time = time.time()
        execution_time = end_time - start_time

        # Calculate time savings
        estimated_sequential_time = parallel_time * 2 + analysis_time
        time_saved = estimated_sequential_time - execution_time

        task_results[task_id] = {
            "status": "completed",
            "execution_time": execution_time,
            "parallel_time": parallel_time,
            "analysis_time": analysis_time,
            "time_saved": time_saved,
            "stock": stock,
            "execution_mode": execution_mode,
        }
    else:
        sequential_time, _ = run_sequential_execution(stock_input)

        end_time = time.time()
        execution_time = end_time - start_time

        task_results[task_id] = {
            "status": "completed",
            "execution_time": execution_time,
            "stock": stock,
            "execution_mode": execution_mode,
        }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Financial Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "POST /analyze": "Start financial analysis",
            "GET /status/{task_id}": "Get analysis status",
            "GET /health": "Health check",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": time.time()}


@app.post("/analyze", response_model=AnalysisResponse)
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Start financial analysis for a given stock."""
    # Generate unique task ID
    task_id = f"{request.stock}_{int(time.time())}"

    # Start background task
    background_tasks.add_task(
        run_analysis_background, task_id, request.stock, request.execution_mode
    )

    return AnalysisResponse(
        status="started",
        message=f"Analysis started for {request.stock} in {request.execution_mode} mode",
        task_id=task_id,
    )


@app.get("/status/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Get the status of a running analysis task."""
    task_data = task_results[task_id]

    return TaskStatus(
        task_id=task_id,
        status=task_data["status"],
        result=task_data.get("results"),
        execution_time=task_data.get("execution_time"),
        error=task_data.get("error"),
    )


@app.get("/tasks")
async def list_tasks():
    """List all tasks and their statuses."""
    return {
        "tasks": [
            {
                "task_id": task_id,
                "status": data["status"],
                "stock": data.get("stock"),
                "execution_mode": data.get("execution_mode"),
                "execution_time": data.get("execution_time"),
            }
            for task_id, data in task_results.items()
        ]
    }


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a task from memory."""
    del task_results[task_id]
    return {"message": f"Task {task_id} deleted successfully"}


@app.post("/analyze/sync", response_model=AnalysisResponse)
async def analyze_sync(request: AnalysisRequest):
    """Run financial analysis synchronously (blocking)."""
    start_time = time.time()
    stock_input = {"stock": request.stock}

    if request.execution_mode == "parallel":
        parallel_time, analysis_time = run_parallel_execution(stock_input)

        end_time = time.time()
        execution_time = end_time - start_time

        # Calculate time savings
        estimated_sequential_time = parallel_time * 2 + analysis_time
        time_saved = estimated_sequential_time - execution_time

        return AnalysisResponse(
            status="completed",
            message=f"Analysis completed for {request.stock}",
            execution_time=execution_time,
            parallel_time=parallel_time,
            analysis_time=analysis_time,
            time_saved=time_saved,
        )
    else:
        sequential_time, _ = run_sequential_execution(stock_input)

        end_time = time.time()
        execution_time = end_time - start_time

        return AnalysisResponse(
            status="completed",
            message=f"Analysis completed for {request.stock}",
            execution_time=execution_time,
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
