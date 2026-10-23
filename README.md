# Library Resource and Usage Analysis
**BCS714D Assignment 2 | USN 4MW23CS162**

## Stack
Python Flask, PostgreSQL, HTML/CSS/JavaScript and Chart.js.

## Windows setup
1. Install PostgreSQL for Windows from https://www.postgresql.org/download/windows/. Keep port 5432 and remember the password you set for user `postgres`. pgAdmin is recommended.
2. In pgAdmin create a database named `library_analysis`.
3. Open Query Tool for that database and execute `database/schema.sql`, then `database/seed.sql`.
4. In PowerShell, open this project directory and run:
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```
5. Edit `.env` and replace `DB_PASSWORD` with your PostgreSQL password.
6. Start the server: `python backend/app.py`
7. Browse to http://127.0.0.1:5000.

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and activate again. Keep the terminal open while using the app.

## Included features
Dashboard, book catalogue/search/add, student registration, book issue and return, overdue loans, most-borrowed books, category analytics and monthly trends. The data is read from PostgreSQL, not hardcoded into the dashboard.

## Evidence and academic use
Capture genuine screenshots after you install PostgreSQL and run the project. The report draft is separate. Do not claim screenshots or tests were completed before you actually verify them. See `docs/SCREENSHOT_CHECKLIST.md`.
