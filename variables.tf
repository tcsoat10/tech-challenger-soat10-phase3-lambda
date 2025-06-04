variable "region" {
  default = "us-east-1"
}

variable "lambda_function_name" {
  default = "lambda_auth_test"
}

variable "aws_role_arn" {
  default = "arn:aws:iam::739439895240:role/LabRole"
}

variable "lambda_handler" {
  default = "lambda_function.lambda_handler"
}

variable "lambda_runtime" {
  default = "python3.9"
}

variable "lambda_zip_file" {
  default = "lambda-package.zip"
}
