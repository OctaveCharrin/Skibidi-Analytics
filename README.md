# Skibidi Game Analytics Engine

A Python framework for simulating the Skibidi card game to develop, test, and analyze player strategies.

For a detailed guide on the project's architecture, API, and how to implement new strategies, please see the **[Technical README](./skibidi/README.md)**.

## Quick Setup

1.  **Prerequisites**: Python 3.8+ and a virtual environment.
2.  **Installation**: Clone the repository and install the project in editable mode. This will also install all necessary dependencies.

    ```bash
    git clone https://github.com/OctaveCharrin/Skibidi-Analytics.git
    cd Skibidi-Analytics
    
    # Create and activate a virtual environment (e.g., using venv)
    python -m venv .env
    .\.venv\Scripts\activate  # On Windows
    # source .venv/bin/activate  # On macOS/Linux

    # Install the package from the project root
    pip install -e .
    ```

## Test the game in your shell
Simply run the `main.py` script and follow the instruction to play the game!
```bash
python main.py
```