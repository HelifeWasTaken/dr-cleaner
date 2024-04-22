# dr-cleaner

This simple docker service is used when you need to clean your registry from time to time due to restrained space on the disk of your host machine, it will simply iterate over all the repositories in the registry and delete the images when the number of images exceeds the limit you set.

## Configuration:
```json
{
    "REGISTRY_URL": "http://localhost:5000",
    "REGISTRY_AUTH": "base64(username:password)",
    "REGISTRY_LIMIT": 10,
    "REGISTRY_CLEANER_INTERVAL": 60
}
```

`REGISTRY_URL`: The URL of the registry you want to clean.
`REGISTRY_AUTH`: The base64 encoded username and password of the registry. (Can be generated by `echo -n "username:password" | base64`)
`REGISTRY_LIMIT`: The limit of the images in the registry. (If the number is -1, the cleaner will not delete any images)
`REGISTRY_CLEANER_INTERVAL`: The interval of the cleaner in seconds.

The configuration file will load an environment variable name `REGISTRY_CLEANER_CONFIG` that contains the path of the configuration file.
If it is not set, the default path will be `/config.json`.

The configuration file can be "hot-reloaded" by waiting for the interval to pass.

## Build:
```
docker build -t dr-cleaner .
```

## Usage:
```
docker run -d -v /path/to/config.json:/config.json dr-cleaner
```

There is no image on docker hub yet