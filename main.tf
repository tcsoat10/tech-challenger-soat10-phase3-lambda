terraform {
  backend "remote" {
    organization = "10SOAT_TC3"
    workspaces {
      name = "lambda_auth"
    }
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.52.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# Lambda Function
resource "aws_lambda_function" "lambda_function" {
  function_name = var.lambda_function_name
  role          = var.aws_role_arn
  handler       = var.lambda_handler
  runtime       = var.lambda_runtime
  filename      = "${path.module}/build/${var.lambda_zip_file}"

  source_code_hash = filebase64sha256("${path.module}/build/${var.lambda_zip_file}")
  timeout          = 10
  memory_size      = 128
}

# Cognito User Pool
resource "aws_cognito_user_pool" "user_pool" {
  name = "${var.lambda_function_name}-user-pool"
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }
}

resource "aws_cognito_user_pool_client" "user_pool_client" {
  name            = "${var.lambda_function_name}-user-pool-client"
  user_pool_id    = aws_cognito_user_pool.user_pool.id
  generate_secret = false
}

# API Gateway HTTP API
resource "aws_apigatewayv2_api" "http_api" {
  name          = "${var.lambda_function_name}"
  protocol_type = "HTTP"
}

resource "aws_lambda_permission" "apigw_invoke" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_function.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id                 = aws_apigatewayv2_api.http_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.lambda_function.invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "post_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /login"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true
}

output "lambda_function_name" {
  value = aws_lambda_function.lambda_function.function_name
}

output "cognito_user_pool_id" {
  value = aws_cognito_user_pool.user_pool.id
}

output "cognito_user_pool_client_id" {
  value = aws_cognito_user_pool_client.user_pool_client.id
}

output "api_endpoint" {
  value = aws_apigatewayv2_api.http_api.api_endpoint
}
