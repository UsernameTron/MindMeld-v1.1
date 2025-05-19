import unittest
from typing import Dict, Type

from base import Agent


class TestFunctions(unittest.TestCase):
    def test_register_agent(self):
        """Test register_agent function."""
        name = "test_name"

        result = register_agent(name)
        # TODO: Add appropriate assertions
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
