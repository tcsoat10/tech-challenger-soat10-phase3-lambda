from http import HTTPStatus
import logging
import os
import json
from cognito_service import CognitoService
from package.pycpfcnpj.cpfcnpj import validate as validate_cpf_cnpj

def validate_cpf(cpf_value: str) -> bool:
    if not cpf_value:
        return False

    try:
        return validate_cpf_cnpj(cpf_value)
    except Exception:
        return False

REQUIRED_FIELDS_CREATE_USER = ['name', 'email', 'birthdate', 'cpf']
REQUIRED_FIELDS_LOGIN_USER = ['cpf']

def build_response(status_code, body):
    return {
        'statusCode': status_code,
        'body': body
    }

def handle_create_user(cognito_service: CognitoService, data: dict):
    cpf = data.get('cpf')
    try:
        exists_user = cognito_service.exists_user_in_user_pool(cpf)
        if exists_user is True:
            return build_response(HTTPStatus.CONFLICT.value, 'User already exists, log in with CPF')
        else:
            new_user = cognito_service.create_user_in_user_pool(data)
            if new_user is True:
                return build_response(HTTPStatus.CREATED.value, 'User created successfully')
    except Exception as e:
        logging.exception(f'Error checking user: {str(e)}')
        raise

def handle_login_user(cognito_service: CognitoService, data: dict):
    cpf = data.get('cpf')
    if not cpf:
        return build_response(HTTPStatus.BAD_REQUEST.value, 'Missing CPF')
    
    if not validate_cpf(cpf):
        return build_response(HTTPStatus.BAD_REQUEST.value, 'Invalid CPF')
    
    try:
        exists_user = cognito_service.exists_user_in_user_pool(cpf)
        if exists_user is True:
            return build_response(HTTPStatus.OK.value, 'User exists')
        else:
            return build_response(HTTPStatus.NOT_FOUND.value, 'User does not exist')
    except Exception as e:
        logging.exception(f'Error checking user: {str(e)}')
        raise

def lambda_handler(event, context):
    data = json.loads(event['body'])
    
    is_create_user_data = sorted(data.keys()) == sorted(REQUIRED_FIELDS_CREATE_USER)
    is_login_user_data = sorted(data.keys()) == sorted(REQUIRED_FIELDS_LOGIN_USER)

    user_pool_id = os.getenv('USER_POOL_ID')
    if not user_pool_id:
        return build_response(HTTPStatus.INTERNAL_SERVER_ERROR.value, 'Server configuration error: USER_POOL_ID not set.')
        
    cognito_service = CognitoService(user_pool_id=user_pool_id)

    if is_create_user_data:       
        return handle_create_user(cognito_service, data)
    elif is_login_user_data:
        return handle_login_user(cognito_service, data)
        
    return build_response(HTTPStatus.BAD_REQUEST.value, 'Invalid request format')
