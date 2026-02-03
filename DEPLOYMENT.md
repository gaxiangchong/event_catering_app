# Deploying to PythonAnywhere

Follow these steps to deploy your Event Catering App:

## 1. Upload your code
- Zip your project folder (excluding `.venv` and `__pycache__`).
- Upload it to PythonAnywhere via the **Files** tab and unzip it, or `git clone` your repo into the bash console.

## 2. Create a Virtual Environment
Open a **Bash Console** on PythonAnywhere and run:
```bash
cd ~/event_catering_app
mkvirtualenv --python=/usr/bin/python3.10 venv
pip install -r requirements.txt
```

## 3. Set up the Web Tab
1. Go to the **Web** tab on PythonAnywhere.
2. Click **Add a new web app**.
3. Choose **Manual Configuration** (do NOT choose Flask) and select Python 3.10.
4. **Virtualenv**: Enter the path: `/home/catercompanion/.virtualenvs/venv`
5. **Code**: Set "Source code" to `/home/catercompanion/event_catering_app`
6. **WSGI configuration file**: Click the link to edit it. Delete everything and paste the contents of `pythonanywhere_wsgi.py`. 
   - *Replace `YOUR_USERNAME` with your actual PythonAnywhere username.*

## 4. Environment Variables
You have two options:
- **Option A (Recommended)**: Create a `.env` file in `/home/catercompanion/event_catering_app` just like your local one.
- **Option B**: Hardcode them in the WSGI file (see the commented lines in `pythonanywhere_wsgi.py`).

## 5. Initialize Database
In your PythonAnywhere Bash console:
```bash
export FLASK_APP=run.py
flask db upgrade
python create_admin.py  # Create your admin user
```

## 6. Static Files (Crucial for Images/CSS)
In the **Web** tab, scroll down to **Static files** and add:
- **URL**: `/static/`
- **Path**: `/home/catercompanion/event_catering_app/app/static/`

## 7. Reload
Click the big green **Reload** button at the top of the Web tab.

---

## 🔍 Verification & Console "Check-in"
If you want to check your app's status via the **Bash Console**:

### Check the Error Log (Priority #1)
If you see a "500 Internal Server Error", run this to see the traceback:
```bash
tail -n 50 /var/log/catercompanion.pythonanywhere.com.error.log
```

### Verify dependencies and paths
```bash
workon venv
which python
pip list | grep Flask
```

### Test Database health
Check how many events are in your database:
```bash
workon venv
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); from app.models import Event; print(f'Total Events: {Event.query.count()}')"
```

### Check Server Access Logs
See who is visiting your site in real-time:
```bash
tail -f /var/log/catercompanion.pythonanywhere.com.access.log
```
