# 📄 Financial Document Intelligence Assistant

> An AI-powered financial document processing system that extracts, analyzes, and monitors financial documents using OCR and anomaly detection techniques.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python">
  <img src="https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi">
  <img src="https://img.shields.io/badge/React-18-61DAFB?logo=react">
  <img src="https://img.shields.io/badge/Vite-Build-purple?logo=vite">
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker">
  <img src="https://img.shields.io/badge/License-MIT-yellow">
</p>

---

## 📌 Overview

Financial Document Intelligence Assistant is a full-stack web application that automates financial document processing.

The application extracts text from invoices and receipts using OCR, stores the extracted data, detects anomalies such as duplicate invoices and unusually large transactions, and visualizes insights through an interactive dashboard.

This project demonstrates backend API development, OCR integration, anomaly detection, database management, and frontend dashboard development.

---

# ✨ Features

- 📄 Upload financial documents (PDF, PNG, JPG, TXT)
- 🔍 OCR-based text extraction
- 🧾 Invoice information processing
- 🚩 Duplicate invoice detection
- 📈 Outlier transaction detection
- 📊 Interactive analytics dashboard
- 📉 Spend by category visualization
- 📋 Transaction history table
- 🐳 Docker support
- ⚡ FastAPI REST APIs
- 🎨 Responsive React UI

---

# 🛠 Tech Stack

## Frontend

- React
- Vite
- JavaScript
- CSS

## Backend

- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn

## OCR & Processing

- Tesseract OCR
- Pillow
- pdf2image
- Pandas

## Database

- SQLite

## DevOps

- Docker
- Docker Compose

---

# 📂 Project Structure

```text
Financial-Document-Intelligence-Assistant/
│
├── backend/
│   ├── app/
│   │   ├── anomaly_detection.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── ocr_extract.py
│   │
│   ├── sample_data/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

# 🚀 Getting Started

## 1️⃣ Clone Repository

```bash
git clone https://github.com/khushiYadav-01/Financial-Document-Intelligence-Assistant.git

cd Financial-Document-Intelligence-Assistant
```

---

## 2️⃣ Backend Setup

```bash
cd backend

python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Backend runs on:

```
http://127.0.0.1:8000
```

Swagger API:

```
http://127.0.0.1:8000/docs
```

---

## 3️⃣ Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend:

```
http://localhost:5173
```

---

# 📊 Dashboard

The application provides:

- Total Documents
- Total Value Processed
- Flagged Transactions
- Value at Risk
- Spend by Category
- Anomaly Breakdown
- Transactions Table

---

# 📄 Supported Document Types

- PDF
- PNG
- JPG / JPEG
- TXT

---

# 🔍 OCR Workflow

```
Financial Document
        │
        ▼
OCR Extraction
        │
        ▼
Structured Data
        │
        ▼
Database Storage
        │
        ▼
Anomaly Detection
        │
        ▼
Dashboard Visualization
```

---

# 📸 Screenshots

## Dashboard

> Add your dashboard screenshot here

```
assets/dashboard.png
```

## Upload Panel

```
assets/upload.png
```

## Analytics

```
assets/analytics.png
```

---

# 📈 Future Improvements

- AI-powered invoice classification
- Vendor prediction
- Export reports to PDF
- Authentication & Authorization
- Cloud database support
- Email notifications
- Multi-user support
- Machine Learning fraud detection

---

# 🧪 Sample Data

Sample financial documents are available in

```
backend/sample_data/generated
```

Use these documents to test the application.

---

# 📦 API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Health Check |
| POST | `/upload` | Upload Document |
| GET | `/transactions` | Fetch Transactions |
| GET | `/summary` | Dashboard Summary |

---

# 💡 Skills Demonstrated

- FastAPI
- React
- REST APIs
- OCR
- SQLAlchemy
- Docker
- SQLite
- Data Processing
- Data Visualization
- Full Stack Development

---

# 👩‍💻 Author

**Khushi Yadav**

AI & Machine Learning Enthusiast • Full Stack Developer

GitHub:
https://github.com/khushiYadav-01

---

# ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub!

---
