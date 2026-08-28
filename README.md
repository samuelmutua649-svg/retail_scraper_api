# Retail Scraper API & Price Analytics Dashboard

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/Node.js-v18%2B-green.svg)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Fastify](https://img.shields.io/badge/Fastify-v4.x-black.svg)](https://www.fastify.io/)
[![Playwright](https://img.shields.io/badge/Playwright-Automated-orange.svg)](https://playwright.dev/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57.svg)](https://www.sqlite.org/)

An end-to-end automated retail price monitoring system designed to extract, store, and analyze product pricing data across major e-commerce platforms (including Jumia and Kilimall). Built with an asynchronous Python scraping engine powered by Playwright, a high-performance Fastify REST API, and an interactive frontend dashboard for historical trend analysis.

---

## 📸 Overview & Features

* **Automated Web Scraping Engine**: Asynchronous crawler built with Python and Playwright, supporting dynamic page rendering, proxy configuration, and resilient DOM extraction.
* **High-Performance API Backend**: Light-weight, fast REST API constructed using Node.js and Fastify, leveraging SQLite (`better-sqlite3`) for persistent price tracking.
* **Analytics Dashboard**: Interactive UI providing price trends, multi-platform comparisons, and product search functionality.
* **Optimized Database Schema**: Normalized relational SQLite design storing product metadata, price history timestamps, and vendor details.
* **Robust Error Handling & Logging**: Retries failed extraction attempts and logs operational events without breaking execution pipelines.

---

## 🏗 System Architecture

```text
  ┌──────────────────────┐         ┌──────────────────────┐
  │  E-Commerce Sites    │         │  Automated Scraper   │
  │  (Jumia / Kilimall)  │ <────── │  (Python + Playwright)│
  └──────────────────────┘         └──────────┬───────────┘
                                              │ Stores extracted data
                                              ▼
  ┌──────────────────────┐         ┌──────────────────────┐
  │  Analytics Dashboard │ <────── │  Fastify API Server  │ <────── [ SQLite DB ]
  │  (React / Vite UI)   │ Requests│  (Node.js + REST)    │
  └──────────────────────┘         └──────────────────────┘
```

---

## 🛠 Tech Stack

* **Scraper Engine**: Python 3.10+, Playwright, Asyncio, BeautifulSoup4
* **Backend API**: Node.js, Fastify, Prisma ORM / `better-sqlite3`
* **Database**: SQLite3
* **Frontend Dashboard**: React, Vite, CSS3, Chart.js / Recharts
* **Version Control**: Git, GitHub

---

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed on your local machine:
* **Node.js** (v18.0.0 or higher)
* **Python** (v3.10 or higher)
* **Git**

---

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/samuelmutua649-svg/retail_scraper_api.git
   cd retail_scraper_api
   ```

2. **Set Up Python Virtual Environment**
   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate environment
   # On Windows (PowerShell):
   .env\Scripts\Activate.ps1
   # On Linux/macOS:
   source venv/bin/activate

   # Install Python dependencies
   pip install -r requirements.txt

   # Install Playwright browser binaries
   playwright install chromium
   ```

3. **Install Node.js Dependencies**
   ```bash
   npm install
   ```

---

## ⚙ Environment Setup

Create a `.env` file in the root directory and configure your settings:

```env
PORT=3000
HOST=0.0.0.0
NODE_ENV=development
DATABASE_URL="file:./data/retail_scraper.db"
HEADLESS=true
SCRAPER_INTERVAL_HOURS=12
```

---

## 🏃 Running the Application

### 1. Execute the Scraper Engine
Run the standalone Python crawler to scrape product listings and save records to SQLite:

```bash
python main.py
```

### 2. Start the API Server
Launch the Fastify API server:

```bash
# Development mode with auto-reload
npm run dev

# Production mode
npm start
```

The API server will be available at `http://localhost:3000`.

### 3. Launch the Analytics Dashboard
Navigate to your dashboard directory (or root frontend entry) and start the Vite development server:

```bash
cd dashboard
npm install
npm run dev
```

---

## 📡 API Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Server health check status |
| `GET` | `/api/products` | Fetch list of tracked products with optional filtering |
| `GET` | `/api/products/:id` | Get detailed product metadata and historical prices |
| `GET` | `/api/analytics/trends` | Fetch price trend metrics for charts |
| `POST`| `/api/scraper/trigger` | Manually trigger scraping pipeline execution |

---

## 📂 Project Structure

```text
retail_scraper_api/
├── api/
│   ├── server.js            # Fastify server entry point
│   ├── routes/              # API endpoints definitions
│   └── controllers/         # Request handling logic
├── scraper/
│   ├── main.py              # Scraper orchestrator script
│   ├── jumia_scraper.py     # Platform-specific extractor
│   └── utils/               # User-agent rotation & DOM parsers
├── dashboard/               # Frontend React application
├── data/                    # Local SQLite database files
├── .gitignore               # Git ignore rules
├── package.json             # Node.js project manifest
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

---

## 🛡 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
