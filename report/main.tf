provider "aws" {
  region = "eu-west-2"
}

# Lambda function with the specified existing role and image URI from ECR
resource "aws_lambda_function" "c14-fahad-lambda-report" {
  function_name = "c14-fahad-lambda-report"
  
  # Reference the existing IAM role by ARN
  role = "arn:aws:iam::129033205317:role/c14-ridwan-hamid-lambda-role"

  
  package_type  = "Image"
  
  # Use the image URI from the ECR repository
  image_uri = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c14-fahad-ecr-report@sha256:cbb734d56dccbedc945e920f0e3e762d512a8effcf7f4aaa2671fb70f0fe23f2"
  
  architectures = ["x86_64"]

  # Environment variables for your Lambda function
  environment {
    variables = {
      DB_HOST     = var.DB_HOST
      DB_NAME     = var.DB_NAME
      DB_USERNAME = var.DB_USERNAME
      DB_PASSWORD = var.DB_PASSWORD
      DB_PORT     = var.DB_PORT
      DB_SCHEMA   = var.DB_SCHEMA
    }
  }
}
