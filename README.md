# Transaction Processor Application

## Overview

The Transaction Processor Application is designed to process financial transaction data using a stack of services
including PostgreSQL, KeyDB (Redis), RabbitMQ, and a Python application. The application consists of several components:

- **Producer**: Sends random transaction messages to a RabbitMQ queue.
- **Consumer**: Reads messages from RabbitMQ and writes the transaction data to a PostgreSQL database.
- **KeyDB Updater**: Periodically updates KeyDB with the latest balances from the PostgreSQL database.
- **Main Application**: Coordinates the producer, consumer, and KeyDB updater.

## Features

- Consumes messages from RabbitMQ and updates PostgreSQL.
- Periodically updates KeyDB with the latest transaction balances.
- Ensures data consistency and tolerances are within specified limits.

## Requirements

- Docker
- Docker Compose
- Python 3.10+
- psycopg2-binary
- pika
- redis
- python-dotenv

## Getting Started

## Installation and Setup

To build the containers and images for the application, use the following Docker Compose command:

```bash
docker-compose --build
```

To start the application, use the following Docker Compose command:

```bash
docker-compose up
```

## Running Tests

To run tests and generate coverage reports, use the following command:

```bash
 docker-compose run --no-deps app bash -c "coverage run -m pytest app/tests && coverage report"
```

## Pre-commit Checks

Ensure code quality and formatting by running pre-commit checks:

```bash
pre-commit run --all-files
```


# Environment Configuration

### Setting up Environment Variables

For local development, setting up environment variables is necessary. Copy the provided `.env.sample` file to
create your own `.env` file. Update the values according to your configuration.

#### Step 1: Copy the Sample Environment File

Copy the contents of `.env.sample`:

```bash
cp .env.sample .env
```

#### Step 2: Update Environment Variables

Open the newly created .env file and update the values based on your specific configuration.
This file contains essential settings for the Database, RabbitMQ, and other environment-specific variables.

## Create a Virtual Environment

Create and activate a virtual environment using:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

#### Install Requirements

Install the required packages:

```bash
pip install -r requirements.txt
```

## Files

- **docker-compose.yml**: Docker Compose configuration file.
- **Dockerfile**: Docker configuration file for building the service image.
- **requirements.txt**: List of Python dependencies.
- **pre-commit.yml**: Configuration file for pre-commit hooks.
- **.env.sample**: sample for environment variables