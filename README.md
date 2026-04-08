# Ticket Management System API

This is a backend project built using FastAPI for managing support tickets. It includes authentication, role-based access control, and complete ticket lifecycle management.

The system allows users to create and manage their own tickets, while admins have full access to monitor, assign, and analyze tickets across the system.

---

## Features

* User registration and login
* Secure authentication using JWT tokens
* Password hashing with bcrypt
* Create, update, and delete tickets
* Filter, search, sort, and paginate tickets
* Role-based access (User and Admin)
* Admin dashboard APIs for ticket statistics
* Simple RAG style chatbot

---

## Tech Stack

* Python
* FastAPI
* SQLAlchemy
* SQLite

---

## Setup

1. Install dependencies:

pip install -r requirements.txt

2. Create a `.env` file:

SECRET_KEY=your_secret_key
ALGORITHM=HS256
TOKEN_LIFETIME_MIN=60

3. Run the application:

uvicorn app.main:app --reload

---

## API Documentation

Swagger UI is available at:

http://127.0.0.1:8000/docs

---

## How it Works

1. Register a new user
2. Login to receive an access token
3. Use the token in request headers:

Authorization: Bearer <token>

4. Access protected routes and manage tickets

---

## Notes

* Users can only access and modify their own tickets
* Admins can access and manage all tickets
* Admin role can be assigned manually in the database

---

## Docker Support

docker build -t ticket-app .
docker run -p 8000:8000 ticket-app

---

## Summary

This project demonstrates backend development concepts such as API design, authentication, database handling, and role-based authorization using FastAPI.

---
