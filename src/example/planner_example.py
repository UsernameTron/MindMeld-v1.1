import json
import logging
import os

from src.agents.core.registry import AgentRegistry
from src.agents.implementations.code_organizer import CodeOrganizerAgent
from src.agents.implementations.planner import PlannerAgent
from src.agents.memory.optimized_vector_memory import OptimizedVectorMemoryAgent
from src.ai.client import LLMClientFactory
from src.ai.embeddings import EmbeddingService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    # Ensure data directories exist
    os.makedirs("./data/vector_memory", exist_ok=True)
    os.makedirs("./data/embeddings", exist_ok=True)
    os.makedirs("./data/storage", exist_ok=True)
    os.makedirs("./data/storage/vector_memory", exist_ok=True)

    # Create LLM client
    llm_client = LLMClientFactory.create_client(
        client_type="ollama", model="codellama"  # Adjust to a model you have in Ollama
    )

    # Create embedding service
    embedding_service = EmbeddingService(
        llm_client=llm_client, cache_dir="./data/embeddings", use_cache=True
    )

    # Create agent registry
    registry = AgentRegistry()

    # Create agents
    vector_memory = OptimizedVectorMemoryAgent(
        storage_path="./data/storage/vector_memory",
        embedding_service=embedding_service,
        llm_client=llm_client,
        use_faiss=True,  # Enable FAISS for faster vector search
        batch_size=5,  # Process embeddings in batches
        max_workers=4,  # Use concurrent processing
    )

    code_organizer = CodeOrganizerAgent(llm_client=llm_client)

    # Register agents
    registry.register(vector_memory)
    registry.register(code_organizer)

    # Create PlannerAgent with registry
    planner = PlannerAgent(registry=registry, llm_client=llm_client)

    # Register PlannerAgent
    registry.register(planner)

    # List all registered agents
    agents = registry.list_agents()
    logger.info(f"Registered agents: {', '.join(agents.keys())}")

    # Sample code knowledge to store in memory
    sample_knowledge = [
        {
            "content": "Python functions should follow the single responsibility principle.",
            "metadata": {"type": "best_practice", "language": "python"},
        },
        {
            "content": "Use meaningful variable names to enhance code readability.",
            "metadata": {"type": "best_practice", "language": "general"},
        },
        {
            "content": "Error handling should be consistent throughout the codebase.",
            "metadata": {"type": "best_practice", "language": "general"},
        },
        {
            "content": (
                "Classes should be designed to be open for extension "
                "but closed for modification (Open-Closed Principle)."
            ),
            "metadata": {"type": "best_practice", "language": "general"},
        },
        {
            "content": "Documentation should explain why something is done, not just what is being done.",
            "metadata": {"type": "best_practice", "language": "general"},
        },
    ]

    # Add knowledge to memory
    for item in sample_knowledge:
        result = registry.dispatch(
            "vector_memory",
            {
                "command": "add",
                "content": item["content"],
                "metadata": item["metadata"],
            },
        )
        logger.info(f"Added memory: {result}")

    # Sample code to analyze and improve
    sample_code = """
def process_data(data):
    # Process the input data
    result = []
    for d in data:
        if d > 0:
            result.append(d * 2)
        else:
            result.append(0)
    return result

def calculate(x, y):
    # Calculate something
    return x * y + x
    """

    # Direct code analysis using CodeOrganizerAgent
    logger.info("\nDirectly analyzing code with CodeOrganizerAgent:")
    analysis_result = registry.dispatch(
        "code_organizer",
        {"command": "analyze", "code": sample_code, "language": "python"},
    )

    logger.info(
        f"Analysis metrics: {json.dumps(analysis_result.get('metrics', {}), indent=2)}"
    )
    issues_count = len(analysis_result.get("issues", []))
    suggestions_count = len(analysis_result.get("suggestions", []))
    logger.info(f"Found {issues_count} issues and {suggestions_count} suggestions")

    # Create a comprehensive plan using PlannerAgent
    logger.info("\nCreating comprehensive plan with PlannerAgent:")
    plan_result = registry.dispatch(
        "planner",
        {
            "command": "create_plan",
            "description": "Analyze, refactor, and document this code according to best practices",
            "context": {
                "code": sample_code,
                "language": "python",
                "requirements": [
                    "Follow Single Responsibility Principle",
                    "Add proper documentation",
                    "Ensure error handling",
                    "Improve code organization",
                ],
            },
        },
    )

    logger.info(f"Created plan: {plan_result}")

    # Get plan status
    if plan_result["status"] == "success":
        plan_id = plan_result["plan_id"]

        status_result = registry.dispatch(
            "planner", {"command": "get_plan_status", "plan_id": plan_id}
        )

        logger.info("Initial plan status:")
        logger.info(f"Name: {status_result.get('name')}")
        logger.info(f"Status: {status_result.get('plan_status')}")
        logger.info(f"Tasks: {len(status_result.get('tasks', []))}")

        # Print the tasks
        for i, task in enumerate(status_result.get("tasks", [])):
            logger.info(f"Task {i+1}: {task['description']} (Agent: {task['agent']})")

        # Execute the plan
        logger.info("\nExecuting plan...")
        execution_result = registry.dispatch(
            "planner", {"command": "execute_plan", "plan_id": plan_id}
        )

        logger.info(
            f"Plan execution completed with status: {execution_result.get('status')}"
        )

        # Show any failed tasks
        if execution_result.get("failed_tasks"):
            logger.info("\nFailed tasks:")
            for task in execution_result.get("failed_tasks"):
                logger.info(f"- {task['description']}: {task['error']}")

        # Get final plan status
        final_status = registry.dispatch(
            "planner", {"command": "get_plan_status", "plan_id": plan_id}
        )

        logger.info("\nFinal plan completion:")
        completed = final_status.get("completion", {}).get("completed")
        total = final_status.get("completion", {}).get("total")
        logger.info(f"Completed: {completed}/{total} tasks")

        # Extract the refactored code from the task results
        refactored_code = None
        for _, result in execution_result.get("task_results", {}).items():
            if result.get("action") == "refactor" and "refactored_code" in result:
                refactored_code = result["refactored_code"]

        # Store the results in vector memory
        if refactored_code:
            logger.info("\nRefactored code:")
            logger.info(refactored_code)

            registry.dispatch(
                "vector_memory",
                {
                    "command": "add",
                    "content": f"Refactored code example:\n{refactored_code}",
                    "metadata": {
                        "type": "refactored_code",
                        "plan_id": plan_id,
                        "description": "Python code refactoring example",
                    },
                },
            )

        # Search memory for related knowledge
        search_result = registry.dispatch(
            "vector_memory",
            {"command": "search", "content": "python code organization best practices"},
        )

        logger.info("\nRelated knowledge from vector memory:")
        for result in search_result.get("results", []):
            logger.info(
                f"- {result['content']} (similarity: {result['similarity']:.4f})"
            )

    else:
        logger.error(f"Failed to create plan: {plan_result.get('message')}")


if __name__ == "__main__":
    main()
