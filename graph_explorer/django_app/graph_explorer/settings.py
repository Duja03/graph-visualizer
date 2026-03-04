"""
Django settings for graph_explorer project.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-change-this-in-production'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'graph_explorer',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'graph_explorer.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / '../../platform/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'graph_explorer.wsgi.application'

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / '../../platform/static']

# Flask API base URL (explorer microservice)
FLASK_API_URL = os.environ.get('FLASK_API_URL', 'http://localhost:5000')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'