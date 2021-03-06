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
        headers = {
            "Access-Control-Allow-Headers":  "Content-Type",
            "Access-Control-Allow-Origin" : "*",
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'

        }

    return {
        'statusCode': status,
        'headers': headers,
        'body': json.dumps(body)
    }


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
    This function creates a did. 
    In order to create a did you need:
    hashed_key: String,
    public_key Key: String,
    private Key: String,
    seed_phrase: String,
    name: String,
    entityType: String,
    linked_dids: [String]
    credentials: [String]
    signed_credentials: [String]
import requests, json
data_new1 = {
    'hashed_key': 'afjk312kj4jkkj', 
    'public_key': '--BEGIN PUBLIC KEY ----- 324nk6jk4n6k453yh34b5hj', 
    'private_key': '--BEGIN PRIVATE KEY ----- nvjks34ktn4j2tn4h2baa', 
    'name': 'DOMA LLC', 
    'entityType': 'TITLE_ORG', 
    'seed_phrase':['title',' is boring'], 
    'signed_credentials' :{},
    'linked_dids': {}
    }


data_new = {'hashed_key': 'vfeajv12yg32kvvgha', 
    'public_key': '--BEGIN PUBLIC KEY ----- 324nk6jk4n6k453yh34b5hj', 
    'private_key': '--BEGIN PRIVATE KEY ----- nvjks34ktn4j2tn4h2baa', 
    'name': 'SAINT LOUIS COUNTY LLC', 
    'entityType': 'PERSON', 
    'seed_phrase':['alex',' is awesome'], 
    'signed_credentials' :{},
    'linked_dids': {}}
url_create= 'https://rfl2i2ty4f.execute-api.us-east-1.amazonaws.com/dev/did_create'
print(requests.post(url_create,json.dumps(data_new)).content)
print(requests.post(url_create,json.dumps(data_new1)).content)

    '''
    LOGGER.info("%s", pformat({"Context" : vars(context), "Request": event}))
    data = json.loads(event['body'])
    dynamo_data = format_data_dynamodb(data)
    keys_to_check = ['hashed_key',
    'public_key ',
    'private_key',
    'seed_phrase',
    'name',
    'entityType']
    print(sorted(keys_to_check)==sorted(list(data.keys())))
    print(dynamo_data)
    dynamodb = boto3.client('dynamodb')

    # mock_data = {
    # "hashed_key":  {"S":"alex_test"},
    # "public_key":  {"S":"alex"},
    # "private key":  {"S":"alex"},
    # "seed_phrase":  {"S":"alex"},
    # "name":  {"S":"alex"},
    # "type":  {"S":"alex"},
    # "linked_dids":  {"M" :{"idd": {"S": "alex"} ,{"idd": {"S": "alex"}}]},
    # "credentials": {"L" :[{"S": "alex"},{"S": "alex"}]},
    # "signed_credentials": {"L" :[{"S": "alex"},{"S": "alex"}]}
    # }

    table = dynamodb.put_item(TableName="DID_POC", 
                                Item=dynamo_data)

    # get item
    req = dynamodb.get_item(TableName="DID_POC", 
                                Key={'hashed_key' : { 'S' : dynamo_data['hashed_key']['S']}})
                                
    resp = clean_dynamodb_item(req['Item'])
    return response(status=200, body=resp)

if __name__ == '__main__':
    # Do nothing if executed as a script
    pass
