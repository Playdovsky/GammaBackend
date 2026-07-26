# GammaBackend

> 🚀 **Gamma Project** is a CI/CD sandbox built to explore, test, and master GitHub Actions pipelines.

This repository serves as the backend service for the Gamma project (which is split into separate frontend and backend repositories). It acts as a realistic, testable environment designed to simulate real-world modern software development workflows.

---

## 🎯 Project Goals & Case Study

The main objective of GammaBackend is to serve as a practical case study for building a complete CI/CD pipeline from scratch.

Key learning milestones for this project include:
- 🛠️ **Building a CI/CD Pipeline:** Understanding continuous integration and automated testing using **GitHub Actions**.
- 🧪 **Integration Testing:** Designing and running first-ever end-to-end integration tests.
- ⚡ **FastAPI Framework:** First time building asynchronous RESTful APIs with FastAPI.
- 🗄️ **Lightweight Persistence:** Working with SQLite and SQLModel for seamless data access.
- 🧼 **Code Quality & Tooling:** Setting up and using modern linters like **Ruff** for automated code linting and formatting.

---

## 🛠️ Tech Stack & Tooling

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Framework** | [FastAPI](https://fastapi.tiangolo.com/) | High-performance Web API framework |
| **ORM / Data** | [SQLModel](https://sqlmodel.tiangolo.com/) | Type-safe ORM built on SQLAlchemy & Pydantic |
| **Database** | [SQLite3](https://www.sqlite.org/) | Lightweight relational database engine |
| **Testing** | [pytest](https://docs.pytest.org/) | Unit and integration testing suite |
| **Linter & Formatter** | [Ruff](https://docs.astral.sh/ruff/) | Blazing-fast Python linter and code formatter |