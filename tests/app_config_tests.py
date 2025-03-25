import pytest
import yaml
from io import StringIO
from unittest.mock import mock_open, patch

from configuration.app_config import AppConfig, DatabaseConfig, AgentConfig

def test_database_config_defaults():
    db_config = DatabaseConfig(url="sqlite:///test.db")
    assert db_config.url == "sqlite:///test.db"
    assert db_config.echo is False
    assert db_config.pool_size == 5
    assert db_config.max_overflow == 10
    assert db_config.pool_timeout == 30
    assert db_config.pool_recycle == 1800

def test_agent_config_defaults():
    agent_config = AgentConfig(model_provider="openai", model="gpt-3.5-turbo")
    assert agent_config.model_provider == "openai"
    assert agent_config.model == "gpt-3.5-turbo"
    assert agent_config.prompt_version == "v1"
    assert agent_config.cache is False
    assert agent_config.max_tokens == 1000
    assert agent_config.temperature == 0.5
    assert agent_config.tags == []

def test_app_config_load():
    config_yaml = """
    default_model_provider: openai
    database:
      url: sqlite:///test.db
      echo: true
      pool_size: 10
    agents:
      agent1:
        model: gpt-4
        cache: true
        tags: ["tag1", "tag2"]
      agent2:
        model_provider: anthropic
        model: claude-v1
        temperature: 0.7
    """

    with patch("builtins.open", mock_open(read_data=config_yaml)):
        config = AppConfig.load()

    assert config.default_model_provider == "openai"
    
    # Test database config
    assert isinstance(config.db_config, DatabaseConfig)
    assert config.db_config.url == "sqlite:///test.db"
    assert config.db_config.echo is True
    assert config.db_config.pool_size == 10
    
    # Test agent1 config
    agent1 = config.agents["agent1"]
    assert isinstance(agent1, AgentConfig)
    assert agent1.model_provider == "openai"
    assert agent1.model == "gpt-4"
    assert agent1.cache is True
    assert agent1.tags == ["tag1", "tag2"]
    
    # Test agent2 config
    agent2 = config.agents["agent2"]
    assert isinstance(agent2, AgentConfig)
    assert agent2.model_provider == "anthropic"
    assert agent2.model == "claude-v1"
    assert agent2.temperature == 0.7

def test_get_agent_existing():
    config = AppConfig(
        default_model_provider="openai",
        agents={
            "test_agent": AgentConfig(
                model_provider="anthropic",
                model="claude-v1"
            )
        }
    )
    
    agent = config.get_agent("test_agent")
    assert isinstance(agent, AgentConfig)
    assert agent.model_provider == "anthropic"
    assert agent.model == "claude-v1"

def test_get_agent_default():
    config = AppConfig(default_model_provider="openai")
    
    agent = config.get_agent("non_existent_agent")
    assert isinstance(agent, AgentConfig)
    assert agent.model_provider == "openai"
    assert agent.model == "default-model"

def test_empty_config_load():
    empty_config_yaml = """
    default_model_provider: openai
    """

    with patch("builtins.open", mock_open(read_data=empty_config_yaml)):
        config = AppConfig.load()

    assert config.default_model_provider == "openai"
    assert isinstance(config.agents, dict)
    assert len(config.agents) == 0

def test_invalid_yaml():
    invalid_yaml = """
    default_model_provider: openai
    agents:
      - invalid yaml
    """

    with pytest.raises(yaml.YAMLError):
        with patch("builtins.open", mock_open(read_data=invalid_yaml)):
            AppConfig.load()