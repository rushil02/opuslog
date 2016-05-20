from common import *
from user import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# TODO: Distribute settings for production and set environment variables
if DEBUG:
    from dev import *
else:
    from pro import *
