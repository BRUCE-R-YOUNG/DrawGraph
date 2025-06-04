from __future__ import print_function
import boto3
from boto3.dynamodb.conditions import Attr
import datetime
import json
import traceback
import os

# ----- Dynamo Info (必要に応じて環境変数から取得) -----
TABLE_NAME = os.environ.get('TABLE_NAME', "default")
DDB_PRIMARY_KEY = "TIMESTAMP"
DDB_SORT_KEY = "DEVICE_NAME"
# -------------------------------------------------------

print("TABLE_NAME:", TABLE_NAME)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

# ------------------------------------------------------------------------


def dynamoQuery(device_name, request_time):
    print("dynamoQuery start")
    val_list = []
    print(
        f"Query parameters - DEVICE_NAME: {device_name}, requestTime: {request_time}")

    try:
        res = table.scan(
            FilterExpression=Attr("DEVICE_NAME").eq(
                device_name) & Attr("TIMESTAMP").gte(request_time),
            Limit=30
        )
    except Exception as e:
        print("Error executing scan: ", e)
        raise e

    print("Scan result: ", res)

    if 'Items' in res:
        for row in res['Items']:
            if 'device_data' in row and 'TEMPERATURE' in row['device_data']:
                val = row['device_data']['TEMPERATURE']
                item_dict = {
                    "timestamp": row['TIMESTAMP'],
                    "value": str(val)
                }
                val_list.append(item_dict)

    return val_list

# ------------------------------------------------------------------------


def lambda_handler(event, context):
    http_res = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": "",
        "isBase64Encoded": False
    }

    try:
        print("lambda_handler start")
        print(json.dumps(event))

        DEVICE_NAME = "temp_humi_bruce_20240620"
        request_time = "1970-01-01T00:00:00"

        print("Request Time: ", request_time)

        res_item_dict = {DEVICE_NAME: dynamoQuery(DEVICE_NAME, request_time)}
        http_res['body'] = json.dumps(res_item_dict)

    except Exception as e:
        print(traceback.format_exc())
        http_res["statusCode"] = 500
        http_res["body"] = "Lambda error. check lambda log"

    print("response:", json.dumps(http_res))
    return http_res
