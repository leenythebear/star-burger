#!/bin/bash

set -e
cd /opt/star-burger
git pull

docker compose -f docker-compose-prod.yml up -d

ID_COMMIT=`git --git-dir=/opt/star-burger/.git rev-parse HEAD`
..
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
