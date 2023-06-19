# Initialize


## Using Docker (Dev environment)

Make sure to create a copy of `Dockerfile` as `Dockerfile-local` and `Dockerfile-production`.
This is to use a non-root user on production and a root user on development environements.
**Remove any non-root user related commands** from `Dockerfile` and `Dockerfile-local`.
This way, VS Code will be able to connect to the dev container with the full access to workspace file system.

Assuming all docker-related configuration on OS level is complete, run following commands.

Create and start containers of all services defined in `docker-compose.yml`
```bash
docker-compose up
```

If you are attempting to re-build
```bash
docker-compose build --no-cache
docker-compose up
```
or
```bash
docker-compose up --build
```

Migrate
```bash
docker-compose exec app python manage.py migrate
```

Create Superuser
```bash
docker-compose exec app python manage.py createsuperuser
```

Bypass Email Activation for Superuser
(`is_active` field of user is initialized as `False` by default)
```bash
python manage.py shell
from core.models import KeiboUser
user = KeiboUser.objects.get(email='your-email@example.com')
user.is_active = True
user.save()
print(user.is_staff, user.is_superuser, user.is_active)
```

Reset Superuser password
```bash
python manage.py changepassword
```

## Deployment

Test the production environment before deploying.
```bash
docker-compose -f docker-compose-production.yml down --volumes
docker-compose -f docker-compose-production.yml build
docker-compose -f docker-compose-production.yml up
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
