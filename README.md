# GammaBackend

> 🚀 **Gamma Project** is a CI/CD sandbox built to explore, test, and master GitHub Actions pipelines.

This repository serves as the backend service for the Gamma project (which is split into separate frontend and backend repositories). It acts as a realistic, testable environment designed to simulate real-world modern software development workflows.

---

## 🎯 Project Goals & Case Study

The main objective of GammaBackend is to serve as a practical case study for building a complete CI/CD pipeline from scratch using **GitHub Actions**.

Key learning milestones for this project include:
- 🐋 **Containerization:** Packaging and isolating the FastAPI application, database, and dependencies using Docker.
- ⚙️ **Automated CI/CD Pipeline:** Implementing an end-to-end continuous integration and continuous deployment pipeline using **GitHub Actions**.
- 🛡️ **Dependency Security:** Running dependency vulnerability scans with **pip-audit**.
- 🧪 **Integration & Unit Testing:** Automating test suites with pytest on every workflow run.
- ☁️ **Cloud Deployment:** Automatically building and pushing Docker images to **Google Artifact Registry**, and deploying to **Google Cloud Run**.
- ⚡ **FastAPI Framework:** Building asynchronous RESTful APIs with FastAPI.
- 🗄️ **Lightweight Persistence:** Working with SQLite and SQLModel for seamless data access.
- 🧼 **Code Quality & Tooling:** Setting up and using modern linters like **Ruff** for automated code linting and formatting.

---

## 🔄 CI/CD Pipeline Workflow

The repository utilizes **GitHub Actions** to automate the entire lifecycle from commit to production:

1. 🔍 **Linting:** Code formatting and style enforcement using **Ruff**.
2. 🛡️ **Security Audit:** Scanning Python dependencies for known vulnerabilities via **pip-audit**.
3. 🧪 **Testing:** Executing automated unit and integration tests using **pytest**.
4. 🏗️ **Build & Package:** Building the production Docker image.
5. 📦 **Artifact Registry:** Authenticating with Google Cloud Platform and pushing the container image to **Google Artifact Registry**.
6. 🚀 **Cloud Run Deployment:** Automatically deploying the updated image as a serverless container service on **GCP Cloud Run**.

---

## 🛠️ Tech Stack & Tooling

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Framework** | [FastAPI](https://fastapi.tiangolo.com/) | High-performance Web API framework |
| **ORM / Data** | [SQLModel](https://sqlmodel.tiangolo.com/) | Type-safe ORM built on SQLAlchemy & Pydantic |
| **Database** | [SQLite3](https://www.sqlite.org/) | Lightweight relational database engine |
| **Testing** | [pytest](https://docs.pytest.org/) | Unit and integration testing suite |
| **Linter & Formatter** | [Ruff](https://docs.astral.sh/ruff/) | Blazing-fast Python linter and code formatter |
| **Security Audit** | [pip-audit](https://pypi.org/project/pip-audit/) | Vulnerability scanning for Python packages |
| **CI/CD Platform** | [GitHub Actions](https://github.com/features/actions) | Automated building, testing, and deployment workflows |
| **Containerization** | [Docker](https://www.docker.com/) | Containerized application environment & deployment |
| **Container Registry** | [Google Artifact Registry](https://cloud.google.com/artifact-registry) | Management and storage for Docker container images |
| **Cloud Hosting** | [GCP Cloud Run](https://cloud.google.com/run) | Fully managed serverless container execution platform |