module "lambda_python" {
  source            = "../../"

  pip_path          = "/Users/alex/anaconda3/bin/pip"

  lambda_name       = "did_link"
  lambda_api_name   = "did_link_api"
  lambda_iam_name   = "did_link_iam"

  api_stage_name    = "dev"
  api_resource_path = "did_link"
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