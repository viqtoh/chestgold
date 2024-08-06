import sys
import os

# Add the project directory to the sys.path
project_home = '/home2/chestgol/chestgold'
if project_home not in sys.path:
    sys.path.append(project_home)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'chestgold.settings'

# Activate the virtual environment
activate_this = '/home2/chestgol/virtualenv/chestgold/3.9/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
