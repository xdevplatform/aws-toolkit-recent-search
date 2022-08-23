# aws-toolkit-recent-search

## Set up
 
1. Run CloudFormation script to create RDS database with MySQL engine.
    * Login to your AWS account and navigate to AWS CloudFormation.
    * Select "Create stack".
    * Select "Template is ready" and "Upload a template file". Using "Choose file", upload `rds.yaml` (you can find this in the `cloudformation` directory of this GitHub repository).
    * Select "Next".
    * Enter a stack name, e.g. "rds". Other parameter values will be automatically populated from the CloudFormation template you just uploaded. Select "Next".
    * No need to Configure stack options and Advanced options. Select "Next". 
    * Scroll to the bottom of the page and select "Create stack".
    * The database is now being created. This will take several minutes to complete.
    * Once complete, make a note of the database endpoint. To find this: select the stack "rds" > "Resources" > click on the Physical ID "mysqldbtweets". Scroll down to the "Connect" section and you will find the endpoint there. This will look something like: mysqldbtweets.cv7ewtjysjfy.us-east-1.rds.amazonaws.com

2. Rename `event_data_creds_example.json` to `event_data_creds.json` and add missing credentials, specifically: Twitter developer app bearer token and the database endpoint you saved in the previous step. Make sure to add `event_data_creds.json` to your `.gitignore` file to avoid sharing your credentials.

3. Navigate to your local command line. From the main `aws-toolkit-recent-search` directory, run the following script to create tables in the database: `$ python3 create_tables.py`

4. Upload ETL code to Lambda:
    * Download `lambda/script.zip` locally from GitHub repo
    * Log in to your AWS account and Search for Lambda in the "Search for services" search box.
    * Navigate to AWS Lambda and select "Create function".
    * Select "Author from scratch".
    * Name the function "etl-recent-search".
    * Under Runtime, select Python 3.9.
    * Click on "Create Function".
    * Select "Upload from" > ".zip file" and upload the `script.zip` file previously downloaded.
    * Click "Save".
    * Under "Configuration" > "General configuration": edit the Timeout to 15 minutes.

5. Test the Lambda function in the AWS Console: 
    * Use the following test event (make sure to replace XXX with your own credentials and to update the start and end times to be within the last 7 days): 
    ```
    {
        "query": "((ipad OR iphone) apple -is:retweet)",
        "max_results": 100,
        "start_time": "2022-08-21T13:00:00Z",
        "end_time": "2022-08-21T13:30:00Z",
        "bearer_token": "XXX",
        "endpoint": "XXX",
        "user": "dbadmin",
        "dbname": "searchtweetsdb",
        "password": "Test1230"
    }
    ```
    *  In the Lambda handler: comment out lines 11-22 and uncomment lines 24-33 (as per comment in the script).
    * You can now test the Lambda function in the AWS console. When you test the function, new data will be added to your DB instance.

**[The above works / has been tested. Review/ work on the following steps]**

6. Create a function URL (this will later be used to trigger the lambda function and fetch Tweets):
    * From the Lambda function page: under "Configuration", select "Function URL".
    * Auth type, select "NONE".
    * Copy the function URL you just created for later. This will have the following format: `https://<url-id>.lambda-url.<region>.on.aws`.
    * Navigate to IAM Roles and create a new role with the following properties:
      * Trusted entity – AWS Lambda.
      * Permissions – AWSLambdaBasicExecutionRole.
      * Role name – lambda-url-role.
9. Build curl command, it will look something like the following. Make sure to update with your own credentials and change the start/end time to be in the last 7 days. If you want to change the query, refer to this [documentation](https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query) for the syntax required. 
```
curl -X POST \
    'https://<url-id>.lambda-url.<region>.on.aws' \
    -H 'Content-Type: application/json' \
    -d '{
    "query": "((ipad OR iphone) apple) -is:retweet",
    "max_results": 100,
    "start_time": "2022-08-22T13:00:00Z",
    "end_time": "2022-08-22T13:30:00Z",
    "bearer_token": "XXX",
    "endpoint": "XXX",
    "user": "dbadmin",
    "region": "us-east-1a",
    "dbname": "searchtweetsdb",
    "password": "Test1230"
}'
```
7. Run curl command.

## Notes
This toolkit in intended as an example framework that quickly fetches, parses, and analyzes Twitter data.

The following [data objects](https://developer.twitter.com/en/docs/twitter-api/data-dictionary/introduction) are extracted and persisted:

* Tweets (including hastags, cashtags, annotations, mentions, urls)
* Users

The following data objects will not be persisted:

* Media
* Polls
* Places
* Spaces
* Lists

## Note to self, useful resources (not to include in tutorial instructions)

* Follow the guidlines here for creating the zip file referred to in Step 4: https://www.danielherediamejias.com/python-scripts-aws-lambda/
* Create a function URL: https://docs.aws.amazon.com/lambda/latest/dg/urls-tutorial.html 
