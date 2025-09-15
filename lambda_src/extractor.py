# lambda_src/extractor.py
import os
import requests
import pandas as pd
import awswrangler as wr
from datetime import datetime, timezone

# Get the destination S3 bucket name from an environment variable
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
API_URL = "https://jsonplaceholder.typicode.com/users"

def handler(event, context):
    """
    Lambda handler function to extract data from a public API,
    transform it into a Pandas DataFrame, and save it as a Parquet file in S3.
    """
    if not S3_BUCKET_NAME:
        raise ValueError("Environment variable S3_BUCKET_NAME is not set.")

    print(f"Fetching data from API: {API_URL}")
    response = requests.get(API_URL)
    response.raise_for_status() # Raise an exception for bad status codes
    
    data = response.json()
    df = pd.json_normalize(data) # Flatten the nested JSON structure

    # Create a partitioned path based on the current date for efficiency
    current_date = datetime.now(timezone.utc)
    s3_path = (
        f"s3://{S3_BUCKET_NAME}/raw/users/"
        f"year={current_date.year}/"
        f"month={current_date.month:02d}/"
        f"day={current_date.day:02d}/"
    )

    print(f"Writing {len(df)} records to Parquet at: {s3_path}")
    
    # Use AWS Data Wrangler to write the DataFrame to S3 as Parquet
    result = wr.s3.to_parquet(
        df=df,
        path=s3_path,
        dataset=True,
        mode="overwrite"
    )

    print("Successfully wrote data to S3.")
    return {
        "statusCode": 200,
        "body": f"Successfully processed and wrote data to {result['paths'][0]}"
    }