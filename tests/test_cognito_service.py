import unittest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cognito_service import CognitoService

class TestCognitoService(unittest.TestCase):
    @patch('boto3.client')
    def setUp(self, mock_boto3_client):
        self.mock_client = MagicMock()
        mock_boto3_client.return_value = self.mock_client
        self.cognito_service = CognitoService(user_pool_id='test-pool-id')
    
    def test_exists_user_successful(self):
        self.mock_client.admin_get_user.return_value = {'Username': 'test-user'}
        result = self.cognito_service.exists_user_in_user_pool('test-user')

        self.assertTrue(result)
        self.mock_client.admin_get_user.assert_called_once_with(
            UserPoolId='test-pool-id',
            Username='test-user'
        )
    
    def test_user_not_found(self):
        not_auth_exception = self.mock_client.exceptions.UserNotFoundException()
        self.mock_client.admin_get_user.side_effect = not_auth_exception
        result = self.cognito_service.exists_user_in_user_pool('non-existent-user')
        self.assertEqual(result, "The user does not exist.")
    
    def test_not_authorized(self):
        not_auth_exception = self.mock_client.exceptions.NotAuthorizedException()
        self.mock_client.admin_get_user.side_effect = not_auth_exception
        result = self.cognito_service.exists_user_in_user_pool('unauthorized-user')
        self.assertEqual(result, "The username or password is incorrect.")
    
    def test_general_exception(self):
        self.mock_client.admin_get_user.side_effect = Exception("Some AWS error")
        result = self.cognito_service.exists_user_in_user_pool('error-user')
        self.assertEqual(result, "Some AWS error")

if __name__ == '__main__':
    unittest.main()
