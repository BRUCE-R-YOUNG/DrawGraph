from __future__ import print_function
import boto3
from boto3.dynamodb.conditions import Key
import datetime
import json
import traceback
import os

# DynamoDB情報
TABLE_NAME = os.environ.get('TABLE_NAME', "default")
DDB_PRIMARY_KEY = "TIMESTAMP"
DDB_SORT_KEY = "DEVICE_NAME"

print("Using DynamoDB Table:", TABLE_NAME)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

def dynamoQuery(device_name, request_time):
    print("dynamoQuery start")
    valList = []
    try:
        res = table.query(
            KeyConditionExpression=Key(DDB_SORT_KEY).eq(device_name) & Key(DDB_PRIMARY_KEY).lt(request_time),
            ScanIndexForward=False,
            Limit=30
        )

        for row in res['Items']:
            val = row['TEMPERATURE']
            itemDict = {
                "timestamp": row['TIMESTAMP'],
                "value": str(val)
            }
            valList.append(itemDict)
    except Exception as e:
        print("Error querying DynamoDB:", str(e))
        print(traceback.format_exc())
    
    return valList

def lambda_handler(event, context):
    HttpRes = {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": "",
        "isBase64Encoded": False
    }

    try:
        print("lambda_handler start")
        print(json.dumps(event))

        device_name = "temp_humi_press_bruce_20240624"
        request_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        resItemDict = {device_name: ""}
        resItemDict[device_name] = dynamoQuery(device_name, request_time)
        HttpRes['body'] = json.dumps(resItemDict)

    except Exception as e:
        print("Error in lambda_handler:", str(e))
        print(traceback.format_exc())
        HttpRes["statusCode"] = 500
        HttpRes["body"] = "Lambda error. Check lambda log."

    print("response: {}".format(json.dumps(HttpRes)))
    return HttpRes
