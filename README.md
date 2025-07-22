## About The Project

FinTracker is a web application built with Python and Flask on the backend and a dynamic, responsive frontend using Tailwind CSS and JavaScript. It moves beyond simple expense logging by incorporating advanced visualizations, a financial health score, and a personalized AI coach to help users make smarter financial decisions.

---
## Key Features ✨

* **Interactive Dashboard:** An at-a-glance overview of your financial health, including:
    * Summaries for monthly income, monthly/weekly/daily expenses.
    * A line chart comparing this month's spending to last month's.
    * A doughnut chart breaking down expenses by category.
    * A **Financial Health Score** based on your "Needs vs. Wants" spending.
    * Smart notifications to alert you when you're going overboard.

* **Transaction Management:**
    * Log expenses and income with details like date, category, and payment method.
    * Classify every expense as a **Need** or a **Want**.
    * View and delete entries from your transaction history.

* **Goal Setting & Motivation:**
    * Create custom financial goals with target amounts.
    * Upload a motivational image for each goal.
    * Prioritize goals using an intuitive **drag-and-drop** interface.
    * Choose which goals to feature on your main dashboard.
    * Mark goals as complete to celebrate your achievements.

* **Security & Personalization:**
    * **PIN-Protected Balance:** Your total balance on the dashboard is hidden until you enter a secure 4-digit PIN.
    * **Custom Categories:** Create and delete your own spending categories with optional monthly budgets.

* **AI-Powered Financial Coach 🤖:**
    * An integrated chatbot powered by the **Google Gemini API**.
    * The chatbot has access to your real-time financial data to provide contextual, personalized advice on your spending decisions.

---
## Tech Stack 🛠️

* **Backend:** Python, Flask
* **Database:** SQLite
* **Frontend:** HTML, Tailwind CSS, JavaScript
* **Libraries:** Chart.js, Flatpickr.js, SortableJS
* **AI:** Google Gemini API

---
## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

* Python 3.x installed
* Git installed

### Installation

1.  **Create a `requirements.txt` file.** This is a list of all the Python libraries your project needs. Run this command in your project's terminal:
    ```bash
    pip freeze > requirements.txt
    ```
2.  **Clone the repo**
    ```bash
    git clone [https://github.com/](https://github.com/)[your_username]/[your_repo_name].git
    ```
3.  **Navigate into the project directory**
    ```bash
    cd [your_repo_name]
    ```
4.  **Create and activate a virtual environment**
    ```bash
    # On Windows
    python -m venv venv
    .\venv\Scripts\activate

    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```
5.  **Install Python packages**
    ```bash
    pip install -r requirements.txt
    ```
6.  **Set up your environment variables**
    * Create a file named `.env` in the root of the project.
    * Add your Google Gemini API key to it:
        ```
        GOOGLE_API_KEY=YOUR_API_KEY_HERE
        ```
7.  **Initialize the database**
    ```bash
    flask --app app init-db
    ```
8.  **Set your security PIN** (replace `1234` with your PIN)
    ```bash
    flask --app app set-pin 1234
    ```
9.  **Run the application**
    ```bash
    flask --app app run
    ```
The application will be available at `http://127.0.0.1:5000`.
