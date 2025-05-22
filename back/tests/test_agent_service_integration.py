"""
Integration tests for the AgentService with DoshaTool and ToolUsageTracker.
"""
import unittest
import json
import os
import time
import sys
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, Mock

# Add the parent directory to the path so we can import from back
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock the database module before importing AgentService
import back.service.database as database

# Mock the database initialization
database.init_db = Mock()
database.get_session = Mock()

# Now import the service with mocked database URL
with patch.dict('os.environ', {'DATABASE_URL': 'sqlite:///:memory:'}):
    from back.service.agent_service import AgentService

from back.service.dosha_tool import DoshaTool
from back.service.tool_usage_tracker import ToolUsageTracker

class TestAgentServiceIntegration(unittest.TestCase):
    """Integration tests for AgentService with DoshaTool and ToolUsageTracker."""
    
    def setUp(self):
        """Set up the test case with a fresh AgentService instance."""
        # Use a test database path
        test_db_path = os.path.join(os.getcwd(), 'test_data', 'test_tool_usage.json')
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(test_db_path), exist_ok=True)
        
        # Clean up any existing test file
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
        # Patch the ToolUsageTracker to use our test path
        self.tracker_patcher = patch(
            'back.service.agent_service.ToolUsageTracker',
            return_value=ToolUsageTracker(storage_path=test_db_path)
        )
        self.mock_tracker = self.tracker_patcher.start()
        
        # Initialize the service with a test user ID
        self.agent_service = AgentService(user_id="test_user")
        self.service = AgentService(user_id="test_user_123")
        
        # Find the DoshaTool instance
        self.dosha_tool = None
        for tool in self.service.tools:
            if isinstance(tool, DoshaTool):
                self.dosha_tool = tool
                break
        
        self.assertIsNotNone(self.dosha_tool, "DoshaTool not found in AgentService tools")
    
    def tearDown(self):
        """Clean up after tests."""
        self.tracker_patcher.stop()
    
    def test_dosha_tool_integration(self):
        """Test that the DoshaTool is properly integrated with AgentService."""
        # Prepare test input
        test_input = {
            "message": "I'm feeling anxious and have trouble sleeping. What's my dosha type?",
            "user_id": "test_user_123"
        }
        
        # Mock the executor to return a test response
        with patch.object(self.service, 'executor') as mock_executor:
            # Configure the mock to return a response that would trigger the DoshaTool
            mock_executor.invoke.return_value = {
                "output": "Based on your symptoms, you might have a Vata imbalance.",
                "intermediate_steps": [
                    (
                        MagicMock(tool="dosha_calculator"),
                        "Vata imbalance detected"
                    )
                ]
            }
            
            # Call the service
            response = self.service.invoke(test_input)
            
            # Verify the response
            self.assertIn("response", response)
            self.assertIn("metrics", response)
            
            # Verify tool usage was tracked
            self.assertIn("dosha_calculator", response["metrics"]["tool_usage"])
    
    def test_tool_usage_tracking(self):
        """Test that tool usage is properly tracked."""
        # Prepare test input
        test_input = {
            "message": "What herbs are good for digestion?",
            "user_id": "test_user_123"
        }
        
        # Mock the executor to return a test response
        with patch.object(self.service, 'executor') as mock_executor:
            # Configure the mock to return a response that would trigger multiple tools
            mock_executor.invoke.return_value = {
                "output": "For digestion, consider ginger, fennel, and peppermint.",
                "intermediate_steps": [
                    (
                        MagicMock(tool="vector_store_search"),
                        "Found information about digestive herbs"
                    ),
                    (
                        MagicMock(tool="herb_recommender"),
                        "Recommended herbs: ginger, fennel, peppermint"
                    )
                ]
            }
            
            # Call the service
            response = self.service.invoke(test_input)
            
            # Verify the response
            self.assertIn("response", response)
            self.assertIn("metrics", response)
            
            # Verify tool usage was tracked
            self.assertIn("vector_store_search", response["metrics"]["tool_usage"])
            self.assertIn("herb_recommender", response["metrics"]["tool_usage"])
            
            # Verify tool stats are included
            self.assertIn("tool_stats", response["metrics"])
            self.assertIn("vector_store_search", response["metrics"]["tool_stats"])
            self.assertIn("herb_recommender", response["metrics"]["tool_stats"])
    
    def test_error_handling(self):
        """Test that errors are properly handled and tracked."""
        # Prepare test input
        test_input = {
            "message": "This will cause an error",
            "user_id": "test_user_123"
        }
        
        # Mock the executor to raise an exception
        with patch.object(self.service, 'executor') as mock_executor:
            mock_executor.invoke.side_effect = Exception("Test error")
            
            # Call the service
            response = self.service.invoke(test_input)
            
            # Verify the error response
            self.assertIn("response", response)
            self.assertIn("error", response)
            self.assertIn("metrics", response)
            
            # Verify the error was tracked
            self.assertTrue(response["metrics"].get("error", False))


if __name__ == "__main__":
    unittest.main()
