import logging
import boto3

class CognitoService:
    def __init__(self):
        self.cognito_client = boto3.client('cognito-idp')
        pools = self.cognito_client.get_paginator('list_user_pools')
        for page in pools.paginate(MaxResults=60):
            for pool in page['UserPools']:
                if pool['Name'] == 'lambda_auth-user-pool':
                    self.user_pool_id = pool['Id']
                break
    
    def exists_user_in_user_pool(self, username: str):
        try:
            self.cognito_client.admin_get_user(
                UserPoolId=self.user_pool_id,
                Username=username
            )
            return True
        except self.cognito_client.exceptions.NotAuthorizedException:
            return "The username or password is incorrect."
        except self.cognito_client.exceptions.UserNotFoundException:
            return "The user does not exist."
        except Exception as e:
            return str(e)
    
    def create_user_in_user_pool(self, user_data: dict):
        name = user_data.get('name')
        email = user_data.get('email')
        username = user_data.get('cpf')
        birthdate = user_data.get('birthdate')
        try:
            response = self.cognito_client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=username,
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': email
                    },
                    {
                        'Name': 'name',
                        'Value': name
                    },
                    {
                        'Name': 'birthdate',
                        'Value': birthdate
                    },
                    {
                        'Name': 'preferred_username',
                        'Value': username
                    }
                ],
                MessageAction='SUPPRESS'  # Suppress the welcome message
            )
            return True
        except Exception as e:
            logging.exception(f'Error creating user: {str(e)}')
            raise
