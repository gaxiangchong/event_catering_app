# Event Catering App
Flask application for event catering bookings.

## Setup
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Initialize the database:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```
   Or run the helper script (if created):
   ```bash
   python setup_db.py
   ```

## Running
```bash
python run.py
```
App will be available at http://127.0.0.1:5000/
