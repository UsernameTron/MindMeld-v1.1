#!/usr/bin/env python3
"""
wait_for_ollama.py - Waits for Ollama to be ready before proceeding

This script is useful in containerized environments where you need to ensure
Ollama is ready before starting other services. It can also pull models
if they don't exist.
"""

import argparse
import os
import sys
import time
import requests
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description='Wait for Ollama to be ready')
    parser.add_argument('--host', type=str, default=os.environ.get('OLLAMA_HOST', 'http://localhost:11434'),
                        help='Ollama API host (default: http://localhost:11434)')
    parser.add_argument('--timeout', type=int, default=300,
                        help='Maximum time to wait in seconds (default: 300)')
    parser.add_argument('--interval', type=int, default=5,
                        help='Polling interval in seconds (default: 5)')
    parser.add_argument('--models', type=str, nargs='+',
                        help='Models to pull if they don\'t exist')
    return parser.parse_args()

def check_ollama_ready(host):
    """Check if Ollama API is responding"""
    try:
        response = requests.get(f"{host}/api/tags", timeout=10)
        return response.status_code == 200, response.json().get('models', [])
    except Exception as e:
        logger.debug(f"Ollama not ready: {str(e)}")
        return False, []

def pull_model(host, model_name):
    """Pull a model if it doesn't exist"""
    logger.info(f"Pulling model: {model_name}")
    try:
        response = requests.post(
            f"{host}/api/pull",
            json={"name": model_name},
            timeout=600  # Longer timeout for model pulling
        )
        if response.status_code == 200:
            logger.info(f"Successfully pulled model: {model_name}")
            return True
        else:
            logger.error(f"Failed to pull model {model_name}: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error pulling model {model_name}: {str(e)}")
        return False

def main():
    args = parse_args()
    logger.info(f"Waiting for Ollama to be ready at {args.host}")
    
    start_time = time.time()
    while time.time() - start_time < args.timeout:
        ready, models = check_ollama_ready(args.host)
        if ready:
            logger.info(f"Ollama is ready with {len(models)} models")
            
            # Pull requested models if needed
            if args.models:
                existing_models = [m.get('name') for m in models]
                logger.info(f"Existing models: {existing_models}")
                
                for model in args.models:
                    if model not in existing_models:
                        logger.info(f"Model {model} not found, will pull it")
                        if not pull_model(args.host, model):
                            return 1
                    else:
                        logger.info(f"Model {model} already exists")
            
            logger.info("All checks completed successfully")
            return 0
            
        logger.info(f"Ollama not ready yet, retrying in {args.interval}s...")
        time.sleep(args.interval)
    
    logger.error(f"Timed out after {args.timeout}s waiting for Ollama")
    return 1

if __name__ == "__main__":
    sys.exit(main())
