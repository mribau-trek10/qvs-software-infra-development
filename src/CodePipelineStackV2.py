import aws_cdk as cdk
import constructs
from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import aws_codepipeline_actions as codepipeline_actions
from aws_cdk import aws_iam as iam
from aws_cdk import aws_codebuild as codebuild

class QVSPipelineStack(cdk.Stack):

    def __init__(self, scope: constructs.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a CodeBuild project
        codebuild_project = codebuild.PipelineProject(
            self,
            "CodeBuildProject",
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "commands": [
                            "n 18.7.1",
                            "make build"
                        ]
                    },
                }
            }),
            environment=codebuild.BuildEnvironment(
                compute_type=codebuild.ComputeType.LARGE
            )
        )

        # Create an IAM role for CodePipeline
        pipeline_role = iam.Role(
            self,
            "PipelineRole",
            assumed_by=iam.ServicePrincipal("codepipeline.amazonaws.com")
        )

        # Add policy statements to the role
        pipeline_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["*"],
                resources=["*"]
            )
        )

        # Create a CodePipeline
        pipeline = codepipeline.Pipeline(
            self,
            "Pipeline",
            pipeline_name="QVSPipeline",
            role=pipeline_role
        )

        # Create artifacts for source and build actions
        source_output = codepipeline.Artifact("SourceOutput")
        build_output = codepipeline.Artifact("BuildOutput")

        # Add source action from GitHub repository
        source_action = codepipeline_actions.GitHubSourceAction(
            action_name="Source",
            owner="mribau-trek10",
            repo="qvs-software-infra-development",
            branch="main",
            oauth_token=cdk.SecretValue.secrets_manager("qvs-github-token"),
            output=source_output
        )
        pipeline.add_stage(
            stage_name="Source",
            actions=[source_action]
        )

        # Add build action using CodeBuild project
        build_action = codepipeline_actions.CodeBuildAction(
            action_name="Build",
            project=codebuild_project,
            input=source_output,
            outputs=[build_output]
        )
        pipeline.add_stage(
            stage_name="Build",
            actions=[build_action]
        )

app = cdk.App()
QVSPipelineStack(app, "QVSPipelineStack")
app.synth()