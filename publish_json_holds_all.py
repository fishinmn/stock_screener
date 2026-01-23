# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 08:36:15 2016

@author: efischer
"""
import pandas as pd
import numpy as np
import os
import time
import logging
import yfinance as yf
import yahooquery as yq
from datetime import datetime, timedelta
from investing_functions import *
import math
import json
import requests
import boto3
from botocore.config import Config
from boto3.s3.transfer import TransferConfig

###get my stocks caps
current_time = datetime.datetime.now()
pd.set_option("display.max_colwidth", 10000)


dir_path = os.path.dirname(os.path.realpath(__file__))
filepath = os.path.join(dir_path, 'data', 'algo10_data_all.csv')
data = pd.read_csv(filepath, encoding='utf-8')
data = data.where(pd.notnull(data), None)  # <-- This line converts NaN to None (which becomes null in JSON)
# Convert DataFrame to list of dicts for JSON export
export_json = data.to_dict(orient='records')

#writing data data frame to json file
file_name = "holds_json_data_all.json"
filepath = os.path.join(dir_path, 'data', file_name)            
with open(filepath, 'w') as f:
    json.dump(export_json, f, indent=4, sort_keys=True, default=str)            

##################

recommendation_list_string = json.dumps(data.to_dict(orient='records'), indent=4, sort_keys=True, default=str)
recommendation_list = json.loads(recommendation_list_string)    
#recommendation_list_json = json.loads(recommendation_list_string)

##write
file_html = open("C:/git/stock_analysis_app/holds_json_data_all.html", "w")
#file_html.write("<html>")
file_html.write(json.dumps(recommendation_list))
#file_html.write("</html>")
file_html.close()

##move to html folder
dir_path = os.path.dirname(os.path.realpath(__file__))
filepath1 = os.path.join(dir_path, "holds_json_data_all.html")
filepath2 = os.path.join(dir_path, 'data', "holds_json_data_all.html")
try:
    os.rename(filepath1, filepath2)
except:
    os.replace(filepath1, filepath2)


file_name = "holds_json_data_all.html"
dir_path = os.path.dirname(os.path.realpath(__file__))
filepath = os.path.join(dir_path, 'data', file_name)
bucketname = "data.fuzzyforrest.ai"

# configure retries/timeouts and transfer config for robust uploads
client_config = Config(
    retries={'max_attempts': 8, 'mode': 'standard'},
    connect_timeout=60,
    read_timeout=60
)
transfer_config = TransferConfig(
    multipart_threshold=8 * 1024 * 1024,   # 8 MB
    multipart_chunksize=8 * 1024 * 1024,
    max_concurrency=4,
    use_threads=True
)

s3_client = boto3.client('s3', config=client_config)
s3_resource = boto3.resource('s3')

def robust_upload_file(local_path, bucket, key, attempts=3, delay=5):
    last_exc = None
    for i in range(attempts):
        try:
            s3_client.upload_file(local_path, bucket, key, Config=transfer_config)
            # set ACL after upload
            s3_client.put_object_acl(Bucket=bucket, Key=key, ACL='public-read')
            return
        except Exception as e:
            last_exc = e
            print(f"upload attempt {i+1} failed: {e}; retrying in {delay}s")
            time.sleep(delay)
    raise last_exc

# upload HTML via robust helper and ensure metadata
robust_upload_file(filepath, bucketname, file_name)
s3_object = s3_resource.Object(bucketname, file_name)
s3_object.copy_from(CopySource={'Bucket': bucketname, 'Key': file_name},
                    MetadataDirective="REPLACE",
                    ContentType="text/html",
                    ACL='public-read')

##################
file_name = "holds_json_data_all.json"
dir_path = os.path.dirname(os.path.realpath(__file__))
filepath = os.path.join(dir_path, 'data', file_name)
bucketname = "data.fuzzyforrest.ai"

# upload JSON via robust helper and set metadata
robust_upload_file(filepath, bucketname, file_name)
s3_object = s3_resource.Object(bucketname, file_name)
s3_object.copy_from(CopySource={'Bucket': bucketname, 'Key': file_name},
                    MetadataDirective="REPLACE",
                    ContentType="application/json",
                    ACL='public-read')

##################

url = "https://www.stratifydataconsulting.com/holds_json_data_all.html"
response = requests.get(url)
print(response.text)

# import wget
# url = "https://seekingalpha.com/news/4049491-software-company-ansys-evaluating-sale-amid-takeover-interest-bloomberg"
# wget.download(url)