from aws_cdk import pipelines as cpipelines
from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_iam as iam
from aws_cdk.pipelines import CodePipelineSource
from typing import List



import constructs
import aws_cdk as cdk

from src.api_gateway.ordering_connector_2 import OrderingConnectorApiGatewayStackV2
from src.ddb.endpoints_table import Endpoints

class CodePipelineStack(cdk.Stack):

    def __init__(self, scope: constructs.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create the pipeline
        pipeline = cpipelines.CodePipeline(
            self, 'Pipeline',
            pipeline_name='QVSPipeline',
            synth=cpipelines.CodeBuildStep(
                'Synth',
                input=CodePipelineSource.git_hub(
                    owner='trek10inc',
                    repo='qvs-software-infra-development',
                    branch='main',
                    access_token_secret=cdk.SecretValue.plain_text('glpat-PyGsEsWAyCUuR46FetU1')
                ),
                commands=[
                    'npm ci',
                    'npx cdk synth',
                    'npm run deploy-ci'
                ],
                build_environment=codebuild.BuildEnvironment(
                    compute_type=codebuild.ComputeType.LARGE
                ),
                role_policy_statements=[
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=['*'],
                        resources=['*']
                    )
                ]
            )
        )

        # Create instances of the stacks
        ordering_connector_stack = OrderingConnectorApiGatewayStackV2(self, "OrderingConnectorStack")
        endpoints_stack = Endpoints(self, "EndpointsStack")

        # Add deployment stages
        self.add_deployment_stage(pipeline, 'Sandbox', 'sandbox-account-id', 'sandbox-region', [ordering_connector_stack, endpoints_stack])
        self.add_deployment_stage(pipeline, 'Production', 'production-account-id', 'production-region', [ordering_connector_stack, endpoints_stack])

    def add_deployment_stage(self, pipeline: cpipelines.CodePipeline, stage_name: str, account_id: str, region: str, stacks: List[cdk.Stack]):
        # Create a new stage for deployment
        stage = pipeline.add_stage(
            stage_name=stage_name,
            actions=[
                cpipelines.CloudFormationCreateUpdateStackAction(
                    action_name=f'Deploy{stage_name}',
                    account=account_id,
                    region=region,
                    stack_name=f'YourStackName-{stage_name}',
                    template_path=cpipelines.SynthAction.template_output_path(pipeline.synth),
                    admin_permissions=True
                )
            ]
        )

        # Add stacks to the stage
        for stack in stacks:
            stage.add_stack_dependency(stack)
    

app = cdk.App()
CodePipelineStack(app, "CodePipelineStack")
app.synth()