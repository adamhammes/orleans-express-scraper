#!/bin/sh
set -e

. ./secrets.sh
aws s3 sync s3://$AWS_BUCKET_NAME synced-s3

rsync -a --delete synced-s3/ unzipped/

gunzip unzipped/*.gz

