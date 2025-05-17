"""
File operations utility for MindMeld.

This module provides safe and standardized file I/O operations with proper
context management and error handling.
"""

import hashlib
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from pathlib import Path
from typing import Any, BinaryIO, Dict, Iterator, List, Optional, TextIO, Tuple, Union

from utils.error_handling import FileProcessingError

logger = logging.getLogger(__name__)

# Constants
MAX_FILE_SIZE_KB = 500  # Default maximum file size to process (500KB)
DEFAULT_ENCODING = "utf-8"  # Default file encoding
DEFAULT_ERRORS = "replace"  # Default error handling for encoding issues


def read_file(
    file_path: Union[str, Path],
    encoding: str = DEFAULT_ENCODING,
    errors: str = DEFAULT_ERRORS,
) -> str:
    """
    Read a file safely with proper context management.

    Args:
        file_path: Path to the file
        encoding: File encoding (default: utf-8)
        errors: How to handle encoding errors (default: replace)

    Returns:
        The file contents as a string

    Raises:
        FileProcessingError: If the file cannot be read
    """
    file_path = Path(file_path)
    try:
        with open(file_path, "r", encoding=encoding, errors=errors) as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read file {file_path}: {str(e)}")
        raise FileProcessingError(f"Failed to read file {file_path}: {str(e)}") from e


def write_file(
    file_path: Union[str, Path],
    content: str,
    encoding: str = DEFAULT_ENCODING,
    create_dirs: bool = True,
) -> None:
    """
    Write content to a file safely with proper context management.

    Args:
        file_path: Path to the file
        content: Content to write
        encoding: File encoding (default: utf-8)
        create_dirs: Whether to create parent directories if they don't exist

    Raises:
        FileProcessingError: If the file cannot be written
    """
    file_path = Path(file_path)
    try:
        if create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding=encoding) as f:
            f.write(content)
    except Exception as e:
        logger.error(f"Failed to write to file {file_path}: {str(e)}")
        raise FileProcessingError(
            f"Failed to write to file {file_path}: {str(e)}"
        ) from e


def path_exists(path: Union[str, Path]) -> bool:
    """
    Check if a path exists.

    Args:
        path: Path to check

    Returns:
        True if the path exists, False otherwise
    """
    try:
        return Path(path).exists()
    except Exception as e:
        logger.debug(f"Error checking if path {path} exists: {str(e)}")
        return False


def should_process_file(
    file_path: Union[str, Path],
    max_size_kb: int = MAX_FILE_SIZE_KB,
    extensions: List[str] = None,
) -> bool:
    """
    Check if a file should be processed based on size and extension.

    Args:
        file_path: Path to the file
        max_size_kb: Maximum file size in KB (default: 500KB)
        extensions: List of allowed extensions (default: ['.py'])

    Returns:
        True if the file should be processed, False otherwise
    """
    if extensions is None:
        extensions = [".py"]

    file_path = Path(file_path)

    # Check if file exists
    if not path_exists(file_path):
        logger.debug(f"File {file_path} does not exist, skipping")
        return False

    # Check extension
    if not any(str(file_path).lower().endswith(ext.lower()) for ext in extensions):
        logger.debug(f"File {file_path} has unsupported extension, skipping")
        return False

    # Check size
    try:
        size_kb = file_path.stat().st_size / 1024
        if size_kb > max_size_kb:
            logger.debug(
                f"File {file_path} exceeds size limit ({size_kb:.1f}KB > {max_size_kb}KB), skipping"
            )
            return False
    except Exception as e:
        logger.warning(f"Could not check size of {file_path}: {str(e)}")
        return False

    return True


def find_files(
    directory: Union[str, Path],
    extensions: List[str] = None,
    max_size_kb: int = MAX_FILE_SIZE_KB,
    recursive: bool = True,
) -> List[Path]:
    """
    Find all files in a directory that match the criteria.

    Args:
        directory: Directory to search
        extensions: List of allowed extensions (default: ['.py'])
        max_size_kb: Maximum file size in KB
        recursive: Whether to search recursively

    Returns:
        List of file paths

    Raises:
        FileProcessingError: If the directory cannot be accessed
    """
    if extensions is None:
        extensions = [".py"]

    directory = Path(directory)
    result = []

    try:
        if recursive:
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = Path(root) / file
                    if should_process_file(file_path, max_size_kb, extensions):
                        result.append(file_path)
        else:
            for file in directory.iterdir():
                if file.is_file() and should_process_file(
                    file, max_size_kb, extensions
                ):
                    result.append(file)
    except Exception as e:
        logger.error(f"Error finding files in {directory}: {str(e)}")
        raise FileProcessingError(
            f"Error finding files in {directory}: {str(e)}"
        ) from e

    return result


def process_files_parallel(
    files: List[Path], processor_func: callable, max_workers: int = 10, **kwargs
) -> Dict[Path, Any]:
    """
    Process files in parallel using a thread pool.

    Args:
        files: List of file paths to process
        processor_func: Function to process each file
        max_workers: Maximum number of worker threads
        **kwargs: Additional arguments to pass to the processor function

    Returns:
        Dictionary mapping file paths to processing results
    """
    results = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(processor_func, file, **kwargs): file for file in files
        }

        # Process results as they complete
        for future in as_completed(future_to_file):
            file = future_to_file[future]
            try:
                result = future.result()
                results[file] = result
            except Exception as e:
                logger.error(f"Error processing {file}: {str(e)}")
                results[file] = {"error": str(e)}

    return results


def get_file_hash(file_path: Union[str, Path]) -> str:
    """
    Calculate MD5 hash of file contents.

    Args:
        file_path: Path to the file

    Returns:
        MD5 hash as a hex string

    Raises:
        FileProcessingError: If the file cannot be read
    """
    try:
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        logger.error(f"Failed to calculate hash for {file_path}: {str(e)}")
        raise FileProcessingError(
            f"Failed to calculate hash for {file_path}: {str(e)}"
        ) from e


class ASTCache:
    """
    Cache for Abstract Syntax Trees with LRU eviction policy.
    """

    def __init__(self, max_size: int = 100):
        """
        Initialize the AST cache.

        Args:
            max_size: Maximum number of ASTs to cache
        """
        self.cache = {}
        self.max_size = max_size
        self._get_ast = lru_cache(maxsize=max_size)(self._load_ast)

    def get(self, file_path: Union[str, Path]) -> Any:
        """
        Get the AST for a file, using cache if available.

        Args:
            file_path: Path to the file

        Returns:
            The AST for the file
        """
        file_path = Path(file_path)
        file_hash = get_file_hash(file_path)
        return self._get_ast(str(file_path), file_hash)

    def _load_ast(self, file_path: str, file_hash: str) -> Any:
        """
        Load the AST for a file.

        Args:
            file_path: Path to the file
            file_hash: Hash of the file contents

        Returns:
            The AST for the file
        """
        import ast

        logger.debug(f"AST cache miss for {file_path}, loading")
        source = read_file(file_path)
        return ast.parse(source, filename=file_path)

    def clear(self) -> None:
        """Clear the cache."""
        self._get_ast.cache_clear()


def read_json(
    file_path: Union[str, Path],
    encoding: str = DEFAULT_ENCODING,
    errors: str = DEFAULT_ERRORS,
) -> Dict[str, Any]:
    """
    Read and parse a JSON file safely.

    Args:
        file_path: Path to the JSON file
        encoding: File encoding (default: utf-8)
        errors: How to handle encoding errors (default: replace)

    Returns:
        The parsed JSON data as a dictionary

    Raises:
        FileProcessingError: If the file cannot be read or parsed
    """
    try:
        content = read_file(file_path, encoding, errors)
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from {file_path}: {str(e)}")
        raise FileProcessingError(
            f"Failed to parse JSON from {file_path}: {str(e)}"
        ) from e
    except FileProcessingError:
        # Pass through FileProcessingError
        raise


def write_json(
    file_path: Union[str, Path],
    data: Dict[str, Any],
    encoding: str = DEFAULT_ENCODING,
    indent: int = 2,
    create_dirs: bool = True,
) -> None:
    """
    Write data to a JSON file safely.

    Args:
        file_path: Path to the JSON file
        data: Data to write as JSON
        encoding: File encoding (default: utf-8)
        indent: JSON indentation level (default: 2)
        create_dirs: Whether to create parent directories if they don't exist

    Raises:
        FileProcessingError: If the file cannot be written
    """
    try:
        content = json.dumps(data, indent=indent)
        write_file(file_path, content, encoding, create_dirs)
    except TypeError as e:
        logger.error(f"Failed to serialize data to JSON for {file_path}: {str(e)}")
        raise FileProcessingError(
            f"Failed to serialize data to JSON for {file_path}: {str(e)}"
        ) from e
