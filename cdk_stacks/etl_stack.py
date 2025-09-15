1   # cdk_stacks/etl_stack.py
from aws_cdk import (
    Stack,
    aws_lambda_python_alpha as lambda_python,
    aws_iam as iam,
    aws_glue_alpha as glue,
    aws_lakeformation as lakeformation,
    Duration
)
from constructs import Construct
from .data_lake_stack import DataLakeStack

class EtlStack(Stack):
    """
    CDK Stack to provision the ETL components of the data pipeline.
    This includes the data extraction Lambda, the Glue Crawler,
    and the necessary Lake Formation permissions.
    """
    def __init__(self, scope: Construct, construct_id: str, data_lake_stack: DataLakeStack, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --- Data Extraction Lambda Function ---
        data_extractor_lambda = lambda_python.PythonFunction(self, "DataExtractorLambda",
            entry="lambda_src/",
            index="extractor.py",
            handler="handler",
            runtime=lambda_python.Runtime.PYTHON_3_10,
            timeout=Duration.seconds(60),
            environment={
                "S3_BUCKET_NAME": data_lake_stack.data_lake_bucket.bucket_name
            }
        )

        # --- Glue Crawler ---
        crawler_role = iam.Role(self, "GlueCrawlerRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSGlueServiceRole")
            ]
        )

        glue_crawler = glue.Crawler(self, "DataLakeCrawler",
            role=crawler_role,
            database=glue.Database.from_database_name(self, "GlueDatabase", data_lake_stack.glue_database.database_input.name),
            targets=[glue.S3Target(bucket=data_lake_stack.data_lake_bucket, path="raw/users/")],
            configuration={
                "Version": 1.0,
                "CrawlerOutput": {
                    "Partitions": {"AddOrUpdateBehavior": "InheritFromTable"}
                }
            }
        )
        
        # --- Lake Formation Permissions ---
        # Grant the Lambda's role permission to write to the S3 bucket location
        lakeformation.CfnPermissions(self, "LambdaLakeFormationPermissions",
            data_lake_principal=lakeformation.CfnPermissions.DataLakePrincipalProperty(
                data_lake_principal_identifier=data_extractor_lambda.role.role_arn
            ),
            resource=lakeformation.CfnPermissions.ResourceProperty(
                data_location_resource=lakeformation.CfnPermissions.DataLocationResourceProperty(
                    catalog_id=self.account,
                    s3_resource=f"arn:aws:s3:::{data_lake_stack.data_lake_bucket.bucket_name}/raw/users/"
                )
            ),
            permissions=["DATA_LOCATION_ACCESS"]
        )

        # Grant the Crawler's role necessary permissions
        # 1. Permission to read the S3 location
        lakeformation.CfnPermissions(self, "CrawlerS3LakeFormationPermissions",
            data_lake_principal=lakeformation.CfnPermissions.DataLakePrincipalProperty(
                data_lake_principal_identifier=crawler_role.role_arn
            ),
            resource=lakeformation.CfnPermissions.ResourceProperty(
                data_location_resource=lakeformation.CfnPermissions.DataLocationResourceProperty(
                    catalog_id=self.account,
                    s3_resource=f"arn:aws:s3:::{data_lake_stack.data_lake_bucket.bucket_name}/raw/users/"
                )
            ),
            permissions=["DATA_LOCATION_ACCESS"]
        )

        # 2. Permission to create tables in the Glue database
        lakeformation.CfnPermissions(self, "CrawlerDbLakeFormationPermissions",
            data_lake_principal=lakeformation.CfnPermissions.DataLakePrincipalProperty(
                data_lake_principal_identifier=crawler_role.role_arn
            ),
            resource=lakeformation.CfnPermissions.ResourceProperty(
                database_resource=lakeformation.CfnPermissions.DatabaseResourceProperty(
                    catalog_id=self.account,
                    name=data_lake_stack.glue_database.database_input.name
                )
            ),
            permissions=["CREATE_TABLE", "ALTER", "DROP"]
        )