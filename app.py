#!/usr/bin/env python3
import aws_cdk as cdk
from cdk_stacks.data_lake_stack import DataLakeStack
from cdk_stacks.etl_stack import EtlStack

app = cdk.App()

# Instantiate the DataLakeStack
data_lake_stack = DataLakeStack(app, "DataLakeStack")
etl_stack = EtlStack(app, "EtlStack", data_lake_stack=data_lake_stack)


app.synth()