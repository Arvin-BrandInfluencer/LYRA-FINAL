# Lyra: The Backend Analytics Engine

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas">
  <img src="https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" alt="Supabase">
</p>

---

## 📖 Overview

**Lyra** is the computational core of the **Nova analytics platform**.  
It is a robust and scalable backend service built with **Python**, **Flask**, and **Pandas**.  

- Connects to a **Supabase database**  
- Performs **complex data aggregations and calculations**  
- Exposes insights through a **unified REST API**  

Lyra is designed to be the **single source of truth** for all analytical queries from the Nova Slack bot.

---

## 🚀 Key Features

- **Unified API Gateway** → `/api/influencer/query` routes all incoming requests.
- **High-Performance Data Processing** → Efficient in-memory transformations using Pandas.
- **Dynamic KPI Calculation** → Computes CAC, CTR, and other metrics on demand.
- **Multi-Currency Aggregation** → Converts currencies for consolidated regional reports.
- **Performance-Based Tiering** → Ranks influencers into **Gold, Silver, Bronze** tiers.
- **Service-Oriented Architecture** → Clean separation of routes, data access, and processing logic.
- **Test-Driven Development** → Comprehensive `pytest` suite ensures reliability.

---

## 🛠️ Technology Stack

- **Backend Framework**: Flask  
- **Data Manipulation**: Pandas  
- **Database**: Supabase (PostgreSQL)  
- **Logging**: Loguru  
- **Testing**: Pytest, Pytest-Mock  

---

## ⚡ Getting Started

Follow these instructions to set up and run Lyra on your local machine.

### ✅ Prerequisites

- Python **3.9+**
- `pip` & `venv`

---

### 1️⃣ Clone the Repository


git clone https://github.com/Arvin-BrandInfluencer/Lyra-Final.git
cd Lyra-Final


2️⃣ Set up a Virtual Environment
It is highly recommended to use a virtual environment for dependencies.

For Mac
python3 -m venv venv
source venv/bin/activate

For Windows
python -m venv venv
.\venv\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt


4️⃣ Configure Environment Variables
Create a .env file in the root directory with the following:
.env.example

Your Supabase project URL
SUPABASE_URL="https://your-project-ref.supabase.co"

Your Supabase project anon (public) key
SUPABASE_KEY="your-supabase-anon-key"


5️⃣ Run the Application
python run.py
The Lyra API will now be running at:
👉 http://127.0.0.1:10000




