from __future__ import print_function
import boto3
from boto3.dynamodb.conditions import Key
import datetime
import json
import traceback
import os

# DynamoDB情報
TABLE_NAME = os.environ.get('TABLE_NAME', "default")
DDB_PRIMARY_KEY = "DEVICE_NAME"
DDB_SORT_KEY = "TIMESTAMP"

print(TABLE_NAME)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

def dynamoQuery(DEVICE_NAME, startTime, endTime):
    print("dynamoQuery start")
    valList = []
    try:
        res = table.query(
            KeyConditionExpression=Key(DDB_PRIMARY_KEY).eq(DEVICE_NAME) & Key(DDB_SORT_KEY).between(startTime, endTime),
            ScanIndexForward=False,
            Limit=30
        )

        for row in res['Items']:
            val = row['device_data']['TEMPERATURE']
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
    # Lambda Proxy response back template
    HttpRes = {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": "",
        "isBase64Encoded": False
    }

    try:
        print("lambda_handler start")
        print(json.dumps(event))

        DEVICE_NAME = "temp_humi_press_bruce_20240624"
        endTime = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        startTime = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')

        resItemDict = {DEVICE_NAME: ""}
        resItemDict[DEVICE_NAME] = dynamoQuery(DEVICE_NAME, startTime, endTime)
        HttpRes['body'] = json.dumps(resItemDict)

    except Exception as e:
        print(traceback.format_exc())
        HttpRes["statusCode"] = 500
        HttpRes["body"] = "Lambda error. check lambda log"

    print("response:{}".format(json.dumps(HttpRes)))
    return HttpRes
