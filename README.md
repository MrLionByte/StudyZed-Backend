# Study-Zed 
### Backend => Build Using Django in Microservice Architecture
### Frontend <a href="https://github.com/MrLionByte/Frontend---StudyZed-/" >GIT</a>

## Overview  
StudyZed is an innovative study management platform that helps tutors and students organize their academic life effectively. The platform combines task management, scheduling, assessment creation, tracking, and resource organization tools to create a comprehensive study environment.

## Architecture Overview
StudyZed is built using a microservices architecture with multiple specialized services communicating through Kafka for event-driven coordination. The system leverages Django's robust framework capabilities while incorporating modern technologies for real-time communication and scalable data management.

## Architecture Overview
StudyZed is built using a microservices architecture with multiple specialized services communicating through Kafka for event-driven coordination. The system leverages Django's robust framework capabilities while incorporating modern technologies for real-time communication and scalable data management.

## Technical Stack
* Django with Django REST Framework (DRF) for RESTful APIs
* Django Channels for WebSocket support
* Docker with docker compose
* Celery with Celery-Beats for task scheduling
* Silk for performance monitoring
* PostgreSQL as the primary database
* MongoDB for notifications and messages
* Redis for caching and channel layer
* Apache Kafka for event-driven communication
* Firebase Cloud Messaging for notification
* Stripe for payment processing

## Backend Services
* User Management Service
* Notification Service
* Payment Service
* Session & Task Management Service
* Message & Video Management Service

## Monitoring and Maintenance
* Use Silk for performance monitoring and debugging
* Implement logging with Django's built-in logging system
* Monitor Kafka topics and consumer groups
* Track Celery task execution and failures
* Monitor Redis memory usage and connection counts
* Set up alerts for critical system events
