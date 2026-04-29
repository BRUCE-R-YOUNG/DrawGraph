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

        # フィルターなしで、とりあえず5件取得
        res = table.scan(Limit=5)

        print("Scan Count:", res.get("Count"))
        print("ScannedCount:", res.get("ScannedCount"))
        print("Items:")
        print(json.dumps(res.get("Items", []),
              cls=DecimalEncoder, ensure_ascii=False, indent=2))

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(
                {
                    "table": TABLE_NAME,
                    "device": DEVICE_NAME,
                    "count": res.get("Count"),
                    "scanned_count": res.get("ScannedCount"),
                    "items": res.get("Items", [])
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
            "body": "Lambda error. check lambda log"
        }
