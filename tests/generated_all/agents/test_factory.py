import unittest
from core.base import Agent

class TestFunctions(unittest.TestCase):
    def test_create_agent(self):
        """Test create_agent function."""
        name = "test_name"

        result = create_agent(name)
        # TODO: Add appropriate assertions
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()