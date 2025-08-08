from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-32_8$a*$t-ppdzfe-5q1@ldzf!79ehe@k5_g0%x#@_(f4dv=1_'

DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'paypal.standard.ipn',
    'counseling',
    'core',
    'ckeditor',
    'django_countries',
    'channels',
    'widget_tweaks',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'counseling.middleware.CounselingAvailabilityMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.approved_projects_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'Main.wsgi.application'
ASGI_APPLICATION = 'Main.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}
# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

# CKEditor
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            {'name': 'document', 'items': ['Source', '-', 'Save', 'NewPage', 'Preview', 'Print']},
            {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord']},
            {'name': 'editing', 'items': ['Find', 'Replace', '-', 'SelectAll']},
            {'name': 'basicstyles', 'items': ['Bold', 'Italic', 'Underline', '-', 'RemoveFormat']},
            {'name': 'paragraph', 'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent']},
            {'name': 'links', 'items': ['Link', 'Unlink']},
            {'name': 'insert', 'items': ['Image', 'Table']},
            {'name': 'styles', 'items': ['Styles', 'Format']},
        ],
        'height': 300,
    }
}

# Jazzmin settings
JAZZMIN_SETTINGS = {
    "site_title": "My Project Admin",
    "site_header": "My Project Administration",
    "site_brand": "My Project",
    "site_logo": "images/favicon/favicon-32x32.png",
    "welcome_sign": "Welcome to My Project Admin",
    "copyright": "Project © 2025",
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "core.BlogPost": "fas fa-newspaper",
        "core.ContactMessage": "fas fa-envelope",
        "core.Subscriber": "fas fa-envelope-open-text",
        "core.Donation": "fa-solid fa-money-bill",
        "core.Event": "fa-solid fa-calendar-check",
        "core.Project": "fa-solid fa-diagram-project",
        "core.ProjectApplication": "fa-solid fa-window-restore",
        "core.Task": "fa-solid fa-window-restore",
        "counseling.Booking": "fa-solid fa-sliders",
        "counseling.CounselingSiteSettings":"fa-solid fa-gear",
        "counseling.CounselingType":"fa-solid fa-user",
        "core": "fas fa-home",
        "sites": "fas fa-globe",
        "flatpages": "fas fa-file-alt",
        "admin": "fas fa-cogs",
        "jazzmin": "fas fa-tachometer-alt",
    },
    "topmenu_links": [
        {"name": "Home", "url": "/", "permissions": ["auth.view_user"]},
        {"model": "auth.User"},
        {"app": "blog"},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "order_with_respect_to": ["auth", "blog", "products", "orders"],
    "theme": "litera",
    "theme_options": {
        "navbar_fixed": True,
        "sidebar_fixed": True,
        "footer_fixed": False,
    }
}

# PayPal
PAYPAL_RECEIVER_EMAIL = 'sb-wtk5f44952286@business.example.com'
PAYPAL_TEST = True

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'infopraivicfarm@gmail.com'
EMAIL_HOST_PASSWORD = 'taxwhticeijcbdsx'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
CONTACT_NOTIFY_EMAIL = 'infopraivicfarm@gmail.com'
ADMIN_EMAIL = 'infopraivicfarm@gmail.com'
# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'paypal.standard.ipn': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Auth
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]


ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
LOGIN_REDIRECT_URL = '/'  # After login
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_ON_GET = True

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#MEDIA_URL = '/media/'
#MEDIA_ROOT = os.path.join(BASE_DIR, 'media')