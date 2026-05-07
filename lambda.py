from __future__ import print_function
import boto3
from decimal import Decimal
import json
import traceback
import os

TABLE_NAME = os.environ.get('TABLE_NAME', "default")
DEVICE_NAME = os.environ.get('DEVICE_NAME', "temp_humi_fujiwara_20260427")

print("TABLE_NAME:", TABLE_NAME)
print("DEVICE_NAME:", DEVICE_NAME)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def lambda_handler(event, context):
    try:
        print("lambda_handler start")

        items = []
        scanned_count = 0

        # 最初のscan
        response = table.scan()

        items.extend(response.get("Items", []))
        scanned_count += response.get("ScannedCount", 0)

        # まだ続きがある場合、繰り返し取得
        while "LastEvaluatedKey" in response:
            response = table.scan(
                ExclusiveStartKey=response["LastEvaluatedKey"]
            )

            items.extend(response.get("Items", []))
            scanned_count += response.get("ScannedCount", 0)

        print("Total Count:", len(items))
        print("Total ScannedCount:", scanned_count)

        # TIMESTAMP順に並び替え
        items.sort(key=lambda x: int(x.get("TIMESTAMP", 0)))

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps(
                {
                    "table": TABLE_NAME,
                    "device": DEVICE_NAME,
                    "count": len(items),
                    "scanned_count": scanned_count,
                    "items": items
                },
                cls=DecimalEncoder,
                ensure_ascii=False
            ),
            "isBase64Encoded": False
        }

    except Exception:
        print(traceback.format_exc())

        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(
                {
                    "message": "Lambda error. check lambda log"
                },
                ensure_ascii=False
            ),
            "isBase64Encoded": False
        }
