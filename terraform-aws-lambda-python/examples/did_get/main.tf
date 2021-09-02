module "lambda_python" {
  source            = "../../"

  pip_path          = "/Users/alex/anaconda3/bin/pip"

  lambda_name       = "did_get"
  lambda_api_name   = "did_get_api"
  lambda_iam_name   = "did_get_iam"

  api_stage_name    = "dev"
  api_resource_path = "did_get"
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
