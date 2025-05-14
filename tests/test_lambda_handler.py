import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from http import HTTPStatus
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import main

class TestLambdaHandler(unittest.TestCase):
    @patch('main.CognitoService')
    @patch('main.validate_cpf')
    def test_handler_missing_cpf(self, mock_validate_cpf, mock_cognito_service):
        event = {}
        context = {}
        
        result = main.handler(event, context)
        
        self.assertEqual(result['statusCode'], 400)
        self.assertEqual(result['body'], 'Missing CPF')
        mock_validate_cpf.assert_not_called()
    
    @patch('main.CognitoService')
    @patch('main.validate_cpf')
    def test_handler_invalid_cpf(self, mock_validate_cpf, mock_cognito_service):
        event = {'cpf': '123.456.789-00'}
        context = {}
        mock_validate_cpf.return_value = False
        
        result = main.handler(event, context)
        
        self.assertEqual(result['statusCode'], 400)
        self.assertEqual(result['body'], 'Invalid CPF')
        mock_validate_cpf.assert_called_once_with('123.456.789-00')
    
    @patch('main.os.getenv')
    @patch('main.CognitoService')
    @patch('main.validate_cpf')
    def test_handler_user_exists(self, mock_validate_cpf, mock_cognito_service, mock_getenv):
        event = {'cpf': '529.982.247-25'}
        context = {}
        mock_validate_cpf.return_value = True
        mock_getenv.return_value = 'test-pool-id'
        
        mock_cognito_instance = MagicMock()
        mock_cognito_instance.exists_user_in_user_pool.return_value = True
        mock_cognito_service.return_value = mock_cognito_instance
        
        result = main.handler(event, context)
        
        self.assertEqual(result['statusCode'], HTTPStatus.OK)
        self.assertEqual(result['body'], 'User exists')
        mock_cognito_instance.exists_user_in_user_pool.assert_called_once_with('529.982.247-25')
    
    @patch('main.os.getenv')
    @patch('main.CognitoService')
    @patch('main.validate_cpf')
    def test_handler_user_does_not_exist(self, mock_validate_cpf, mock_cognito_service, mock_getenv):
        event = {'cpf': '529.982.247-25'}
        context = {}
        mock_validate_cpf.return_value = True
        mock_getenv.return_value = 'test-pool-id'
        
        mock_cognito_instance = MagicMock()
        mock_cognito_instance.exists_user_in_user_pool.return_value = False
        mock_cognito_service.return_value = mock_cognito_instance
        
        result = main.handler(event, context)
        
        self.assertEqual(result['statusCode'], HTTPStatus.NOT_FOUND)
        self.assertEqual(result['body'], 'User does not exist')
    
    @patch('main.os.getenv')
    @patch('main.CognitoService')
    @patch('main.validate_cpf')
    def test_handler_service_exception(self, mock_validate_cpf, mock_cognito_service, mock_getenv):
        event = {'cpf': '529.982.247-25'}
        context = {}
        mock_validate_cpf.return_value = True
        mock_getenv.return_value = 'test-pool-id'
        
        mock_cognito_instance = MagicMock()
        mock_cognito_instance.exists_user_in_user_pool.side_effect = Exception("Service error")
        mock_cognito_service.return_value = mock_cognito_instance
        
        result = main.handler(event, context)
        
        self.assertEqual(result['statusCode'], HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertEqual(result['body'], "Service error")

if __name__ == '__main__':
    unittest.main()
