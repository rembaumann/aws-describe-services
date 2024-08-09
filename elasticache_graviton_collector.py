import boto3
import os
import json
import datetime
from json import JSONEncoder
import logging
from botocore.client import Config
from botocore.exceptions import ClientError

account_id = '663146358110'
bucket = 'rem-graviton-lambda-test' 

ec2_client = boto3.client('ec2', aws_access_key_id=accesskey, aws_secret_access_key=secretkey )
regions = ec2_client.describe_regions()

cluster_list = {}

with open("/tmp/data.json", "w") as f:
    for region in regions['Regions']:
        print(f"Checking {region['RegionName']}")
        elasticache_client = boto3.client("elasticache", aws_access_key_id=accesskey, aws_secret_access_key=secretkey, region_name=region['RegionName'])
        paginator = elasticache_client.get_paginator("describe_cache_clusters") #Paginator for a large list of accounts
        response_iterator = paginator.paginate()

        for page in paginator.paginate():
            for cluster in page['CacheClusters']:
                cluster_list = {
                        'CacheClusterId': cluster['CacheClusterId'],
                        'CacheNodeType': cluster['CacheNodeType'], 
                        'EngineVersion': cluster['EngineVersion'], 
                        'Engine': cluster['Engine'], 
                        'NumCacheNodes': cluster['NumCacheNodes'],
                        'PreferredAvailabilityZone': cluster['PreferredAvailabilityZone'], 
                        'CacheClusterCreateTime': cluster['CacheClusterCreateTime']
                    }
                jsonout = json.dumps(cluster_list, default=str)
                f.write(jsonout)
                f.write("\n")


def s3_upload(account_id):
    if os.path.getsize("/tmp/data.json") == 0:
        print(f"No data in file")
        return
    d = datetime.datetime.now()
    month = d.strftime("%m")
    year = d.strftime("%Y")
    dt_string = d.strftime("%d%m%Y-%H%M%S")
    today = datetime.date.today()
    year = today.year
    month = today.month
    try:
        s3 = boto3.client('s3', aws_access_key_id=accesskey, aws_secret_access_key=secretkey)
        s3.upload_file(f'/tmp/data.json', bucket, f"elasticache/year={year}/month={month}/elasticache-graviton-{account_id}.json")
        print(f"Elasticache data in s3 {bucket}")
    except Exception as e:
        logging.warning("%s" % e)


s3_upload(account_id)