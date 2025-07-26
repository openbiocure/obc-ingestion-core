"""Tests for configuration modules."""

import os
import tempfile

import yaml

from openbiocure_corelib.config.yaml_config import YamlConfig


def test_yaml_config_load():
    """Test loading YAML configuration."""
    # Create test config file
    test_config = {"test_key": "test_value", "nested": {"key": "nested_value"}}

    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="wb", delete=False) as temp:
        yaml.dump(test_config, temp, encoding="utf-8")
        temp_path = temp.name

    try:
        # Load config
        config = YamlConfig()
        config.load(temp_path)

        # Test access
        assert config.get("test_key") == "test_value"
        assert config.get("nested.key") == "nested_value"
        assert config.get("non_existent", "default") == "default"
    finally:
        os.unlink(temp_path)


def test_yaml_config_singleton():
    """Test that YamlConfig uses singleton pattern."""
    config1 = YamlConfig.get_instance()
    config2 = YamlConfig.get_instance()

    assert config1 is config2
