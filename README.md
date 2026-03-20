# Gemini CLI Project

This project provides a CLI interface for interacting with the Gemini API.

## Project Structure
- `main.py`: Entry point for the CLI application.
- `api_client.py`: Module for handling API requests.
- `formatter.py`: Module for formatting API responses.
- `tests/`: Directory containing project tests.
- `conductor/`: Project management and workflow documentation.

## Getting Started
To install dependencies and set up the environment, run:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the Application
```bash
python3 main.py --help
```

## Running Tests
```bash
pytest
```
