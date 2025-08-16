# Copyright 2025 The game_arena Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import tempfile
from unittest import mock

from absl.testing import absltest
from game_arena.harness import config


class ConfigTest(absltest.TestCase):

  def test_llm_config_default_values(self):
    """Test LLMConfig has correct default values."""
    llm_config = config.LLMConfig()
    self.assertIsNone(llm_config.api_key)
    self.assertIsNone(llm_config.base_url)

  def test_llm_config_with_values(self):
    """Test LLMConfig can be initialized with values."""
    llm_config = config.LLMConfig(api_key="test_key", base_url="test_url")
    self.assertEqual(llm_config.api_key, "test_key")
    self.assertEqual(llm_config.base_url, "test_url")

  def test_config_default_values(self):
    """Test Config has correct default LLMConfig instances."""
    cfg = config.Config()
    self.assertIsInstance(cfg.openai, config.LLMConfig)
    self.assertIsInstance(cfg.anthropic, config.LLMConfig)
    self.assertIsInstance(cfg.gemini, config.LLMConfig)
    self.assertIsInstance(cfg.together, config.LLMConfig)
    self.assertIsInstance(cfg.xai, config.LLMConfig)
    self.assertIsNone(cfg.openai.api_key)
    self.assertIsNone(cfg.openai.base_url)

  def test_load_config_no_file(self):
    """Test load_config returns default config when no file exists."""
    cfg = config.load_config("/nonexistent/path.json")
    self.assertIsInstance(cfg, config.Config)
    self.assertIsNone(cfg.openai.api_key)
    self.assertIsNone(cfg.anthropic.api_key)

  def test_load_config_with_valid_file(self):
    """Test load_config loads values from JSON file."""
    config_data = {
        "openai": {
            "api_key": "openai_key",
            "base_url": "openai_url"
        },
        "anthropic": {
            "api_key": "anthropic_key"
        },
        "gemini": {}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
      json.dump(config_data, f)
      temp_path = f.name
    
    try:
      cfg = config.load_config(temp_path)
      self.assertEqual(cfg.openai.api_key, "openai_key")
      self.assertEqual(cfg.openai.base_url, "openai_url")
      self.assertEqual(cfg.anthropic.api_key, "anthropic_key")
      self.assertIsNone(cfg.anthropic.base_url)
      self.assertIsNone(cfg.gemini.api_key)
      self.assertIsNone(cfg.gemini.base_url)
    finally:
      os.unlink(temp_path)

  def test_load_config_with_invalid_json(self):
    """Test load_config handles invalid JSON gracefully."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
      f.write("invalid json content")
      temp_path = f.name
    
    try:
      with mock.patch('builtins.print') as mock_print:
        cfg = config.load_config(temp_path)
        self.assertIsInstance(cfg, config.Config)
        self.assertIsNone(cfg.openai.api_key)
        mock_print.assert_called_once()
        self.assertIn("Could not load config", mock_print.call_args[0][0])
    finally:
      os.unlink(temp_path)

  def test_load_config_with_missing_provider(self):
    """Test load_config handles missing provider in config."""
    config_data = {
        "openai": {
            "api_key": "openai_key"
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
      json.dump(config_data, f)
      temp_path = f.name
    
    try:
      cfg = config.load_config(temp_path)
      self.assertEqual(cfg.openai.api_key, "openai_key")
      self.assertIsNone(cfg.anthropic.api_key)
      self.assertIsNone(cfg.gemini.api_key)
    finally:
      os.unlink(temp_path)

  def test_load_config_default_paths(self):
    """Test load_config checks default paths when no path provided."""
    with mock.patch('os.path.exists') as mock_exists:
      mock_exists.return_value = False
      cfg = config.load_config()
      self.assertIsInstance(cfg, config.Config)
      self.assertIsNone(cfg.openai.api_key)

  @mock.patch('os.path.exists')
  @mock.patch('builtins.open')
  @mock.patch('json.load')
  def test_load_config_finds_default_file(self, mock_json_load, mock_open, mock_exists):
    """Test load_config finds and loads default config file."""
    config_data = {"openai": {"api_key": "default_key"}}
    mock_json_load.return_value = config_data
    
    def exists_side_effect(path):
      return "game_arena_config.json" in path
    
    mock_exists.side_effect = exists_side_effect
    
    cfg = config.load_config()
    self.assertEqual(cfg.openai.api_key, "default_key")

  def test_get_api_key_with_fallback_config_key(self):
    """Test get_api_key_with_fallback returns config_key when provided."""
    result = config.get_api_key_with_fallback("test_key", "OPENAI_API_KEY")
    self.assertEqual(result, "test_key")

  def test_get_api_key_with_fallback_env_var(self):
    """Test get_api_key_with_fallback returns environment variable."""
    with mock.patch('os.environ.get', return_value="env_key"), \
         mock.patch('game_arena.harness.config.load_config') as mock_load_config:
      mock_load_config.return_value = config.Config()
      result = config.get_api_key_with_fallback(None, "OPENAI_API_KEY")
      self.assertEqual(result, "env_key")

  def test_get_api_key_with_fallback_config_provider(self):
    """Test get_api_key_with_fallback returns config provider key."""
    test_config = config.Config()
    test_config.openai.api_key = "config_key"
    
    result = config.get_api_key_with_fallback(None, "OPENAI_API_KEY", test_config)
    self.assertEqual(result, "config_key")

  def test_get_api_key_with_fallback_anthropic(self):
    """Test get_api_key_with_fallback works for Anthropic."""
    test_config = config.Config()
    test_config.anthropic.api_key = "anthropic_key"
    
    result = config.get_api_key_with_fallback(None, "ANTHROPIC_API_KEY", test_config)
    self.assertEqual(result, "anthropic_key")

  def test_get_api_key_with_fallback_gemini(self):
    """Test get_api_key_with_fallback works for Gemini."""
    test_config = config.Config()
    test_config.gemini.api_key = "gemini_key"
    
    result = config.get_api_key_with_fallback(None, "GOOGLE_API_KEY", test_config)
    self.assertEqual(result, "gemini_key")

  def test_get_api_key_with_fallback_together(self):
    """Test get_api_key_with_fallback works for Together."""
    test_config = config.Config()
    test_config.together.api_key = "together_key"
    
    result = config.get_api_key_with_fallback(None, "TOGETHER_API_KEY", test_config)
    self.assertEqual(result, "together_key")

  def test_get_api_key_with_fallback_xai(self):
    """Test get_api_key_with_fallback works for XAI."""
    test_config = config.Config()
    test_config.xai.api_key = "xai_key"
    
    result = config.get_api_key_with_fallback(None, "XAI_API_KEY", test_config)
    self.assertEqual(result, "xai_key")

  def test_get_api_key_with_fallback_none(self):
    """Test get_api_key_with_fallback returns None when no key found."""
    result = config.get_api_key_with_fallback(None, "NONEXISTENT_KEY")
    self.assertIsNone(result)

  @mock.patch('game_arena.harness.config.load_config')
  def test_get_api_key_with_fallback_loads_config(self, mock_load_config):
    """Test get_api_key_with_fallback loads config when not provided."""
    test_config = config.Config()
    test_config.openai.api_key = "loaded_key"
    mock_load_config.return_value = test_config
    
    result = config.get_api_key_with_fallback(None, "OPENAI_API_KEY")
    self.assertEqual(result, "loaded_key")
    mock_load_config.assert_called_once()


if __name__ == '__main__':
  absltest.main()