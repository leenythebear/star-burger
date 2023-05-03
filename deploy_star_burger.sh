#!/bin/bash

set -e
cd /opt/star-burger
git pull
source /root/.pyenv/versions/3.9.0/envs/django_39/bin/activate
source .env

pip install -r requirements.txt
npm ci --dev
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

python3 manage.py migrate --no-input
python3 manage.py collectstatic --no-input

systemctl daemon-reload
systemctl restart django.service
systemctl reload nginx

ID_COMMIT=`git --git-dir=/opt/star-burger/.git rev-parse HEAD`

curl --request POST \
     --url https://api.rollbar.com/api/1/deploy \
     --header "X-Rollbar-Access-Token: $ROLLBAR_TOKEN" \
     --header 'accept: application/json' \
     --header 'content-type: application/json' \
     --data '
{
  "environment": "'"$CURRENT_ENVIRONMENT"'",
  "revision": "'"$ID_COMMIT"'"
}
'
echo 'Deploy successfully done.'
