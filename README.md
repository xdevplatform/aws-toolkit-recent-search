# aws-toolkit-recent-search

1. Run CloudFormation script to create RDS database with MySQL engine.
2. Create tables within DB [TO DO].
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
4. Add required credentials in `event_data.json`.
5. Change start and end times in `event_data.json`.
6. Change query in `event_data.json` ([documentatio](https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query) for how to build a query).
7. Run  curl command. [TO DO]
8. ETC. [TO DO]
