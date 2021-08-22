module "lambda_python" {
  source            = "../../"

  pip_path          = "/Users/alex/anaconda3/bin/pip"

  lambda_name       = "credentials_sign"
  lambda_api_name   = "credentials_sign_api"
  lambda_iam_name   = "credentials_sign_iam"

  api_stage_name    = "dev"
  api_resource_path = "credentials_sign"
  api_http_method   = "POST"
  
  iam_additional_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "dynamodb:*"
        ],
        "Resource": "arn:aws:dynamodb:*"
      }
    ]
  })
}