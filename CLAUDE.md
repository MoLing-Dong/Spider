# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python web scraping project that contains various spiders for different Chinese websites and services. The project is organized as a collection of independent scraping modules, each targeting specific platforms like:

- Social media platforms (Weibo, Facebook, Douyin)
- E-commerce and automotive sites (Car data, Maoyan)
- Educational platforms (Campus systems, learning platforms)
- Entertainment platforms (NetEase Music, iQiyi)
- News and content aggregation (Hacker News)
- Utility tools (IP detection, proxy management)

## Key Architecture

### Project Structure
- **Main entry point**: `main.py` - Simple hello world script
- **Configuration**: `config.py` + `settings.toml` - Uses Dynaconf for configuration management
- **Dependencies**: Managed via `pyproject.toml` with uv package manager
- **Modular structure**: Each platform/service has its own directory

### Common Patterns
- Most modules use `requests` or `httpx` for HTTP requests
- Async/await pattern is used in newer modules (e.g., `hacknews/main.py`)
- Logging with `loguru` is implemented in several modules
- Sessions and retry logic are used for robust connections
- Data processing often involves CSV/JSON conversion

### Configuration System
The project uses Dynaconf with:
- `settings.toml` for environment-specific configurations
- Environment variables with `DYNACONF_` prefix
- Support for `.secrets.toml` for sensitive data

## Development Commands

### Environment Setup
```bash
# Install dependencies
uv sync

# Or with pip
pip install -r requirements.txt  # Note: requirements.txt not present, use pyproject.toml
```

### Running Individual Modules
```bash
# Run Hacker News scraper
python hacknews/main.py

# Run utility functions
python utils/get_ip.py

# Run any specific spider
python <module_directory>/main.py
```

### Testing
No specific test commands found. Individual modules can be run directly.

## Dependencies

Core dependencies from `pyproject.toml`:
- `httpx` - Modern HTTP client
- `requests` - Traditional HTTP library
- `beautifulsoup4` - HTML parsing
- `loguru` - Logging
- `pycryptodome` - Cryptographic functions
- `fake-useragent` - User agent rotation
- `googlesearch-python` - Google search API

## Important Notes

### Security Considerations
- Some modules contain hardcoded credentials (e.g., `校园网/CampusNetworkBlasting.py`)
- Configuration should be externalized using the Dynaconf system
- Be careful with modules that might test security boundaries

### Module Independence
- Each spider module is largely independent
- Shared utilities are in the `utils/` directory
- Common patterns can be found across modules but aren't always DRY

### Data Handling
- Many modules include data processing utilities
- CSV/JSON conversion is common
- Some modules include data analysis functionality

### Chinese Context
- Many targets are Chinese platforms
- Text processing may require Chinese character handling
- Some modules include Chinese comments and documentation