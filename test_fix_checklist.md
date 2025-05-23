1. Update test_dependency_management.py and test_test_generator.py
   - Use fixtures or update setUp to include: name, role, api_client

2. Fix executor test expectation to check for "FastAPI" in completion
   - or modify the agent mock output

3. Fix planner test by updating the expected objective string

4. Update mock in test_run_agent_error to return {'status': 'error'}

5. Patch background_tasks in test_async_run_agent
   - Or create a dummy background_tasks.py if needed

6. Optional: Rename classes like TestGeneratorAgent if collected as test cases
