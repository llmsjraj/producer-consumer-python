# RabbitMQ Producer-Consumer Application

## Overview

This application demonstrates a simple RabbitMQ producer-consumer setup using Python and Docker Compose. The producer sends messages to RabbitMQ, and the consumer receives and processes these messages asynchronously.

## Prerequisites

- Docker
- Docker Compose

## Getting Started

1. **Clone the repository:**

```
    git clone https://github.com/llmsjraj/producer-consumer-python.git
    cd <DIRECTORY>
```

2. **Set up environment variables:**

```
    - RABBITMQ_HOST=rabbitmq
    - INTERVAL=5
    - RABBITMQ_QUEUE=task_queue
    - RABBITMQ_DELIVERY_MODE=2
```

3. **Build and run the containers:**

```
    docker-compose up --build
```

4. **View application logs:**
```
    docker-compose logs -f
```

5. **Shutdown the application:**
```
    docker-compose down
```