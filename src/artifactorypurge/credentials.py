import os
from .exceptions import MissingEnvironmentVariable

CREDENTIALS = {
        "artifactory_password": os.getenv('ARTIFACTORY_PASSWORD'),
        "artifactory_username": os.getenv('ARTIFACTORY_USERNAME'),
        "artifactory_url": os.getenv('ARTIFACTORY_URL')
        }

for key in CREDENTIALS:
    if CREDENTIALS[key] == None:
        raise MissingEnvironmentVariable(key.upper())

