"""
WSGI config for web_ansible project.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_ansible.settings')

application = get_wsgi_application()

