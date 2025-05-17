import time
import functools
import logging
from typing import Callable, Any, Dict, Optional

logger = logging.getLogger("mindmeld")

def retry_on_failure(max_retries: int = 3, 
                    backoff_factor: float = 1.5,
                    fallback_model: Optional[str] = None):
    """Decorator to retry operations with exponential backoff and fallback."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            from exceptions import ModelUnavailableError
            
            metadata = {
                "retries": 0,
                "fallback_used": False,
                "original_model": kwargs.get("model", None)
            }
            
            last_exception = None
            
            # Try with primary model
            for attempt in range(max_retries):
                try:
                    metadata["retries"] = attempt + 1
                    start_time = time.time()
                    result = func(*args, **kwargs)
                    
                    # If result is a dict, add retry metadata
                    if isinstance(result, dict):
                        if "metadata" not in result:
                            result["metadata"] = {}
                        result["metadata"].update(metadata)
                    
                    return result
                
                except Exception as e:
                    last_exception = e
                    wait_time = backoff_factor ** attempt
                    logger.warning(f"Attempt {attempt+1} failed. Retrying in {wait_time:.2f}s: {str(e)}")
                    time.sleep(wait_time)
            
            # If we get here, all attempts failed
            # Try with fallback model if specified
            if fallback_model is not None and "model" in kwargs:
                original_model = kwargs["model"]
                try:
                    logger.info(f"Attempting fallback to {fallback_model}")
                    kwargs["model"] = fallback_model
                    metadata["fallback_used"] = True
                    result = func(*args, **kwargs)
                    
                    # If result is a dict, add retry metadata
                    if isinstance(result, dict):
                        if "metadata" not in result:
                            result["metadata"] = {}
                        result["metadata"].update(metadata)
                    
                    return result
                
                except Exception as fallback_ex:
                    logger.error(f"Fallback to {fallback_model} also failed: {str(fallback_ex)}")
                    # Restore original model in kwargs
                    kwargs["model"] = original_model
            
            # If we reach here, both primary and fallback failed
            # Format error response following the schema
            error_result = {
                "status": "error",
                "error": {
                    "message": str(last_exception),
                    "type": last_exception.__class__.__name__
                },
                "metadata": metadata
            }
            
            return error_result
        
        return wrapper
    
    return decorator
