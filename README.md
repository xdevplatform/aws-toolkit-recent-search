# aws-toolkit-recent-search

1. Run CloudFormation script to create RDS database with MySQL engine.
2. Create tables within DB **[TO DO]**.
3. Upload ETL code to Lambda:
    * Download `lambda/script.zip` locally from GitHub repo
    * Log in to your AWS account and Search for Lambda in the "Search for services" search box.
    * Navigate to AWS Lambda and select "Create function".
    * Select "Author from scratch".
    * Name the function "etl-recent-search".
    * Under Runtime, select Python 3.9.
    * Click on "Create Function".
    * Select "Upload from" > ".zip file" and upload the `script.zip` file previously downloaded.
    * Click "Save".
    * Under "Configuration", edit the Timeout to 15 minutes.
4. Create a function URL (this will later be used to trigger the lambda function and fetch Tweets):
    * Under "Configuration", select "Function URL".
    * Auth type, select "AWS_IAM".
    * Copy the function URL you just created for later. This will have the following format: `https://<url-id>.lambda-url.<region>.on.aws`.
5. Add required credentials in `event_data.json`.
6. Change start and end times in `event_data.json`.
7. Change query in `event_data.json` ([documentatio](https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query) for how to build a query).
8. Run  curl command. **[IN PROGRESS]**
    * Create [function URL](https://docs.aws.amazon.com/lambda/latest/dg/lambda-urls.html).
    * Attempted following steps
        * Create execution role, as described [here](https://docs.aws.amazon.com/lambda/latest/dg/urls-tutorial.html).
        * Add `AWSLambdaVPCAccessExecutionRole` to execution role as described [here](https://bobbyhadz.com/blog/aws-lambda-provided-execution-role-does-not-have-permissions).
        * Add VPC.
        * **[CONNECTION TO FUNCTION URL IS STILL NOT WORKING. NEED TO FIGURE OUT WHY.]**
9. ETC. **[TO DO]**
