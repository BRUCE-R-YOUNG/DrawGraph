import boto3
import json
from boto3.dynamodb.conditions import Key

# DynamoDBのクライアントを設定
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    # DynamoDBのテーブル名
    table_name = "temp_humi_press_bruce_20240624"
    table = dynamodb.Table(table_name)
    
    # パーティションキーとソートキーの値をイベントから取得
    partition_key = event.get('TIMESTAMP')
    sort_key = event.get('DEVICE_NAME')
    
    # デバッグログを追加
    print(f"Received event: {json.dumps(event, indent=2)}")
    print(f"Partition Key: {partition_key}")
    print(f"Sort Key: {sort_key}")
    
    if not partition_key or not sort_key:
        return {
            'statusCode': 400,
            'body': json.dumps('Partition key or sort key not provided.')
        }
    
    # DynamoDBからアイテムを取得
    try:
        response = table.get_item(
            Key={
                'TIMESTAMP': partition_key,
                'DEVICE_NAME': sort_key
            }
        )
    except Exception as e:
        print(f'Error getting item from DynamoDB: {str(e)}')
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error getting item from DynamoDB: {str(e)}')
        }
    
    # アイテムが存在しない場合の処理
    if 'Item' not in response:
        return {
            'statusCode': 404,
            'body': json.dumps('Item not found in DynamoDB.')
        }
    
    item = response['Item']
    
    # デバッグのためにアイテム全体をログに出力
    print(f"Retrieved item: {json.dumps(item, indent=2)}")
    
    # device_dataマップからTEMPERATUREフィールドを取得
    device_data = item.get('device_data', {})
    temperature = device_data.get('TEMPERATURE')
    
    if temperature is None:
        return {
            'statusCode': 400,
            'body': json.dumps('Temperature not found in the item.')
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'temperature': temperature
        })
    }
