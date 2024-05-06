# Smart Budget App Backend Service

## Introduction

Keibo is a privacy-focused budget management system, designed to function like a digital account book.
It enables users to track their expenses and analyze spending without connecting to any banking APIs, ensuring user data privacy and security.

The backend service is built using Django and supports a variety of functionalities, including the tracking of key economic indexes such as inflation rates, exchange rates, and interest rates across different currencies and financial regions.
This service helps users make informed decisions about their finances by predicting future spending patterns based on historical data.

## Features

- Expense Tracking: Manually log and categorize expenses to keep track of spending without the need for bank API integration.
- Economic Indexes: Fetch and display various economic indicators, including inflation rates, exchange rates, and interest rates, which help users understand external factors affecting their finances.
- Financial Analysis: Analyze spending patterns and predict future trends to assist with financial planning.
- Privacy First: Built with privacy as a core principle, ensuring that personal financial data is stored securely and never shared.

## Technical Stack

Framework: [Django](https://www.djangoproject.com)
Database: [PostgreSQL](https://www.postgresql.org)
Caching: [Redis](https://redis.io)
Reverse proxy routing: [nginx](https://www.nginx.com)
Containerization: [Docker](https://www.docker.com)
SSL/TLS: [Certbot](https://certbot.eff.org) with [LetsEncrypt](https://letsencrypt.org) certificates
Core auth library: [Djoser](https://pypi.org/project/djoser)

## Contributing

I welcome contributions! Please submit pull requests for any bug fixes or feature enhancements.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.

# Initialize development environment

## Using Docker (Dev environment)

Make sure to create a copy of `dockerfile` as `dockerfile-local` and `dockerfile-production`.
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
quit()
```

Reset Superuser password

```bash
python manage.py changepassword
```

## Infrastructure architecture

`Client`
⬇️
`Amazon DNS (Hosted Zones)`
⬇️
`Amazon CloudFront`
⬇️
`AWS Load Balancer`
⬇️
`Nginx`
⬇️
`uWSGI`
⬇️
`Django Application`

## Deployment using AWS

(Priori to the first deployment) test the production environment locally before deploying.

```bash
docker-compose -f docker-compose-production.yml down --volumes
docker-compose -f docker-compose-production.yml build
docker-compose -f docker-compose-production.yml up
```

1. Go to AWS. Create an EC2 instance. In this doc, I'll be using `Amazon Linux`.

Warning: _Make sure you are using the right region. It is important not to switch the region before all steps are completed to make sure all configuration is in order. For example, If you switch the region, you won't be able to see your EC2 instance previously created in another region._

2. Configure a `security group` to attach to the EC2 instance. (ex: HTTPS TCP PORT 443, HTTP TCP PORT 80, SSH TCP PORT 22...)
3. Create an `elastic ip address` to attach to the EC2 instance.
4. Connect to the EC2 instance's terminal using SSH connection (Putty required if Windows). Install dependencies and configure the environment using these commands:

```bash
sudo yum install git -y
sudo yum install -y docker
sudo systemctl enable docker.service
sudo systemctl start docker.service
sudo usermod -aG docker ec2-user
sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose version
sudo chkconfig docker on
```

5. Set up EC2 instance to git clone this repo

```bash
git clone https://github.com/AndyLeezard/keibo-django-postgresql.git
```

6. cd into the repo folder, create a dotenv file and edit

```bash
touch .env
nano .env
```

7. Build and run containers

```bash
docker-compose -f docker-compose-production.yml up -d
```

8. Check docker container status

```bash
docker ps
docker logs keibo-django-postgresql-app-1
docker logs keibo-django-postgresql-proxy-1
```

9. Create a superuser

```bash
docker-compose exec app python manage.py createsuperuser
```

## Enable HTTPS

To properly implement secure cookies (especially important for Chromium-based browsers), the `SSL` setup is required.

To enable HTTPS, a domain name is first required.

Initially I let AWS handle it with additional services and costs, but I figured I'd reduce the hosting fees so I did it by using Letsencrypt and Certbot.
Either way, you'll need a domain name.

### Using Letsencrypt and Certbot

I initially used a plain EC2 instance, and it was working great.
But then I switched to a lightsail instance.

#### Stages of deployment

1. getting certificates (first run)
2. Serving HTTPS
3. Renewing certificates (periodically)

#### Detailed steps

1. Get into the instance terminal
2. Git clone the repository.
3. Configure the .env file. `DOMAIN=your.website` without the https://.

4. Build docker images and get the first certificate

```bash
docker-compose -f docker-compose-production.yml run --rm certbot /opt/certify-init.sh
```

When it runs, it waits for proxy and request a certificate for the domain.
After then it should say "successfully received certificate".

5. Unmount the running containers because they are serving in http, and then rebuild the images, and then remount the containers to serve in https.

```bash
docker-compose -f docker-compose-production.yml down
docker-compose -f docker-compose-production.yml build
docker-compose -f docker-compose-production.yml up
```

### (Deprecated) let AWS handle it

1. If you haven't, buy a domain on [AWS Route 53](https://us-east-1.console.aws.amazon.com/route53/domains/home#/).
   this will be necessary to issue a `certificate` using `ACM`. (If I'm wrong and there's another cheaper way pls correct me.)

2. Use `ACM` to generate a certificate.

3. Create a `target group` that will be associated with an `Eslastic Load Balancer (ELB)`. Type = Instance.

Warning: _Make sure to click on the `Include as pending below` button before saving. Also Make sure you're still on the right region. otherwise it will be invisible._

4. On the EC2 page, look for the `load balancer` options and set up an `ELB` by choosing the `Application Load Balancer (ALB)` option.
   By default, a HTTP listner will be created.
   Add a HTTPS listener and choose the `target group` previously created.
   Health check path: `/api/hello_world`
   AWS Interface: (EC2/Target groups/keibo-instance)

5. Create a Distribution on `CloudFront` that will link your `ELB` and your domain. Here you have the option to auto-convert any http request to https. The distribution is only active if it is connected to a url on `Hosted Zones` in `Route53` which is the AWS interface.

6. Configure the connection between the domain and your `CloudFront` distribution on `Hosted Zones of Route53`, .

## Update the code and re-build the container with the latest version

```bash
git pull origin
docker-compose -f docker-compose-production.yml build app
docker-compose -f docker-compose-production.yml up -d app
```

## Troubleshooting 502 Bad Gateaway nginx error

```bash
docker-compose -f docker-compose-production.yml restart <proxy-container-name>
```

## Troubleshooting 'No space left on device' while building a new docker image

Check the disk status using this command:

```bash
df -h
```

If really there is no space, you might have to prune old docker images.

```bash
docker images prune
```

_You can also prune the volumens. Do this if you're not storing files locally (which you shouldn't be anyway, they should be in something like AWS S3) -Nitin Nain from StackOverflow-_

```bash
docker system prune --volumes
```

## Troubleshooting database related problems

When removing containers, do not forget to remove the volumes as well.
Warning: this will erase all databases

```bash
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

Listen to a container logs

```bash
docker ps -a
docker logs --follow <container ID>
```

```bash
docker-compose logs
```

### Troubleshooting issues

- **Django can't connect to the database**: When Django starts, it tries to connect to the database specified in the settings. If the database service is not ready yet or if the settings are incorrect, Django will fail to start. Ensure the database service is running and check the database settings.

- **A problem with the Docker setup**: There might be a problem with the Dockerfile or `docker-compose.yml` file that's preventing the 'web' service from starting. For example, you might have forgotten to install a necessary package, or a path in one of your Docker files might be incorrect.

## Using venv instead of Docker containers

```bash
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

## Edit .env file

```
DJANGO_SECRET_KEY='django-insecure-redacted'
DJANGO_ALLOWED_HOSTS='127.0.0.1,localhost'
CORS_ALLOWED_ORIGINS='http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173'
DEBUG='boolean'
DEVELOPMENT_MODE='boolean'

POSTGRES_DB='db-name-redacted'
POSTGRES_USER='admin-name-redacted'
POSTGRES_PASSWORD='db-pw-redacted'

GOOGLE_AUTH_KEY='redacted'
GITHUB_AUTH_KEY='redacted'

GOOGLE_AUTH_SECRET_KEY='redacted'
GITHUB_AUTH_SECRET_KEY='redacted'

DOMAIN='localhost:3000'
AUTH_COOKIE_SECURE='boolean'
ACCESS_DURATION_IN_DAYS='numeric-value'
REFRESH_DURATION_IN_DAYS='numeric-value'

AWS_SES_ACCESS_KEY_ID='redacted'
AWS_SES_SECRET_ACCESS_KEY='redacted'
AWS_SES_REGION_NAME='us-region-redacted'
AWS_SES_FROM_EMAIL='example@example.com'

REDIRECT_BASE_URL='base_url'
REDIS_URL='redis_url'

API_PROVIDER_KEY_HEADER='redacted'
API_PROVIDER_HOST_HEADER='redacted'
API_PROVIDER_KEY='redacted'

API_EXCHANGE_RATES_HOST='redacted'
API_EXCHANGE_RATES='redacted'

API_CRYPTO_PRICES_HOST='redacted'
API_CRYPTO_PRICES='redacted'

API_FRED_KEY='redacted'
API_ECOS_BOK_KR_KEY='redacted'

# To experiment Supabase database, I added an optional parameter to hit a supabase request on economic index updates.
USE_SUPABASE_PLUGIN='false'
```

## Auth docs

https://djoser.readthedocs.io/en/latest/base_endpoints.html
