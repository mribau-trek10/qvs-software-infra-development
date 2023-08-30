import aws_cdk as cdk
import constructs

from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_ec2 as ec2

class VpnStack(cdk.Stack):

    def __init__(self, scope: constructs.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a VPC
        vpc = ec2.Vpc(self, "QVSvpc", max_azs=2)  # max_azs=2 creates a VPC that spans two Availability Zones

        # Create the Site-to-Site VPN
        # Note: This is a simplified example, and you will need to specify more parameters based on your requirements
        customer_gateway = ec2.CustomerGateway(self, "CustomerGateway", 
                                               ip_address="YOUR-CUSTOMER-GATEWAY-IP",  # Replace with your customer gateway IP
                                               type=ec2.VpnConnectionType.IPSEC_TUNNEL)

        vpn = ec2.VpnConnection(self, "VpnConnection", 
                                customer_gateway=customer_gateway,
                                vpc=vpc,
                                static_routes=["10.0.0.0/16"])  # Example static route

        # Lambda Function
        # Note: This Lambda function doesn't have a specified handler since it's just an example
        lambda_function = _lambda.Function(self, "MyLambdaFunction",
                                           runtime=_lambda.Runtime.PYTHON_3_8,
                                           code=_lambda.Code.from_inline("def handler(event, context):\n    pass"),  # Example inline code
                                           handler="index.handler",
                                           vpc=vpc,
                                           vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE))

        # Ensure the Lambda function has the necessary permissions to communicate over the VPN
        # You might need to adjust this based on your VPN's security requirements
        lambda_function.connections.allow_all_outbound()