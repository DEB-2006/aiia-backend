# AIIA Clinical Trial Management System (CTMS) - Backend

The official Python FastAPI backend service for the All India Institute of Ayurveda Clinical Trial Management System.

## 🚀 Key Features
* **RESTful Architecture:** Built with FastAPI for high-performance endpoint handling.
* **Security & Authentication:** OAuth2 implementation with JWT token generation and dependency injection for Role-Based Access Control (Investigator, Admin, Monitor).
* **Database Management:** Serverless PostgreSQL via Neon, managed with SQLAlchemy ORM and Alembic migrations.
* **Strict Data Validation:** Utilizes Pydantic schemas to validate clinical trial metrics, custom dosages, and Ayurvedic variables.

## 🛠️ Tech Stack
* **Framework:** Python, FastAPI, Pydantic
* **Database:** PostgreSQL (Neon), SQLAlchemy, Alembic
* **Authentication:** OAuth2, python-jose (JWT)
* **Hosting:** Render

🔗 *Frontend Repository: https://github.com/DEB-2006/aiia-frontend.git*
