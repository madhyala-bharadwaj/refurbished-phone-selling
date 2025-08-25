# PhoneDash: Refurbished Phone Inventory Management System

## 1. Overview

**PhoneDash** is a robust, full-stack web application designed to manage and simulate the selling of refurbished phones across multiple e-commerce platforms (X, Y, and Z). It provides a professional, feature-rich dashboard for handling complex inventory, platform-specific pricing, and condition categorization.

This project was built to solve key challenges in the refurbished electronics market, such as preventing unprofitable listings due to high fees, managing stock levels accurately, and translating internal product conditions to platform-specific standards.

---

## 2. Key Features

* **📊 Interactive Analytics Dashboard:** Get a real-time overview of your inventory with charts for stock distribution by brand and condition, and KPIs for total inventory value.
* **📦 Comprehensive Inventory Management:** Full CRUD (Create, Read, Update, Delete) functionality for your phone stock.
* **📑 Bulk Data Management:** Effortlessly add hundreds of phones at once using the CSV bulk upload feature.
* **🔍 Advanced Search & Filtering:** Instantly filter the entire inventory by brand, condition, or platform. The dashboard analytics dynamically update to reflect your filters.
* **⚙️ Platform-Specific Logic:**
    * **Automated Pricing:** Prices are automatically calculated for each platform based on their unique fee structures (e.g., X: 10% fee, Y: 8% + $2).
    * **Condition Mapping:** Internal conditions (e.g., "Excellent") are automatically translated to platform-specific categories (e.g., "3 stars (Excellent)").
    * **Profitability Checks:** The system prevents listing phones that would be unprofitable due to high platform fees.
* **🖱️ Efficient Bulk Actions:** List all filtered phones onto a specific platform with a single click.
* **📝 Action Audit Log:** A running log of all significant actions (create, update, delete, list) for full traceability.
* **🔐 Secure by Design:** The backend features mock authentication to protect sensitive endpoints and uses Pydantic for rigorous data validation.

---

## 3. Technology Stack

This application is built with a modern, professional technology stack chosen for performance, scalability, and maintainability.

* **Backend:** **Python 3.11+** with the **FastAPI** framework for its high performance and automatic API documentation.
* **Frontend:** Vanilla **HTML5**, **CSS3**, and **JavaScript (ES6+)** with **Tailwind CSS** for rapid, professional UI development.
* **Data Visualization:** **Chart.js** for creating interactive and responsive dashboard charts.
* **Data Handling:** **Pandas** for robust and efficient CSV parsing.
* **Server:** **Uvicorn** server.

---

## 4. Professional Architecture

The project is built on a modular, decoupled architecture that separates concerns, making it highly maintainable and scalable.

* **Backend (Python/FastAPI):**
    * **`main.py`:** API router and entry point.
    * **`services.py`:** Contains all core business logic, acting as an intermediary between the API and the database.
    * **`models.py`:** Pydantic models for strict data validation and schema definition.
    * **`utils.py`:** Helper functions for isolated tasks like price calculation and condition mapping.
    * **`database.py`:** Abstracted data persistence layer (currently JSON, easily swappable for a SQL/NoSQL database).
    * **`security.py`:** Handles authentication logic.
* **Frontend (JavaScript):**
    * **Multi-Page Application (MPA):** A dedicated `login.html` page ensures a robust separation between authentication and the main application (`app.html`).
    * **Modular JS:** The `main.js` file is structured with clear modules for API communication, UI rendering, and state management.

---

## 5. Setup and Installation

To get the project running locally, please follow these steps.

### Prerequisites
* Python 3.7+
* `pip` (Python package installer)

### Installation
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/madhyala-bharadwaj/refurbished-phone-selling/
    cd refurbished_phone_selling
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required Python packages:**
    ```bash
    pip install "fastapi[all]" pandas jinja2
    ```

---

## 6. How to Run the Application

1.  **Start the Backend Server:**
    Navigate to the project's root directory in your terminal and run:
    ```bash
    uvicorn main:app --reload
    ```
    The server will start on `http://localhost:8000`.

2.  **Access the Application:**
    Open your web browser and go to the following address:
    ```
    http://localhost:8000
    ```

3.  **Login:**
    You will be greeted by the login page. Click the **"Login as Admin"** button to access the main dashboard. The application uses mock credentials (`admin`/`password`) handled by the backend.


