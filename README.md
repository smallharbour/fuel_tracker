# Fuel Consumption Tracker

A modern web application to track your vehicle's fuel consumption, costs, and efficiency.

## Features

- User authentication (login/register)
- Track fuel consumption entries
- Calculate fuel efficiency (L/100km)
- Visualize consumption trends with charts
- Responsive and modern UI design

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Register a new account or login with existing credentials
2. Add new fuel entries with:
   - Liters of fuel
   - Kilometers driven
   - Cost in euros
3. View your consumption history and statistics
4. Track your vehicle's efficiency over time

## Technologies Used

- Python/Flask
- SQLite Database
- Bootstrap 5
- Chart.js
- Flask-Login
- Flask-SQLAlchemy

## Security Note

This is a development version. For production use:
- Use proper password hashing (e.g., with Werkzeug's `generate_password_hash`)
- Set up proper session management
- Use environment variables for sensitive data
- Implement CSRF protection
- Use HTTPS 