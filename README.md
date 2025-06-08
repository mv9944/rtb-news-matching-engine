RTB News Matching Engine

![alt text](https://img.shields.io/badge/python-3.11+-blue.svg)


![alt text](https://img.shields.io/badge/framework-FastAPI-green.svg)


![alt text](https://img.shields.io/badge/License-MIT-yellow.svg)

This project is a real-time news recommendation system built as a full-stack technical demonstration. It matches a high-throughput stream of incoming articles to a stream of users based on interest overlap, using the Google Gemini LLM for intelligent, real-time semantic tag extraction.

Core Features

Real-time Article Stream (~100 QPS): Simulates a high-frequency feed of news articles on a variety of topics.

Real-time User Stream (~15 QPS): Simulates a stream of active users and their specific interests.

LLM-Powered Tag Extraction: Uses the Google Gemini API to read each article's title and summary and extract a list of relevant semantic tags.

High-Performance Matching: Implements a Jaccard Index scoring algorithm to calculate a normalized match score between article tags and user interests.

Live Dashboard: A simple, dependency-free frontend built with HTML, CSS, and JavaScript that visualizes all three data streams (articles, users, and matches) in real-time using WebSockets.

Containerized & Deployable: Includes a multi-stage Dockerfile for building a lean, production-ready image, designed for easy deployment on platforms like Railway or Render.

Architecture Overview

While implemented as a single FastAPI application for this technical test, the design simulates a production-grade, event-driven architecture.

Backend (app.py): A single, asynchronous FastAPI application serves as the core. It uses asyncio background tasks to run the data generators concurrently.

Real-time Layer (python-socketio): Integrated with FastAPI to manage WebSocket connections and push live updates to the dashboard.

LLM Integration (google-generativeai): A dedicated async function handles all communication with the Google Gemini API, including robust error handling, logging, and a fallback mechanism.

Data Simulation (Faker): The Faker library is used to generate realistic but random article content. To ensure matches can occur, both article and user generation are seeded from a master list of topics.

Tech Stack

Backend: Python 3.11+, FastAPI, Uvicorn

Real-time: Python-SocketIO

LLM: Google Gemini Pro

Frontend: HTML5, CSS3, Vanilla JavaScript (with Socket.IO client)

Containerization: Docker

Deployment: Railway, Render, or any Docker-compatible platform

Getting Started

Follow these instructions to set up and run the project on your local machine.

Prerequisites

Python 3.10+

Git

A Google Gemini API Key. You can get one from Google AI Studio.

Local Development Setup

Clone the repository:

git clone 
cd rtb-news-matching-engine


Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate
# On Windows, use: venv\Scripts\activate
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Install the required dependencies:

pip install -r requirements.txt
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Set up your environment variables:
Create a file named .env in the root of the project directory. Add your API key to this file:

# .env
GOOGLE_API_KEY="your-google-api-key-goes-here"
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
IGNORE_WHEN_COPYING_END

Run the application:

uvicorn app:app_asgi --reload
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

View the dashboard:
Open your web browser and navigate to http://127.0.0.1:8000. You should see the live dashboard.

Docker Deployment

The project includes a Dockerfile for containerized deployment.

Build the Docker image:

docker build -t rtb-news-engine .
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Run the Docker container:
Make sure your .env file is present in the root directory.

docker run -p 8000:8000 --env-file .env rtb-news-engine
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

The application will be accessible at http://localhost:8000.

This project is ready for one-click deployment on modern cloud platforms.

Push your code to a new GitHub repository.

Create a new service on your chosen platform (e.g., Railway, Render).

Connect the service to your GitHub repository. The platform will automatically detect and use the Dockerfile.

In the service's settings, navigate to the "Variables" or "Environment" section.

Add your GOOGLE_API_KEY as a secret environment variable.

The platform will build the image and deploy the application, providing you with a public URL.

Project Structure
rtb-news-matching-engine/
├── .env                # Local environment variables (ignored by Git)
├── .gitignore          # Specifies files for Git to ignore
├── Dockerfile          # Instructions for building the production container
├── README.md           # This file
├── app.py              # The core FastAPI application logic
├── requirements.txt    # Python dependencies
└── static/
    └── index.html      # The frontend dashboard
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
IGNORE_WHEN_COPYING_END
License

This project is licensed under the MIT License. See the LICENSE file for details.