import aws_cdk as cdk
from aws_cdk import (
    aws_apigateway as apigateway,
    aws_lambda as _lambda,
    aws_iam as iam,
)
import constructs

class ApiGatewayLambdaStack(cdk.Stack):

    def __init__(self, scope: constructs.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create the API Gateway
        api = apigateway.SpecRestApi(
            self, "OrderingConnector",
            api_definition=apigateway.ApiDefinition.from_asset("src/api_gateway/swagger.json")
        )

        # Create the Lambda function
        lambda_function = _lambda.Function(
            self, "LambdaFunction",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="lambda.lambda_handler",
            code=_lambda.Code.from_asset("src/lambda"),
        )

        # Create the Lambda integration for API Gateway
        integration = apigateway.LambdaIntegration(
            lambda_function,
            credentials_role=self._create_execution_role(lambda_function)
        )

        # Add a resource and method to the API Gateway
        api_resource = api.root.add_resource("v1-order-product")
        api_resource.add_method(
            "POST",
            integration=integration
        )

        # Set the default method options for the resource
        api_resource.add_method(
            "OPTIONS",  # HTTP OPTIONS method
            integration=apigateway.MockIntegration(
                integration_responses=[
                    {
                        "statusCode": "200",
                        "responseParameters": {
                            "method.response.header.Access-Control-Allow-Headers": "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                            "method.response.header.Access-Control-Allow-Origin": "'*'",
                        },
                    }
                ],
                passthrough_behavior=apigateway.PassthroughBehavior.WHEN_NO_MATCH,
                request_templates={
                    "application/json": '{"statusCode": 200}'
                },
            ),
            method_responses=[
                {
                    "statusCode": "200",
                    "responseParameters": {
                        "method.response.header.Access-Control-Allow-Headers": True,
                        "method.response.header.Access-Control-Allow-Methods": True,
                        "method.response.header.Access-Control-Allow-Origin": True,
                    },
                }
            ]
        )

    def _create_execution_role(self, lambda_function: _lambda.Function) -> iam.Role:
        role = iam.Role(
            self, "APIGatewayExecutionRole",
            assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com")
        )
        
        # Grant permission for Lambda function to be invoked by API Gateway
        lambda_function.grant_invoke(role)

        # Create a statement to allow API Gateway to invoke the API
        #api_id = self.format_arn(service="execute-api", resource="*", region="*", account="*")
        #api_invoke_statement = iam.PolicyStatement(
            #effect=iam.Effect.ALLOW,
            #actions=["execute-api:Invoke"],
            #resources=[f"{api_id}/*"],
            #principals=[iam.ArnPrincipal("arn:aws:iam::378337867365:role/IhmOrderingGatewayService-ServiceRole@gamma")]
        #)

        # Add the statement to the role's policy
        #role.add_to_policy(api_invoke_statement)

        lambda_function.add_to_role_policy(iam.PolicyStatement(
            actions=["execute-api:Invoke"],
            resources=["*"]
        ))

        return role

app = cdk.App()
ApiGatewayLambdaStack(app, "ApiGatewayLambdaStack")
app.synth()