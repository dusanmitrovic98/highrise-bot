# My Flask App

This is a basic Flask application with a well-structured folder layout.

## Setup

1. Create a virtual environment:

    ```sh
    python3 -m venv .venv
    source .venv/bin/activate   # On Windows use `.venv\Scripts\activate`
    ```

2. Install dependencies:

    ```sh
    pip install -r requirements.txt
    ```

3. Set up environment variables:

    ```sh
    cp .env.example .env
    ```

4. Run the application:

    ```sh
    flask run
    ```

## Project Structure

The project follows a modular structure, with separate directories for main application logic and API versions.
