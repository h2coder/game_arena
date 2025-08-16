# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Game Arena is a Kaggle-hosted platform where LLMs compete in games against each other. This repository contains the harness developed by Google DeepMind that orchestrates the game environment with model calling and parsing.

## Key Architecture Components

### Core System Design
- **Game Environment**: Uses OpenSpiel for game state management and legal move validation
- **Agent Framework**: Generic LLM agent architecture with specialized implementations for different games
- **Model Integration**: Supports both SDK-based and HTTP-based model calling with retry mechanisms
- **Response Parsing**: Multi-stage parsing pipeline with rule-based and LLM-based approaches
- **Sampling Strategies**: Majority voting and "rethinking" strategies to improve move legality

### Main Components
- `agent.py`: Core agent classes including `ChessLLMAgent` and `ChessRethinkAgent`
- `model_generation.py`: Model interface with automatic retry decorators
- `parsers.py`: Move parsing with rule-based and soft-matching approaches
- `samplers.py`: Parallel (majority voting) and sequential (rethinking) sampling
- `prompt_generation.py`: Template-based prompt generation
- `tournament_util.py`: Common utilities for tournaments and model inputs

### Agent Types
- `LLMAgent`: Basic LLM agent with prompt builder and response parser
- `ChessLLMAgent`: Chess-specific agent with fallback to random moves
- `ChessRethinkAgent`: Uses rethink sampling strategy for improved move legality

## Development Commands

### Python Virtual Environment
```bash
source ~/game_arena_venv/bin/activate
```

### Testing
```bash
# Run all tests with unittest
python3 -m unittest discover game_arena/harness -v

# Run specific test file
python3 -m unittest game_arena.harness.agent_test -v

# Run demo (requires API keys)
python3 -m game_arena.harness.harness_demo
```

### Code Quality
```bash
# Lint with pylint
pylint game_arena/harness/

# Format with pyink (Google style)
pyink game_arena/harness/
```

### Environment Setup for Demos
```bash
# Install demo dependencies
python3 -m pip install termcolor

# Set API keys
export GEMINI_API_KEY=your_key
export OPENAI_API_KEY=your_key
```

## Important Patterns

### Model Integration
- Models implement the `Model` protocol with `generate_with_text_input` method
- Automatic retry with exponential backoff is applied via decorator
- Supports both SDK (`model_generation_sdk.py`) and HTTP (`model_generation_http.py`) backends

### Response Parsing Pipeline
- `ChainedMoveParser`: Applies multiple parsers sequentially
- `RuleBasedMoveParser`: Extracts moves using string processing and regex
- `SoftMoveParser`: Matches against legal moves with game-specific logic
- Handles chess notation ambiguities and non-standard formats

### Agent Configuration
- Agents take `observation` and `configuration` mappings
- Return `KaggleSpielActionWithExtras` with submission and metadata
- Support fallback to random moves and call limits

### Game State Handling
- Uses OpenSpiel's `pyspiel.State` for game state representation
- Serializes/deserializes state for Kaggle environment compatibility
- Legal moves obtained via `state.legal_actions()` and `state.action_to_string()`

## Testing Strategy

Tests follow unittest framework and are located alongside source files with `_test.py` suffix.
- run unittest with "python3 -m unittest xx_test.py -v" instead "python3 -m unittest discover game_arena/harness"
- Output the test pass rate and coverage status.

## Dependencies

Key dependencies include:
- `open_spiel`: Game environment and state management
- `anthropic`, `openai`, `google-genai`: LLM SDKs
- `chess`: Chess-specific parsing and validation
- `tenacity`: Retry mechanisms
- `aiohttp`, `requests`: HTTP model calling

## Must rules
- Always activate the python virtaul environment game_arena_venv before python related cmdlets.
- For unittest, always search all test files and run the unittest directly.
- Git commit use my real github account, git ssh key for this device already setup in github profile.