import boto3

class CognitoService:
    def __init__(self, user_pool_id: str):
        self.cognito_client = boto3.client('cognito-idp')
        self.user_pool_id = user_pool_id
    
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
