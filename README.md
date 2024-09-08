# homework-ai-helper

## Overview

`homework-ai-helper` is a web application designed to assist students with their homework by leveraging AI technologies. The application allows users to upload images of their homework questions, which are then processed using OpenAI's API to generate answers. The project is built using Flask for the backend and React for the frontend.

![alt text](<docs/screenshot.png>)

## Features

- **Image Upload**: Users can upload images of their homework questions.
- **AI-Powered Answers**: The application uses OpenAI's API to generate answers based on the uploaded images.
- **Google OAuth**: Users can log in using their Google accounts.
- **Comment System**: Users can post and view comments on questions.

## Project Structure

```
Database configuration
SQLALCHEMY_DATABASE_URI=postgresql://user:password@localhost/dbname

Google OAuth configuration
GOOGLE_CLIENT_ID=your_google_client_id GOOGLE_CLIENT_SECRET=your_google_client_secret

OpenAI API Key
OPENAI_API_KEY=your_openai_api_key

Flask configuration
FLASK_ENV=development FLASK_DEBUG=1

Docker Compose configuration
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=dbname
```

## Run for development
- Backend
```bash
cd backend
pip install -r requirements.txt
python run.py
```

- Frontend
```bash
cd frontend
npm install
npm start dev
```

## Flow migration database.
```
flask db migrate -m "change:table comments"
flask db upgrade
```