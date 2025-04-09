# StudyZed

Backend: Django (Microservices Architecture)  
Frontend: [Frontend Repository](https://github.com/MrLionByte/Frontend---StudyZed-/)

---

## Overview

StudyZed is a modern, modular study management platform designed to streamline academic workflows for both tutors and students. The platform brings together task scheduling, assessment tools, real-time collaboration, and resource management—offering a robust and scalable solution for educational environments.

---

## Future Integration

StudyZed is designed with scalability and personalization in mind. Future iterations of the platform aim to evolve it into a personalized learning ecosystem that caters to individual learning needs.

### Vision Highlights:
- Verified Tutors by StudyZed: Tutors onboarded and authorized by the platform, ensuring quality and credibility.
- 1:1 Personalized Sessions: Enable tutors to manage small cohorts or provide one-on-one guidance tailored to individual student goals.
- Mentorship Framework: Trainers can mentor tutors, and tutors can mentor students—creating a multi-layered, feedback-driven ecosystem.
- Skill & Language Learning Modules: Extend support for professional skills and language acquisition with session tracking and adaptive assessments.
- Growth Monitoring: Real-time dashboards to monitor tutor and student progress across subjects, skills, and timelines.
- Complete Edu-Suite: A comprehensive solution where each student receives individualized learning experiences driven by verified educators and intelligent tools.

StudyZed is not just a tool for managing study routines—it's a platform with the potential to redefine the future of personalized education.

---

## System Architecture

StudyZed follows a microservices architecture, with each service independently developed, deployed, and scaled. Communication between services is event-driven, powered by Apache Kafka. Backend services are containerized using Docker, orchestrated with Kubernetes, and deployed on Google Cloud (GKE).

Each service utilizes Django REST Framework (DRF) for API handling and is integrated with external services for notifications, payments, and real-time communication.

---

## Technical Stack

Core Backend Technologies
- Django + Django REST Framework (DRF)
- Django Channels (WebSocket support)
- Celery + Celery Beat (Task scheduling)
- Docker & Docker Compose
- PostgreSQL (Primary relational database)
- MongoDB (Used for notifications and chat)
- Redis (Caching and Django Channels layer)
- Apache Kafka (Asynchronous microservice communication)
- Firebase Cloud Messaging (FCM) for push notifications
- Stripe (Payment integration)
- Silk (Performance profiling)

---

## Microservices Overview

- User Management Service
  - Authentication (JWT)
  - Role-based access control
  - User profiles and preferences

- Notification Service
  - Real-time and scheduled push notifications
  - Uses FCM and MongoDB

- Payment Service
  - Stripe integration for billing and subscription
  - Secure payment event handling

- Session & Task Management Service
  - Schedule classes, track progress, manage tasks
  - Time management tools for tutors and students

- Message & Video Management Service
  - Real-time messaging and video link management
  - Supports group announcements and collaboration

---

## Monitoring & Observability

- Silk for performance profiling and request tracing
- Django logging system with rotating file handlers
- Kafka monitoring for topic/consumer tracking
- Celery dashboard to track task executions and retries
- Redis monitoring for memory and connection usage
- Planned: Prometheus + Grafana for system-wide observability

---

## CI/CD & Deployment

- GitHub Actions for automated CI/CD:
  - Code linting and quality checks (SonarQube)
  - Docker image build and push to Docker Hub
  - Kubernetes deployment via kubectl rollout
- Deployed on Google Kubernetes Engine (GKE)
- Dynamic image tag management for microservice rollouts

---

## Contact

For any queries or collaboration opportunities, reach out via [LinkedIn](www.linkedin.com/in/farhan-mahmood-n) or open an issue in the repository.