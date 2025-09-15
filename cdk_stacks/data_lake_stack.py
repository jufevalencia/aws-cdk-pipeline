# cdk_stacks/data_lake_stack.py
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_glue as glue,
    RemovalPolicy
)
from constructs import Construct

class DataLakeStack(Stack):
    """
    CDK Stack to provision the foundational resources for the Data Lake.
    This includes the S3 bucket for storage and the Glue Database for cataloging.
    """
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --- S3 Bucket for Raw Data ---
        # This bucket will store the data extracted by the Lambda function.
        self.data_lake_bucket = s3.Bucket(self, "DataLakeBucket",
            # For development purposes, DESTROY allows the bucket to be deleted when the stack is destroyed.
            # In production, this would typically be RETAIN.
            removal_policy=RemovalPolicy.DESTROY,
            # Automatically delete objects in the bucket when the stack is destroyed.
            # Useful for cleaning up development environments.
            auto_delete_objects=True,
            # Enforce best practices for security by blocking all public access.
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL
        )

        # --- AWS Glue Database ---
        # This database will act as a namespace for our tables in the Glue Data Catalog.
        self.glue_database = glue.CfnDatabase(self, "GlueDatabase",
            # The catalog ID is typically your AWS Account ID.
            catalog_id=self.account,
            database_input=glue.CfnDatabase.DatabaseInputProperty(
                name="serverless_data_lake_db",
                description="Database for the serverless data lake."
            )
        )