# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

db_config = {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'django',
    'USER': 'sergio',
    'PASSWORD': 'SergioAdmin1',
    'HOST': '',
    'PORT': '',
    #    'NAME': 'django_bookings',
    #    'USER': 'django',
    #    'PASSWORD': 'django',
    'OPTIONS': {
                'sql_mode': 'STRICT_TRANS_TABLES',
    },
}
