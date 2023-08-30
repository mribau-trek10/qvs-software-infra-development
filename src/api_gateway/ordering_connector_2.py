import aws_cdk as cdk
from aws_cdk import aws_iam as iam
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_lambda

import constructs
import json

class OrderingConnectorApiGatewayStackV2(cdk.Stack):

    def __init__(self, scope: constructs.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create IAM Role
        api_gateway_role = iam.Role(
            self, "AmazonOrderingConnectorAPIGatewayCloudWatchRole",
            assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonAPIGatewayPushToCloudWatchLogs"
                )
            ]
        )

         # Add trust relationship for Lambda
        api_gateway_role.assume_role_policy.add_statements(
            iam.PolicyStatement(
                actions=["sts:AssumeRole"],
                effect=iam.Effect.ALLOW,
                principals=[iam.ServicePrincipal("lambda.amazonaws.com")]
            )
        )
        
        # Create API Gateway
        api = apigateway.RestApi(
            self, "AmazonOrderingConnectorAPIGateway",
            rest_api_name="OrderingConnector",
            description="Ordering Gateway Connector API to pass purchased cart items, shopper identity"
        )

        # Create Lambda Function
        lambda_function = self.create_lambda_function(api_gateway_role, api.rest_api_id)

        # Create Lambda Integration
        lambda_integration = apigateway.LambdaIntegration(
            handler=lambda_function,
            proxy=True,
            credentials_role=api_gateway_role
        )

        # Create Execution Role and grant permission to API Gateway
        execution_role = self._create_execution_role(lambda_function)

        # Method Definitions
        method_definitions = [
            {
                "path": "/v1/order/authorize/charges",
                "method": "POST",
            },
            {
                "path": "/v1/order/cancel/charges",
                "method": "POST",
            },
            {
                "path": "/v1/order/capture/charges",
                "method": "POST",
            },
            {
                "path": "/v1/order/product",
                "method": "POST",
            },
            {
                "path": "/v1/order/products",
                "method": "POST",
            },
            {
                "path": "/v1/order/purchases",
                "method": "POST",
            },
            # Add more method definitions as needed
        ]

        # Create Methods
        for method_def in method_definitions:
            sanitized_path = method_def["path"].replace("/", "_").replace("-", "_").replace(".", "_")
            resource = api.root.add_resource(sanitized_path)
            method_object = resource.add_method(
                http_method=method_def["method"],
                integration=lambda_integration,
                request_models={"application/json": apigateway.Model.EMPTY_MODEL}
            )

    def create_lambda_function(self, role: iam.Role, api_gateway_id: str):
    # This method creates and returns the Lambda function
        lambda_function = aws_lambda.Function(
            self, "OrderingConnectorLambda",
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            handler="lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset(path="src/lambda"),
            role=role,
        )
        
        # Construct the resource ARN
        resource_arn = f"arn:aws:execute-api:{self.region}:{self.account}:{api_gateway_id}/*"

        # Grant permission for Lambda function to be invoked by API Gateway
        lambda_function.add_permission(
            "InvokePermission",
            action="lambda:InvokeFunction",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            source_arn=resource_arn,
        )
        
        return lambda_function
    
    def _create_execution_role(self, lambda_function: aws_lambda.Function) -> iam.Role:
        role = iam.Role(
            self, "APIGatewayExecutionRole",
            assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com")
        )
        
        # Grant permission for Lambda function to be invoked by API Gateway
        lambda_function.grant_invoke(role)

        return role

app = cdk.App()
OrderingConnectorApiGatewayStackV2(
    app, "OrderingConnectorApiGatewayStackV2",
    env={'region': 'us-east-1'}
)
app.synth()