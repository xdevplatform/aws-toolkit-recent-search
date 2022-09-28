# aws-toolkit-recent-search

This toolkit provides a framework to ingest, process, and store Twitter data. The toolkit leverages Twitter's new [recent search API v2](https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-recent), allowing you to fetch Tweets from the last seven days that match a specific search query. 

Follow the steps below to ingest Tweets into an AWS storage solution.

## What services does this toolkit leverage? 

* This toolkit requires a Twitter developer account and access to the Twitter API. The following two levels of access are free of charge:

  * Essential access gives you 500K Tweets/month
  * Elevated access gives you 2M Tweets/month

* This toolkit leverages AWS Lambda and RDS. Pricing information for AWS services can be found [here](https://aws.amazon.com/pricing/).

## Prerequisites

1. A Twitter Developer account: [sign up here](https://developer.twitter.com/en/apply-for-access).
2. A bearer token to authenticate your requests to the Twitter API: [refer to this documentation](https://developer.twitter.com/en/docs/authentication/oauth-2-0/bearer-tokens).
3. An AWS account (the [free tier](http://aws.amazon.com/free) is sufficient): [create an account here](https://portal.aws.amazon.com/billing/signup#/start/email).

## Implementation: step-by-step guide

### Step 1: Create RDS MySQL database and associated tables

1. Start by cloning this repository locally.

2. Create an RDS MySQL database: 

* Login to your AWS account and navigate to AWS CloudFormation.
* Select "Create stack".
* Select "Template is ready" and "Upload a template file". 
* Using "Choose file", upload the file entitled rds.yaml (you can find this in the cloudformation directory of this GitHub repository, which you cloned locally).
* Select "Next".
* Enter a stack name, for example "rds". Other parameter values will be automatically populated from the CloudFormation template you just uploaded. Select "Next".
* No need to Configure stack options and Advanced options. Select "Next".
* Scroll to the bottom of the page and select "Create stack".
* The database is now being created. This will take several minutes to complete.

3. Once the process is complete, make a note of your database endpoint. To find this: 

* Navigate to the "Stacks" section of CloudFormation. 
* Select the stack you just created: "rds". 
* Select "Resources", then click on the Physical ID "mysqldbtweets".This will take you to the RDS Management Console. 
* Scroll down to the "Connect" section and you will find the endpoint there. This will look something like: `mysqldbtweets.xxxxxxxxxxxx.us-east-1.rds.amazonaws.com`

4. Add a new inbound rule:

* Navigate to Amazon RDS, select "DB Instances", and click into your database "mysqldbtweets". 
* In the "Connectivity & security" tab, under "Security", click on the default VPC security group. 
* Select the "Inbound rules" tab.
* Click "Edit inbound rules" and "Add rule". Your new rule should have the following properties: 
  * Type: All traffic 
  * Source: IPv4 and 0.0.0.0/0

5. Before you move onto the next step, be sure to check that your DB instance has a Status of "Available". You can check this by navigating to RDS > DB Instances. Note that, once created, it can take up to 20 minutes for your database instance to become available for network connections.

6. You’re now ready to create tables in the database you just created:

* Navigate to your local version of the GitHub repository. Rename `event_data_creds_example.json` to `event_data_creds.json`
* On line 8, add the endpoint url for your database, the one you fetched in point 3 above. Make sure to add `event_data_creds.json` to your `.gitignore` file to avoid sharing your credentials.
* Install PyMySQL. You can install it with pip in your local command line: `$ python3 -m pip install PyMySQL`
* In your local command line, navigate to the main aws-toolkit-recent-search directory, and run the following script: `$ python3 create_tables.py`

7. (Optional) You can download [DBeaver Lite](https://dbeaver.com/download/) to connect to your database and view the tables you created.

### Step 2: Deploy the ETL code as an AWS Lambda function

1. Locate lambda/script.zip in your local version of the GitHub repository.

2. Back in your AWS account, navigate to AWS Lambda.

3. Select "Create function".

4. Select "Author from scratch".

5. Name the function "etl-recent-search".

6. Under Runtime, select Python 3.9.

7. Click on "Create Function".

8. Select "Upload from" > ".zip file" and upload the lambda/script.zip file.

9. Click "Save".

10. Under "Configuration" > "General configuration": edit the Timeout to 15 minutes.

### Step 3: Create function URL to trigger the Lambda function

1. Navigate to the AWS Lambda Functions page and select the "etl-recent-search" function you created in Step 2.

2. Under "Configuration", select "Function URL" and create a new function URL.

3. For auth type, select "NONE".

4. Make a note of the function URL you just created. The URL format will be as follows: `https://<url-id>.lambda-url.<region>.on.aws`. This URL will be used in Step 4 to form a cURL command that can trigger the Lambda function to fetch Tweets and store them.

5. Navigate to the AWS IAM Roles Console and create a new role with the following properties:

* Trusted entity type – "AWS service"
* Use case – Lambda
* Permissions – AWSLambdaBasicExecutionRole
* Role name – lambda-url-role

### Step 4: Run cURL command to fetch and store Tweets of interest 

1. Build the following cURL command. Make sure to add your own details and credentials where relevant, specifically: 

* Replace `https://<url-id>.lambda-url.<region>.on.aws` with the function URL you generated in the above step.
* The "query" line determines what Tweets will get returned. You can edit this query to fetch Tweets of interest to you. Twitter's [documentation](https://developer.twitter.com/en/docs/authentication/oauth-2-0/bearer-tokens) contains details on how to build a search query.
* Edit the start and end times to be within the last 7 days (if your start and end times are older than the last 7 days, the query will fail).
* Add your Twitter bearer token. Twitter's [documentation](https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query) explains how to generate and find your bearer token.
* Next to "endpoint" add the database endpoint you generated in Step 1.3 above.
* If required, edit the region to reflect the region in which you created your database.

``` curl
curl -X POST \
    'https://<url-id>.lambda-url.<region>.on.aws' \
    -H 'Content-Type: application/json' \
    -d '{
    "query": "((ipad OR iphone) apple) -is:retweet lang:en",
    "max_results": 100,
    "start_time": "2022-08-22T13:00:00Z",
    "end_time": "2022-08-22T13:30:00Z",
    "bearer_token": "XXXXX",
    "endpoint": "XXXXX",
    "user": "dbadmin",
    "region": "us-east-1a",
    "dbname": "searchtweetsdb",
    "password": "Test1230"
}'
```

2. In your local command line run this cURL command. This will trigger the AWS Lambda function you deployed in Step 2, connect to the Twitter API to fetch Tweets of interest and store these in the database you created in Step 1.

Please note: the cURL command might take a while to run if you are fetching large amounts of data. Anything that takes longer than 15 minutes will automatically timeout. If this happens, try reducing the time period between your "start_time" and "end_time". 

If you run into any errors, you may want to check the logs to troubleshoot the cause of the issue. You can find these under "Lambda" > "Functions" > "etl-recent-search" > "Monitor" > "logs". There you’ll find a more verbose description of the error.
## Notes
This toolkit in intended as an example framework that quickly fetches, parses, and stores Twitter data.

The following [data objects](https://developer.twitter.com/en/docs/twitter-api/data-dictionary/introduction) are extracted and persisted:

* Tweets (including hastags, cashtags, annotations, mentions, urls)
* Users

The following data objects will not be persisted:

* Media
* Polls
* Places
* Spaces
* Lists