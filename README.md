# Deploy Did Backend 

Terraform modules which where we are dploying basic did poc functionalities.

## Usage 
There are 4 different lambdas that achieve the poc functionality:
* credentials_create
* credentials_sign
* did_create
* did_link

## How to deploy
Each lambda is deployed indipendetly.
NOTE: MAKE SURE YOU ARE LOGGED IN WITH YOUR AWS CREDENTIALS AND HAVE A DYNAMO TABLE NAMED "DID_POC".

Run the following command to see them. 
`cd terraform-aws-lambda-python/examples ; ls -l`
now simply `cd` into each folder and run `terraform init ;terraform apply` to deploy each endpoints

