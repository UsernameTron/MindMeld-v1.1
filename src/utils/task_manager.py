import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logger
logger = logging.getLogger("mindmeld.task_manager")


def store_task_result(task_id: str, result: Dict[str, Any]) -> None:
    """
    Store a task result to the file system.

    Args:
        task_id: The unique ID of the task
        result: The result dictionary to store
    """
    try:
        output_dir = Path("outputs") / "jobs"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Prevent division by zero
        if not task_id:
            logger.error("Cannot store task result with empty task_id")
            return

        output_dir = Path("outputs") / "jobs"
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_dir / f"{task_id}.json", "w") as f:
            json.dump(result, f, indent=2)

        logger.debug(f"Stored task result for task_id: {task_id}")
    except Exception as e:
        logger.error(f"Failed to store task result for {task_id}: {str(e)}")
        raise


def get_task_result(task_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a task result from the file system.

    Args:
        task_id: The unique ID of the task

    Returns:
        The task result dictionary or None if not found
    """
    # Prevent division by zero
    if not task_id:
        logger.error("Cannot retrieve task result with empty task_id")
        return None

    job_file = Path("outputs") / "jobs" / f"{task_id}.json"

    if not job_file.exists():
        logger.debug(f"Task result not found for task_id: {task_id}")
        return None

    try:
        with open(job_file, "r") as f:
            result = json.load(f)
        logger.debug(f"Retrieved task result for task_id: {task_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to retrieve task result for {task_id}: {str(e)}")
        return None


def cleanup_old_tasks(max_age_days: int = 7) -> int:
    """
    Clean up task result files older than the specified age.

    Args:
        max_age_days: Maximum age of task files in days

    Returns:
        The number of files deleted
    """
    try:
        # Prevent division by zero
        if max_age_days <= 0:
            logger.warning("Invalid max_age_days value, must be positive integer")
            return 0

        output_dir = Path("outputs") / "jobs"
        if not output_dir.exists():
            return 0

        cutoff_time = datetime.now() - timedelta(days=max_age_days)
        count = 0

        for task_file in output_dir.glob("*.json"):
            # Check file modification time
            file_mod_time = datetime.fromtimestamp(task_file.stat().st_mtime)

            if file_mod_time < cutoff_time:
                task_file.unlink()
                count += 1

        logger.info(f"Cleaned up {count} task files older than {max_age_days} days")
        return count
    except Exception as e:
        logger.error(f"Failed to clean up old task files: {str(e)}")
        return 0


def list_tasks(limit: int = 100, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List the most recent task results, optionally filtered by status.

    Args:
        limit: Maximum number of task results to return
        status: Optional status filter (e.g., "completed", "error", "processing")

    Returns:
        List of task result dictionaries
    """
    # Prevent division by zero
    if limit <= 0:
        logger.warning("Invalid limit value, must be positive integer")
        return []

    try:
        output_dir = Path("outputs") / "jobs"
        if not output_dir.exists():
            return []

        tasks = []

        for task_file in sorted(
            output_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True
        ):
            # Skip if we've reached the limit
            if len(tasks) >= limit:
                break

            try:
                with open(task_file, "r") as f:
                    task_data = json.load(f)

                # Filter by status if specified
                if status is not None:
                    if task_data.get("status") != status:
                        continue

                tasks.append(task_data)
            except Exception as e:
                logger.warning(f"Error reading task file {task_file}: {str(e)}")
                continue

        return tasks
    except Exception as e:
        logger.error(f"Failed to list tasks: {str(e)}")
        return []
