# Lyra: The Backend Analytics Engine

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas">
  <img src="https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" alt="Supabase">
</p>

## Overview

Lyra is the computational core of the Nova analytics platform. It is a robust and scalable backend service built with Python, Flask, and Pandas. Its primary function is to connect to a Supabase database, perform complex data aggregations and calculations, and expose these insights through a clean, unified REST API. It is designed to be the single source of truth for all analytical queries from the Nova Slack bot.

## Key Features

- **Unified API Gateway**: A single, powerful endpoint (`/api/influencer/query`) that routes all incoming requests.
- **High-Performance Data Processing**: Leverages the Pandas library for efficient in-memory data manipulation, aggregation, and transformation.
- **Dynamic KPI Calculation**: Computes key metrics on the fly, including Cost Per Acquisition (CAC), Click-Through Rate (CTR), and more.
- **Multi-Currency Aggregation**: Automatically handles currency conversion to provide consolidated reports for multi-market regions like the Nordics.
- **Performance-Based Tiering**: Programmatically ranks influencers into Gold, Silver, and Bronze tiers based on their effective CAC.
- **Service-Oriented Architecture**: Clean separation of concerns between routes, data access, and processing logic.
- **Test-Driven Development**: Includes a comprehensive test suite using `pytest` to ensure code quality and reliability.

## Technology Stack

- **Backend Framework**: Flask
- **Data Manipulation**: Pandas
- **Database**: Supabase (PostgreSQL)
- **Logging**: Loguru
- **Testing**: Pytest, Pytest-Mock

---

## Getting Started

Follow these instructions to set up and run the Lyra backend service on your local machine.

### Prerequisites

- Python 3.9+
- `pip` and `venv`

### 1. Clone the Repository

```bash
git clone https://github.com/Arvin-BrandInfluencer/Lyra-Final.git
cd Lyra-Final
2. Set up a Virtual Environment
It is highly recommended to use a virtual environment to manage dependencies.

code
Bash
# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
3. Install Dependencies
Install all required Python packages from the requirements.txt file.

code
Bash
pip install -r requirements.txt
4. Configure Environment Variables
The application requires a .env file in the root directory to store credentials for the Supabase database. Create a file named .env and populate it with the following variables:

code
Ini
# .env.example

# Your Supabase project URL
SUPABASE_URL="https://your-project-ref.supabase.co"

# Your Supabase project anon (public) key
SUPABASE_KEY="your-supabase-anon-key"

# Optional: Port and Host for the Flask server
# PORT=10000
# HOST="0.0.0.0"
5. Run the Application
Once the dependencies are installed and the environment variables are set, you can start the Flask development server.

code
Bash
python run.py
The Lyra API will now be running, typically at http://127.0.0.1:10000.
