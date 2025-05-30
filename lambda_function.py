from http import HTTPStatus
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

def lambda_handler(event, context):
    data = json.loads(event['body'])
    cpf = data.get('cpf')

    if not cpf:
        return {
            'statusCode': HTTPStatus.BAD_REQUEST.value,
            'body': 'Missing CPF'
        }
    
    if not validate_cpf(cpf):
        return {
            'statusCode': HTTPStatus.BAD_REQUEST.value,
            'body': 'Invalid CPF'
        }

    user_pool_id = os.getenv('USER_POOL_ID')
    if not user_pool_id:
        return {
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value,
            'body': 'Server configuration error: USER_POOL_ID not set.'
        }
        
    cognito_service = CognitoService(user_pool_id=user_pool_id)
    
    try:
        exists_user = cognito_service.exists_user_in_user_pool(cpf)
        if exists_user:
            return {
                'statusCode': HTTPStatus.OK.value,
                'body': 'User exists'
            }
        else:
            return {
                'statusCode': HTTPStatus.NOT_FOUND.value,
                'body': 'User does not exist'
            }
    except Exception as e:
        return {
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value,
            'body': f'Error checking user: {str(e)}'
        }

