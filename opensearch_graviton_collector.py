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

domain_array = []
paramList = {}
domain_name_list = []

with open("opensearch_output_debug.json", "w") as f:
    for region in regions['Regions']:
        print(f"Checking {region['RegionName']}")
        opensearch_client = boto3.client("opensearch", aws_access_key_id=accesskey, aws_secret_access_key=secretkey, region_name=region['RegionName'])
    
        response = opensearch_client.list_domain_names()
    
        if len(response.get('DomainNames')) > 0:
            domainNames = response.get('DomainNames')
            domain_name_list = [d.get('DomainName', None) for d in domainNames]

            for domain in domain_name_list:
                print(domain)

                describeDomain = opensearch_client.describe_domain(DomainName=domain)
                response = describeDomain['DomainStatus']

                paramList = {
                    'DomainName': response['DomainName'],
                    'DomainId': response['DomainId'],
                    'EngineVersion': response['EngineVersion'],
                    'InstanceType': response['ClusterConfig']['InstanceType'],
                    'InstanceCount': response['ClusterConfig']['InstanceCount']
                  }

                jsonout = json.dumps(paramList, default=str)
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
        s3.upload_file(f'/tmp/data.json', bucket, f"opensearch/year={year}/month={month}/opensearch-graviton-{account_id}.json")
        print(f"Opensearch data in s3 {bucket}")
    except Exception as e:
        logging.warning("%s" % e)

# s3_upload(account_id)