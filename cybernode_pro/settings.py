import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-your-key-here'
DEBUG = True

# --- 1. HOST & SECURITY SETTINGS ---
# Yahan '*' aur ngrok dono hain, error ki koi gunjayish nahi
ALLOWED_HOSTS = ['shalelike-cecilia-discifloral.ngrok-free.dev', '127.0.0.1', 'localhost', '*']

# HTTPS/Ngrok ke liye zaroori
CSRF_TRUSTED_ORIGINS = [
    'https://shalelike-cecilia-discifloral.ngrok-free.dev',
    'https://*.ngrok-free.dev'
]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# --- 2. APPS CONFIGURATION ---
INSTALLED_APPS = [
    'daphne',  # Daphne top par hona chahiye real-time chat ke liye
    'chat',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# --- 3. MIDDLEWARE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cybernode_pro.urls'

# --- 4. TEMPLATES ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# --- 5. ASYNC & CHANNELS ---
WSGI_APPLICATION = 'cybernode_pro.wsgi.application'
ASGI_APPLICATION = 'cybernode_pro.asgi.application' 

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# --- 6. DATABASE ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# --- 7. CACHE (Stranger Matching ke liye sabse important) ---
# LocMemCache matching queues ko fast rakhta hai
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# --- 8. AUTH & REDIRECTS ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'login'

# --- 9. STATIC & MEDIA FILES ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'  # India ke time ke hisaab se
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') # Ngrok deployment ke liye zaroori

# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- 10. EXTRA NGROK & SECURITY FIXES ---
# Jab tak DEBUG True hai, ye settings Ngrok par errors nahi aane dengi
if DEBUG:
    CSRF_TRUSTED_ORIGINS = [
        'https://*.ngrok-free.dev',
        'https://shalelike-cecilia-discifloral.ngrok-free.dev',
    ]
    # Secure connection header
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')