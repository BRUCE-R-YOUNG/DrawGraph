from __future__ import print_function
import boto3
from boto3.dynamodb.conditions import Key
import datetime
import json
import traceback
import os

# -----Dynamo Info change here------
TABLE_NAME = os.environ.get('TABLE_NAME', "default")
DDB_PRIMARY_KEY = "DEVICE_NAME"
DDB_SORT_KEY = "TIMESTAMP"
# -----Dynamo Info change here------

print("TABLE_NAME:", TABLE_NAME)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

# ------------------------------------------------------------------------

def dynamoQuery(DEVICE_NAME, requestTime):
    print("dynamoQuery start")
    valList = []
    print("Query parameters - DEVICE_NAME: {}, requestTime: {}".format(DEVICE_NAME, requestTime))
    try:
        res = table.query(
            KeyConditionExpression=Key(DDB_PRIMARY_KEY).eq(DEVICE_NAME) &
            Key(DDB_SORT_KEY).gte(requestTime),  # changed from le to lte
            ScanIndexForward=False,
            Limit=30
        )
    except Exception as e:
        print("Error executing query: ", e)
        raise e

    print("Query result: ", res)

    if 'Items' in res:
        for row in res['Items']:
            if 'device_data' in row and 'TEMPERATURE' in row['device_data']:
                val = row['device_data']['TEMPERATURE']
                itemDict = {
                    "timestamp": row['TIMESTAMP'],
                    "value": str(val)
                }
                valList.append(itemDict)

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

        DEVICE_NAME = "temp_humi_press_bruce_20240624"  
        requestTime = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        print("Request Time: ", requestTime)

        resItemDict = {DEVICE_NAME: ""}
        resItemDict[DEVICE_NAME] = dynamoQuery(DEVICE_NAME, requestTime)
        HttpRes['body'] = json.dumps(resItemDict)

    except Exception as e:
        print(traceback.format_exc())
        HttpRes["statusCode"] = 500
        HttpRes["body"] = "Lambda error. check lambda log"

    print("response:{}".format(json.dumps(HttpRes)))
    return HttpRes
