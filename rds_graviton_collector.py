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

client = boto3.client(
                    service,
                    aws_access_key_id=credentials['AccessKeyId'],
                    aws_secret_access_key=credentials['SecretAccessKey'],
                    aws_session_token=credentials['SessionToken']
                )

# initialize EC2 client to get list of regions to check
ec2_client = boto3.client('ec2', aws_access_key_id=accesskey, aws_secret_access_key=secretkey )
regions = ec2_client.describe_regions()

db_array = []
db_list = {}

with open("/tmp/data.json", "w") as f:
    # loop through all regions
    for region in regions['Regions']:
        print(f"Checking {region['RegionName']}")
        #initialize RDS client
        rds_client = boto3.client("rds", aws_access_key_id=accesskey, aws_secret_access_key=secretkey, region_name=region['RegionName'])
        # initialize paginator to handle large responses 
        paginator = rds_client.get_paginator("describe_db_instances")
        response_iterator = paginator.paginate()

        for page in paginator.paginate():
            # get specified data for each region that has a DB Instance
            for db in page['DBInstances']:
                db_list = {
                        'DBInstanceIdentifier': db['DBInstanceIdentifier'],
                        'Engine': db['Engine'], 
                        'EngineVersion': db['EngineVersion'], 
                        'DBInstanceClass': db['DBInstanceClass'], 
                        'MultiAZ': db['MultiAZ'], 
                        'StorageType': db['StorageType'], 
                        'AvailabilityZone': db['AvailabilityZone'], 
                        'InstanceCreateTime': db['InstanceCreateTime'], 
                        'AutoMinorVersionUpgrade': db['AutoMinorVersionUpgrade'], 
                        'PreferredMaintenanceWindow': db['PreferredMaintenanceWindow'], 
                        'TagList': db['TagList']
                    }
                jsonout = json.dumps(db_list, default=str)
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
        s3.upload_file(f'/tmp/data.json', bucket, f"rds/year={year}/month={month}/rds-graviton-{account_id}.json")
        print(f"RDS data in s3 {bucket}")
    except Exception as e:
        logging.warning("%s" % e)

s3_upload(account_id)