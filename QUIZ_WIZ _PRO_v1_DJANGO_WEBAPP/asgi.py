"""
ASGI config for QUIZ_WIZ _PRO_v1_DJANGO_WEBAPP project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QUIZ_WIZ _PRO_v1_DJANGO_WEBAPP.settings')

application = get_asgi_application()
