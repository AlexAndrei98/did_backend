#!/usr/bin/env python
'''
Echo service as a Lambda function
'''

import os
import sys
import json
import logging
from pprint import pformat


# Hack to use dependencies from lib directory
BASE_PATH = os.path.dirname(__file__)
sys.path.append(BASE_PATH + "/lib")

LOGGER = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.INFO)

import boto3
from flatten_dict import flatten, unflatten

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

def clean_dynamodb_item(data):
    clean_dict={}
    for k, values in data.items():
        if isinstance(values,dict):
            for key, values2 in values.items():
                if key is 'S':
                    clean_dict[k] = values2
                elif key is 'L':
                    clean_dict[k] = [list(el.values())[0] for el in values2]
                elif key is 'M':
                    clean_dict[k]={}
                    for new_key, vals in values2.items():
                        clean_dict[k][new_key]= list(vals.values())[0]
    return clean_dict

def update(key, fields, value, dynamodb):    
    request = dynamodb.get_item(TableName="DID_POC", 
                                Key={'hashed_key' : { 'S' : key}})
    request_data = flatten(clean_dynamodb_item(request['Item']))
    request_data[fields] = value
    request_data = unflatten(request_data)
    item_data = format_data_dynamodb(request_data)
    dynamodb.put_item(TableName="DID_POC", 
                                Item=item_data)

def lambda_handler(event, context):
    '''
    This function is called on HTTP request.
    It logs the request and an execution context. Then it returns body of the request.
payload_sign = {
    'issuer_to_hashed_key': 'afjk312kj4jkkj',
    'issued_to_hashed_key': 'vfeajv12yg32kvvgha'
    'issued_date':'Somedate'
    }
payload_sign = {
    'hashed_key': 'afjk312kj4jkkj to vfeajv12yg32kvvgha'
    }
    '''
    LOGGER.info("%s", pformat({"Context" : vars(context), "Request": event}))
    data = json.loads(event['body'])
    issuer_key_hash = data['issuer_to_hashed_key']
    issued_key_hash = data['issued_to_hashed_key']
    date = data['issued_date']

    cred_key = issuer_key_hash+' to '+issued_key_hash+date
    dynamodb = boto3.client('dynamodb')

    update(issuer_key_hash,('signed_credentials',cred_key),'True',dynamodb)

    update(issued_key_hash,('signed_credentials',cred_key),'True',dynamodb)


    update(cred_key,('signed',),'True',dynamodb)

    return response(status=200, body={'success':f'Successfuly signed credential {cred_key}.'})


if __name__ == '__main__':
    # Do nothing if executed as a script
    pass

