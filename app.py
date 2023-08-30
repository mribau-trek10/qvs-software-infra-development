import aws_cdk as cdk
import constructs

from src.api_gateway.ordering_connector_2 import OrderingConnectorApiGatewayStackV2
from src.ddb.endpoints_table import Endpoints
from src.CodePipelineStack import CodePipelineStack

class InitialDeploymentStack(cdk.Stack):

    def __init__(self, scope: constructs.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        Endpoints(self, "EndpointsTable")
        OrderingConnectorApiGatewayStackV2(self, "OrderingConnectorApiGatewayStackV2")

app = cdk.App()

InitialDeploymentStack(app, "InitialDeploymentStack")

CodePipelineStack(app, "ApiGatewayLambdaDynamoPipelineStack")

app.synth()