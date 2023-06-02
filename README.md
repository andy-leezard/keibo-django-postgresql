# Initialize


## Using Docker

Assuming all docker-related configuration on OS level is complete, run following commands.

Create and start containers of all services defined in `docker-compose.yml`
```
docker-compose up
```

If you are attempting to re-build
```
docker-compose build --no-cache
docker-compose up
```
or
```
docker-compose up --build
```

Migrate
```
docker-compose exec web python manage.py migrate
```

Create Superuser
```
docker-compose exec web python manage.py createsuperuser
```

## Troubleshooting database related problems

When removing containers, do not forget to remove the volumes as well.
Warning: this will erase all databases
```
docker-compose down --volumes
```

### Developing in the Dev Container

1. Assuming the VS extension `Remote Development` (pack of 4 extensions including Dev Containers) is installed, open the tab on the left side called `Remote Explorer` and select the container. Open (attach) in a new window.

2. In the new remote VS Code window, reinstall `Gitlens` and `Python`.

3. Configure the carriage-return git settings for Linux by running the following command and refresh the `Source Control` tab, this will resolve the all files showing as modified files:
```
git config --global core.autocrlf input
```

Check if all is good (the result should be `input`)
```
git config --global --get core.autocrlf
```

### Checking logs

```
docker-compose logs
```

### Troubleshooting issues

- **Django can't connect to the database**: When Django starts, it tries to connect to the database specified in the settings. If the database service is not ready yet or if the settings are incorrect, Django will fail to start. Ensure the database service is running and check the database settings.

- **A problem with the Docker setup**: There might be a problem with the Dockerfile or `docker-compose.yml` file that's preventing the 'web' service from starting. For example, you might have forgotten to install a necessary package, or a path in one of your Docker files might be incorrect.

## Using venv instead of Docker containers
```
python -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
venv/Scripts/python.exe -m pip install --upgrade pip`
```

## Connecting to the admin page

Assuming Superuser is already created
```
http://127.0.0.1:8000/admin
```