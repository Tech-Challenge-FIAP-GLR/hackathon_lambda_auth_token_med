import unittest
from unittest.mock import patch, MagicMock
import json
from lambda_function import lambda_handler

class TestLambdaHandler(unittest.TestCase):

    @patch('lambda_function.cognito_client')
    def test_lambda_handler_success(self, mock_cognito_client):
        event = {
            'body': json.dumps({'crm': 'testuser', 'password': 'testpassword'})
        }
        context = {}

        mock_cognito_client.initiate_auth.return_value = {
            'AuthenticationResult': {
                'AccessToken': 'test_token'
            }
        }

        response = lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body'])['token'], 'test_token')

    @patch('lambda_function.cognito_client')
    def test_lambda_handler_new_password_required(self, mock_cognito_client):
        event = {
            'body': json.dumps({'crm': 'testuser', 'password': 'newpassword'})
        }
        context = {}

        mock_cognito_client.initiate_auth.return_value = {
            'ChallengeName': 'NEW_PASSWORD_REQUIRED',
            'Session': 'test_session'
        }
        mock_cognito_client.respond_to_auth_challenge.return_value = {
            'AuthenticationResult': {
                'AccessToken': 'new_test_token'
            }
        }

        response = lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body'])['token'], 'new_test_token')

    def test_lambda_handler_missing_user_or_password(self):
        event = {
            'body': json.dumps({})
        }
        context = {}

        response = lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], 'CRM e/ou senha não fornecidos.')


if __name__ == '__main__':
    unittest.main()
