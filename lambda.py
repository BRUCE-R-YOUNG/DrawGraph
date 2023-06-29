from __future__ import print_function
import boto3
from boto3.dynamodb.conditions import Key
import datetime
import json
import traceback
import os

# -----Dynamo Info change here------
TABLE_NAME = os.environ.get('TABLE_NAME', "default")  # Lambda関数の環境変数を取得するため
DDB_PRIMARY_KEY = "DEVICE_NAME"
DDB_SORT_KEY = "TIMESTAMP"
# -----Dynamo Info change here------

print(TABLE_NAME)


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

# ------------------------------------------------------------------------


def dynamoQuery(DEVICE_NAME, requestTime):
    print("dynamoQuery start")
    valList = []
    res = table.query(
        KeyConditionExpression=Key(DDB_PRIMARY_KEY).eq(DEVICE_NAME) &
        Key(DDB_SORT_KEY).lt(requestTime),
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

    return valList

# ------------------------------------------------------------------------
# call by Lambda here.
#  Event structure : API-Gateway Lambda proxy post
# ------------------------------------------------------------------------


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

        # get Parameters
        # pathParameters = event.get('pathParameters')
        # print(pathParameters)

        DEVICE_NAME = "temp_humi_press_bruce_20230626"
        requestTime = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        resItemDict = {DEVICE_NAME: ""}
        resItemDict[DEVICE_NAME] = dynamoQuery(DEVICE_NAME, requestTime)
        HttpRes['body'] = json.dumps(resItemDict)

    except Exception as e:
        print(traceback.format_exc())
        HttpRes["statusCode"] = 500
        HttpRes["body"] = "Lambda error. check lambda log"

    print("response:{}".format(json.dumps(HttpRes)))
    return HttpRes
