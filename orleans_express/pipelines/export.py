import datetime
import gzip
import json
import io
import os

import boto3

BUCKET_NAME = os.environ["AWS_BUCKET_NAME"]


class ItemCollector:
    def open_spider(self, spider):
        self.items = []

    def process_item(self, item, _):
        self.items += item["outboundDailyItineraries"]

    def close_spider(self, _):
        serialized = json.dumps(self.items)
        compressed = gzip.compress(serialized.encode("utf-8"))

        now = datetime.datetime.now(datetime.timezone.utc)
        date_slug = now.strftime("%Y%m%dT%H%M%SZ")
        file_name = date_slug + "-orleans-scrape.json.gz"

        with open(file_name, "wb+") as outfile:
            outfile.write(compressed)

        upload_to_s3(file_name, compressed)


def upload_to_s3(path, body):
    # For the following line of code to work, the following environment
    # variables need to be set:
    #
    # os.environ['AWS_ACCESS_KEY_ID']
    # os.environ['AWS_SECRET_ACCESS_KEY']
    s3 = boto3.resource("s3", region_name="us-east-2")
    bucket = s3.Bucket(BUCKET_NAME)
    bucket.put_object(Key=path, Body=body)
