#!/usr/bin/env python
'''
Echo service as a Lambda function
'''

import os
import sys
import json
import logging
from pprint import pformat
import boto3

# Hack to use dependencies from lib directory
BASE_PATH = os.path.dirname(__file__)
sys.path.append(BASE_PATH + "/lib")

LOGGER = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.INFO)

def response(status=200, headers=None, body=''):
    '''
    http://www.awslessons.com/2017/lambda-api-gateway-internal-server-error/
    '''
    if not body:
        return {'statusCode': status}

    if headers is None:
        headers = {'Content-Type': 'application/json'}

    return {
        'statusCode': status,
        'headers': headers,
        'body': json.dumps(body)
    }
def format_data_dynamodb(data):
    new_dict={}
    for k, v in data.items():
        if isinstance(v, list):
            new_dict[k]= {"L": [{"S":value} for value in v]}
        elif isinstance(v, dict):
            new_dict[k]={}
            new_dict[k]["M"]={}
            for key, value in v.items():
                new_dict[k]["M"][key] = {"S":value}        
        else:
            new_dict[k]= {"S" :v} 
    return new_dict

def lambda_handler(event, context):
    '''
    This function is called on HTTP request.
    It logs the request and an execution context. Then it returns body of the request.
    payload = {'hashed_key': 'vfeajv12yg32kvvgha', 
    'did_to_link': 'afjk312kj4jkkj',
    'status':'True'
    }

    '''
    LOGGER.info("%s", pformat({"Context" : vars(context), "Request": event}))
    data = json.loads(event['body'])
    hashed_key = data['hashed_key']
    did_to_link = data['did_to_link']
    status = data['status'] #True or False (string)
    dynamodb = boto3.client('dynamodb')

    field_to_update = 'linked_dids'

    req1 = dynamodb.update_item(TableName="DID_POC", 
                            Key={'hashed_key' : { 'S' : hashed_key }},
                            UpdateExpression=f"set {field_to_update}.{did_to_link}=:r",
                            ExpressionAttributeValues={
            ":r": {"S":status}
        })
    #TODO: CHECK IF DID TO LINK EXISTS
    req2 = dynamodb.update_item(TableName="DID_POC", 
                            Key={'hashed_key' : { 'S' : did_to_link }},
                            UpdateExpression=f"set {field_to_update}.{hashed_key}=:r",
                            ExpressionAttributeValues={
            ":r": {"S":status}
    })
    print(req1)
    print(req2)
   
    return response(status=200, body='Successfuly requested wallets.')


if __name__ == '__main__':
    # Do nothing if executed as a script
    pass

