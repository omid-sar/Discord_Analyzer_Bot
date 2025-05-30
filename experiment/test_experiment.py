"""
High-level integration tests for Discord Customer Analyzer Experiment

These tests simulate real user behavior and validate the complete pipeline.
Focus on end-to-end testing rather than unit tests to catch regressions
when LLMs make changes to unrelated parts of the code.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
import json

# Import our experiment modules (will be created)
try:
    from experiment.config import ExperimentConfig
    from experiment.discord_reader import SimpleDiscordReader
    from experiment.claude_analyzer import SimpleClaudeAnalyzer
    from experiment.main_experiment import run_experiment
except ImportError:
    # Modules don't exist yet - that's expected during development
    pass


class TestFullPipeline:
    """Test the complete Discord → Claude → Results pipeline"""
    
    def test_full_pipeline_with_real_apis(self):
        """
        INTEGRATION TEST: Test complete pipeline with real API calls
        This simulates actual user behavior - the most important test
        """
        # Skip if API keys not available (for CI/CD)
        if not os.getenv("DISCORD_BOT_TOKEN") or not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("API keys not available for integration test")
        
        # This test will run the actual experiment
        result = run_experiment()
        
        # Validate the pipeline completed successfully
        assert result is not None
        assert "error" not in str(result).lower()
        
        # Should have found some messages and analysis
        assert "messages" in result
        assert "analysis" in result
        assert len(result["messages"]) > 0
    
    def test_pipeline_error_handling(self):
        """
        INTEGRATION TEST: Ensure pipeline handles errors gracefully
        Prevents regressions when LLMs modify error handling code
        """
        # Test with invalid API keys
        with patch.dict(os.environ, {
            "DISCORD_BOT_TOKEN": "invalid_token",
            "ANTHROPIC_API_KEY": "invalid_key"
        }):
            result = run_experiment()
            
            # Should handle errors gracefully, not crash
            assert result is not None
            # Should indicate what went wrong
            assert "error" in str(result).lower() or "failed" in str(result).lower()


class TestDiscordReader:
    """Test Discord message fetching functionality"""
    
    def test_discord_connection(self):
        """
        INTEGRATION TEST: Verify Discord API connection works
        """
        if not os.getenv("DISCORD_BOT_TOKEN"):
            pytest.skip("Discord token not available")
        
        reader = SimpleDiscordReader()
        
        # Should connect without errors
        connection_result = reader.connect()
        assert connection_result is not False
    
    def test_message_fetching_real_channel(self):
        """
        INTEGRATION TEST: Fetch real messages from Discord
        This validates the actual user workflow
        """
        if not os.getenv("DISCORD_BOT_TOKEN") or not os.getenv("TEST_CHANNEL_ID"):
            pytest.skip("Discord credentials not available")
        
        reader = SimpleDiscordReader()
        reader.connect()
        
        channel_id = os.getenv("TEST_CHANNEL_ID")
        messages = reader.fetch_recent_messages(channel_id, limit=10)
        
        # Should return a list of messages
        assert isinstance(messages, list)
        
        # If there are messages, they should have the right structure
        if messages:
            message = messages[0]
            assert "author" in message
            assert "content" in message
            assert "timestamp" in message
    
    def test_message_data_structure(self):
        """
        INTEGRATION TEST: Validate message data format
        Ensures LLM changes don't break data contracts
        """
        # Mock Discord API response
        with patch('discord.Client') as mock_client:
            mock_message = MagicMock()
            mock_message.author.name = "test_user"
            mock_message.content = "I need help with my startup"
            mock_message.created_at = "2024-01-01T12:00:00"
            
            mock_client.return_value.get_channel.return_value.history.return_value = [mock_message]
            
            reader = SimpleDiscordReader()
            messages = reader.fetch_recent_messages("123", limit=5)
            
            # Validate structure matches our expectations
            assert len(messages) > 0
            message = messages[0]
            assert all(key in message for key in ["author", "content", "timestamp"])


class TestClaudeAnalyzer:
    """Test AI analysis functionality"""
    
    def test_claude_api_connection(self):
        """
        INTEGRATION TEST: Verify Anthropic API works
        """
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("Anthropic API key not available")
        
        analyzer = SimpleClaudeAnalyzer()
        
        # Test with minimal message
        test_messages = [
            {"author": "user1", "content": "I'm looking for a CRM solution", "timestamp": "2024-01-01"}
        ]
        
        result = analyzer.analyze_messages(test_messages)
        
        # Should return structured analysis
        assert result is not None
        assert isinstance(result, dict)
    
    def test_analysis_output_format(self):
        """
        INTEGRATION TEST: Validate Claude returns expected format
        Critical for catching when LLM changes break response parsing
        """
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("Anthropic API key not available")
        
        analyzer = SimpleClaudeAnalyzer()
        
        test_messages = [
            {"author": "customer1", "content": "Anyone know a good project management tool?", "timestamp": "2024-01-01"},
            {"author": "customer2", "content": "I'm frustrated with my current CRM", "timestamp": "2024-01-01"}
        ]
        
        result = analyzer.analyze_messages(test_messages)
        
        # Validate expected keys exist
        expected_keys = ["potential_customers", "key_phrases"]
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"
        
        # Validate data types
        assert isinstance(result["potential_customers"], (int, float))
        assert isinstance(result["key_phrases"], list)


class TestConfiguration:
    """Test configuration and environment setup"""
    
    def test_config_validation_with_missing_keys(self):
        """
        INTEGRATION TEST: Config handles missing environment variables
        """
        with patch.dict(os.environ, {}, clear=True):
            config = ExperimentConfig()
            
            # Should handle missing keys gracefully
            validation_result = config.validate()
            assert validation_result is not None
    
    def test_config_loads_environment_correctly(self):
        """
        INTEGRATION TEST: Config loads real environment variables
        """
        test_env = {
            "DISCORD_BOT_TOKEN": "test_discord_token",
            "ANTHROPIC_API_KEY": "test_anthropic_key",
            "TEST_CHANNEL_ID": "123456789"
        }
        
        with patch.dict(os.environ, test_env):
            config = ExperimentConfig()
            
            assert config.discord_token == "test_discord_token"
            assert config.anthropic_key == "test_anthropic_key"
            assert config.test_channel_id == "123456789"


class TestRegressionPrevention:
    """
    High-level tests specifically designed to catch when LLMs make
    unnecessary changes to unrelated parts of the code
    """
    
    def test_experiment_still_runs_after_changes(self):
        """
        REGRESSION TEST: Ensure experiment still works after any LLM modifications
        This is the most important test - if this fails, we know something broke
        """
        # This test runs the full experiment and ensures it doesn't crash
        # It's designed to catch when LLMs modify unrelated code
        try:
            result = run_experiment()
            # If we get here without exceptions, that's already a success
            assert True
        except Exception as e:
            pytest.fail(f"Experiment crashed after code changes: {e}")
    
    def test_api_interfaces_unchanged(self):
        """
        REGRESSION TEST: Ensure our tool interfaces haven't changed
        """
        # Test that our main classes still exist and have expected methods
        assert hasattr(SimpleDiscordReader, 'connect')
        assert hasattr(SimpleDiscordReader, 'fetch_recent_messages')
        assert hasattr(SimpleClaudeAnalyzer, 'analyze_messages')
        assert hasattr(ExperimentConfig, 'validate')


# Test runner configuration
if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main(["-v", __file__]) 