#!/bin/sh

set -e

cd /home/ec2-user/keibo-django-postgresql
/usr/local/bin/docker-compose -f docker-compose.deploy.yml run --rm certbot certbot renew