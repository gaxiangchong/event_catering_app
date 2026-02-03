import sys
import os

# ADD YOUR PROJECT PATH HERE
path = '/home/catercompanion/event_catering_app'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables if not using .env
# os.environ['SECRET_KEY'] = 'your-secret-key'

from run import app as application
