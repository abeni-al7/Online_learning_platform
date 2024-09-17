#!/usr/bin/env python3
"""A module for running the Flask app."""
from app import create_app
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
