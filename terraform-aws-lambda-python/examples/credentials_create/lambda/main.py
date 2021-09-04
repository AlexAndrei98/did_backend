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
    done = dynamodb.put_item(TableName="DID_POC", 
                                Item=item_data)

def save_to_main_table(cred_id,dynamodb):
    request = dynamodb.get_item(TableName="DID_POC", 
                                    Key={'hashed_key' : { 'S' : 'all_credentials'}})
    if (request.get('Item') is None):
        print("FIRST ALL CREDS")
        request_data = {
            'hashed_key': 'all_credentials',
            'all_cred_ids': [cred_id]
        }
    else:
        request_data = clean_dynamodb_item(request['Item'])
        print('exisiting creds', request_data)
        request_data['all_cred_ids'].extend([cred_id]) 

    item_data = format_data_dynamodb(request_data)
    print('all creds data',item_data)
    done = dynamodb.put_item(TableName="DID_POC", 
                                Item=item_data)

def lambda_handler(event, context):
    '''
    This function creates a credentials for two dids

credential = {
'issuer_to_hashed_key': 'afjk312kj4jkkj',
'issuer_to_public_key' : '---public key issuer---- ',
'issuer_to_type': 'TITLE_ORG',
'issued_to_hashed_key': 'vfeajv12yg32kvvgha', 
'issued_to_public_key' : '---public key issued---- ',
'issued_to_type': 'PERSON',
'signed' : 'False',
}
print(requests.post('https://h5ctmemjw0.execute-api.us-east-1.amazonaws.com/dev/credentials_create',json.dumps(credential)).content)

    '''
    LOGGER.info("%s", pformat({"Context" : vars(context), "Request": event}))
    dynamodb = boto3.client('dynamodb')
    
    data = json.loads(event['body'])
    data['hashed_key'] = data['issuer_to_hashed_key']+' to '+data['issued_to_hashed_key']+data['issued_date']
    # signed = data['signed']
    dynamo_data = format_data_dynamodb(data)
    
    
    table = dynamodb.put_item(TableName="DID_POC",
                                Item=dynamo_data)

    req = dynamodb.get_item(TableName="DID_POC", 
                                Key={'hashed_key' : { 'S' : data['hashed_key']}})
                                
    print(req['Item'])
    field_to_update ='signed_credentials'

    update(data['issuer_to_hashed_key'],('signed_credentials',data['hashed_key']),'False',dynamodb )
    update(data['issued_to_hashed_key'],('signed_credentials',data['hashed_key']),'False',dynamodb )
    save_to_main_table(data['hashed_key'],dynamodb)
    print('Assigned Credentials to both.')

    #TODO: SEND SNS MESSAGE TO NOTIFY APP
   
    return response(status=200, body={"Saved to ":'all fields table public'})


if __name__ == '__main__':
    # Do nothing if executed as a script
    pass

