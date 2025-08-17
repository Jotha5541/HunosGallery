import time
import os
import requests
import json
import boto3 # AWS SDK for Python

sqs = boto3.client('sqs')

def lambda_handler(event, context):

    # ----- Credentials for Environment ----- #
    pinterest_token = os.environ.get('PINTEREST_ACCESS_TOKEN')
    pinterest_username = os.environ.get('PINTEREST_USERNAME')
    queue_url = os.environ.get('SQS_QUEUE_URL')
    

    # ----- Pinterest API Call ----- #
    url = f"https://api.pinterest.com/v5/pins?username={pinterest_username}"
    headers = {
        "Authorization": f"Bearer {pinterest_token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() 
        pin_data = response.json()
        print(f"Successfully fetched {len(pin_data.get('items', []))} pins from Pinterest.")
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to fetch data from Pinterest API: {e}")
        return {'statusCode': 500, 'body': json.dumps('API request error.')}    
    
    
    # ----- Process Pin Data to SQS Queue ----- #
    process_pins = pin_data.get('items', [])
    if not process_pins:
        print("No new pins to process.")
        return {'statusCode': 200, 'body': json.dumps('No new pins found.')}
    
    count = 0
    for pin in process_pins:
        message_body = {
            'pin_id': pin.get('id'),
            'image_url': pin.get('media', {}).get('images', {}).get('1200x', {}).get('url'),
            'description': pin.get('description')
        }
        if message_body['image_url']:
            try:
                sqs.send_message(
                    QueueUrl=queue_url,
                    MessageBody=json.dumps(message_body)
                )
                count += 1
            except Exception as e:
                print(f"ERROR: Failed to send message to SQS: {e}")

    print(f"\nFinished sending {count} Pins to SQS queue for processing.\n")

    return {
        'statusCode': 200,
        'body': f'Successfully sent {count} Pins to processing queue.'
    }
    
