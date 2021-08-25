
provider "aws" {
  profile = "${var.aws_profile}"
  region = "${var.aws_region}"
  version = "~> 3.0"
}

# This will fetch our account_id, no need to hard code it
data "aws_caller_identity" "current" {}

# Prepare Lambda package (https://github.com/hashicorp/terraform/issues/8344#issuecomment-345807204)
resource "null_resource" "pip" {
  triggers = {
    main         = "${base64sha256(file("lambda/main.py"))}"
    requirements = "${base64sha256(file("requirements.txt"))}"
  }

  provisioner "local-exec" {
    command = "${var.pip_path} install -r ${path.root}/requirements.txt -t lambda/lib"
  }
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.root}/lambda/"
  output_path = "${path.root}/lambda.zip"

  depends_on = [null_resource.pip]
}


resource "aws_lambda_function" "lambda" {
  filename         = "lambda.zip"
  function_name    = "${var.lambda_name}"
  role             = "${aws_iam_role.lambda_iam.arn}"
  handler          = "main.lambda_handler"
  runtime          = "python3.6"
  source_code_hash = "${data.archive_file.lambda_zip.output_base64sha256}"
}

module "apigateway_with_cors" {
  source  = "alparius/apigateway-with-cors/aws"
  version = "0.3.1"
  http_method = "POST"
  stage_name = "dev"
  path_part = "${var.api_resource_path}"

  lambda_function_name = aws_lambda_function.lambda.function_name
  lambda_invoke_arn    = aws_lambda_function.lambda.invoke_arn 
}

# IAM
resource "aws_iam_role" "lambda_iam" {
  name = "${var.lambda_iam_name}"

  assume_role_policy = "${file("${path.module}/policy.json")}"
}

resource "aws_iam_role_policy_attachment" "logs_policy" {
    role       = "${aws_iam_role.lambda_iam.name}"
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "additional_policy" {
  count = "${var.iam_additional_policy != "" ? 1 : 0}"

  name = "${var.lambda_iam_name}-additional-policy"
  role = "${aws_iam_role.lambda_iam.id}"

  policy = "${var.iam_additional_policy}"
}

# CloudWatch 
resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name = "/aws/lambda/${var.lambda_name}"

  retention_in_days = 30
}
