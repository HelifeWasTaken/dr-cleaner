import docker
from sys import exit
from time import sleep
from json import load as json_load
from json import dumps as json_dumps
from os import path
from os import getenv
from base64 import b64decode

class DockerRegistryCleaner:

    FIELDS = ['REGISTRY_URL', 'REGISTRY_AUTH', 'REGISTRY_LIMIT', 'REGISTRY_INTERVAL']

    def _config_check(self):
        if self.config is None:
            raise Exception('Config not loaded')

        for field in DockerRegistryCleaner.FIELDS:
            if field not in self.config:
                raise Exception(f'{field} not found in config file')

        if self.config['REGISTRY_LIMIT'] <= 0 and self.config['REGISTRY_LIMIT'] != -1:
            raise Exception('Invalid limit set -1 (do nothing) or >= 1 (limit to 1)')
        if self.config['REGISTRY_INTERVAL'] < 60:
            raise Exception('Interval too short (minimum 60 seconds)')

        for valid_fields in self.config.keys():
            if valid_fields not in DockerRegistryCleaner.FIELDS:
                print(f'Warning: {valid_fields} is not a valid field in the config file (may present a typo or security issue)')
                exit(1)

    # reloads the config file if it has been modified
    def _load_config(self):
        if self.config is not None:
            if path.getmtime(self.config_path) <= self.last_file_timestamp:
                return
        print('Loading configuration file:', self.config_path)
        with open(self.config_path, 'r') as f:
            self.config = json_load(f)
            self.last_file_timestamp = path.getmtime(self.config_path)
        self._config_check()
        if self.client is not None:
            self.client.close()
            self.client = None
        self._connect() # reconnect to docker if the config has changed (new credentials)

    def _connect(self):
        try:
            print('Connecting to docker')

            # decode the registry auth
            registry_password, registry_user = None, None
            try:
                registry_user, registry_password = b64decode(self.config['REGISTRY_AUTH']).decode().split(':')
            except:
                print('Error decoding the registry auth field. Check if it is base64 encoded it must be in the format base64(user:password)')
                print('It can be generated with echo -n "user:password" | base64')
                exit(1)

            self.client = docker.DockerClient(base_url=self.config['REGISTRY_URL'])
            self.client.login(username=registry_user, password=registry_password)
            print('Connected to docker')
        except:
            print('Error connecting to docker with the provided credentials')
            self.config['REGISTRY_AUTH'] = '<redacted>'
            print(json_dumps(self.config, indent=4))
            exit(1)

    def __init__(self, config_path):
        self.config = None
        self.config_path = config_path
        self._load_config()

    def _run(self):
        print('Running cleaner')

        for repository in self.client.repositories.list():
            print(f'Cleaning {repository.name}')
            images = repository.images.list()
            images.sort(key=lambda x: x.attrs['Created'])
            for image in images[:-self.config['REGISTRY_LIMIT']]:
                print(f'Deleting {image.tags[0]}')
                image.remove()

        print('Finished cleaning')

    def run(self):
        while True:
            self._run()
            sleep(self.config['REGISTRY_INTERVAL'])
            self._load_config()

if __name__ == '__main__':
    DockerRegistryCleaner(getenv('REGISTRY_CLEANER_CONFIG', '/config.json')).run()