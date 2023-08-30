import aws_cdk as cdk

from aws_cdk import (
    aws_iam as iam,
    aws_dynamodb as dynamodb,
)
import constructs

class BasicTable(constructs.Construct):
    def __init__(
        self,
        scope: constructs.Construct,
        id: str,
        **kwargs
    ):
        super().__init__(scope, id, **kwargs)

        self.__table = dynamodb.Table(
            self,
            id,
            partition_key=dynamodb.Attribute(
                name="storeId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )

    @property
    def table(self):
        return self.__table

class Endpoints(BasicTable):
    def __init__(
        self,
        scope: constructs.Construct,
        id: str,
        **kwargs
    ):
        super().__init__(scope, id, **kwargs)

app = cdk.App()
stack = cdk.Stack(app, "EndpointsTableStack")  # Create a Stack
Endpoints(stack, "EndpointsTable")  # Create the Endpoints table within the Stack
app.synth()