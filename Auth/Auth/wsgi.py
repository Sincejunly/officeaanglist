"""
WSGI config for Auth project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import asyncio
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Auth.settings')
application = get_wsgi_application()

# asyncio.set_event_loop(asyncio.new_event_loop())
# loop = asyncio.get_event_loop()

# asyncio.ensure_future(redisPool())