import json
import boto3
from botocore.exceptions import ClientError

cognito_client = boto3.client('cognito-idp')

USER_POOL_ID = 'us-east-1_s1VeEPHyY'
CLIENT_ID = '7ien1g4pficmdogqkr9irrnfb4'


def lambda_handler(event, context):
    print(event)
    req_body = event['body']
    print(req_body)
    json_acceptable_string = req_body.replace("'", "\"")
    d = json.loads(json_acceptable_string)
    user = d.get("crm")
    pwd = d.get("password")

    if not user or not pwd:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "CRM e/ou senha não fornecidos."})
        }
    
   
#teste deploy esteira
    try:
        response = cognito_client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': user,
                'PASSWORD': pwd
            },
            ClientId=CLIENT_ID
        )
        challenge = response.get('ChallengeName')

        if challenge == 'NEW_PASSWORD_REQUIRED':
            challenge_response = cognito_client.respond_to_auth_challenge(
                ClientId=CLIENT_ID,
                ChallengeName='NEW_PASSWORD_REQUIRED',
                Session=response.get('Session'),
                ChallengeResponses={
                    'USERNAME': user,
                    'NEW_PASSWORD': pwd
                }
            )
            token = challenge_response.get("AuthenticationResult", {}).get("AccessToken")
        else:
            token = response.get("AuthenticationResult", {}).get("AccessToken")

        return {
            "statusCode": 200,
            "body": json.dumps({"token": token})
        }
    except ClientError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": str(e)})
        }