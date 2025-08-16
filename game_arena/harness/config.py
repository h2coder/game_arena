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

"""Configuration management for LLM settings."""

import dataclasses
import json
import os
from typing import Any, Mapping


@dataclasses.dataclass
class LLMConfig:
  """Configuration for a specific LLM provider."""
  api_key: str | None = None
  base_url: str | None = None


@dataclasses.dataclass
class Config:
  """Main configuration class for all LLM providers."""
  openai: LLMConfig = dataclasses.field(default_factory=LLMConfig)
  anthropic: LLMConfig = dataclasses.field(default_factory=LLMConfig)
  gemini: LLMConfig = dataclasses.field(default_factory=LLMConfig)
  together: LLMConfig = dataclasses.field(default_factory=LLMConfig)
  xai: LLMConfig = dataclasses.field(default_factory=LLMConfig)


def load_config(config_path: str | None = None) -> Config:
  """Load configuration from file or create default config.
  
  Args:
    config_path: Path to config file. If None, checks default locations.
  
  Returns:
    Config object with loaded settings.
  """
  if config_path is None:
    # Check default locations
    home_dir = os.path.expanduser("~")
    default_paths = [
      os.path.join(home_dir, ".game_arena_config.json"),
      os.path.join(os.getcwd(), "game_arena_config.json"),
      os.path.join(os.path.dirname(__file__), "..", "..", "game_arena_config.json"),
    ]
    
    for path in default_paths:
      if os.path.exists(path):
        config_path = path
        break
    else:
      # No config file found, return default config
      return Config()
  
  try:
    with open(config_path, "r") as f:
      config_data = json.load(f)
    
    # Convert dict to Config object
    llm_configs = {}
    for provider in ["openai", "anthropic", "gemini", "together", "xai"]:
      if provider in config_data:
        provider_data = config_data[provider]
        llm_configs[provider] = LLMConfig(
          api_key=provider_data.get("api_key"),
          base_url=provider_data.get("base_url")
        )
      else:
        llm_configs[provider] = LLMConfig()
    
    return Config(
      openai=llm_configs["openai"],
      anthropic=llm_configs["anthropic"],
      gemini=llm_configs["gemini"],
      together=llm_configs["together"],
      xai=llm_configs["xai"]
    )
  except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
    print(f"Warning: Could not load config from {config_path}: {e}")
    return Config()


def get_api_key_with_fallback(
    config_key: str | None,
    env_var: str,
    config: Config | None = None
) -> str | None:
  """Get API key from config or environment variable.
  
  Args:
    config_key: API key from config
    env_var: Environment variable name
    config: Config object (will load if None)
  
  Returns:
    API key string or None if not found
  """
  if config_key is not None:
    return config_key
  
  if config is None:
    config = load_config()
  
  # Check config first, then environment
  if hasattr(config, "openai") and env_var == "OPENAI_API_KEY":
    if config.openai.api_key:
      return config.openai.api_key
  elif hasattr(config, "anthropic") and env_var == "ANTHROPIC_API_KEY":
    if config.anthropic.api_key:
      return config.anthropic.api_key
  elif hasattr(config, "gemini") and env_var == "GOOGLE_API_KEY":
    if config.gemini.api_key:
      return config.gemini.api_key
  elif hasattr(config, "together") and env_var == "TOGETHER_API_KEY":
    if config.together.api_key:
      return config.together.api_key
  elif hasattr(config, "xai") and env_var == "XAI_API_KEY":
    if config.xai.api_key:
      return config.xai.api_key
  
  # Fallback to environment variable
  return os.environ.get(env_var)