import boto3
import click

from infra_buddy.commandline import cli
from infra_buddy.context.deploy_ctx import DeployContext
from infra_buddy.deploy.cloudformation_deploy import CloudFormationDeploy
from infra_buddy.template.template import NamedLocalTemplate
from infra_buddy.utility import print_utility


@cli.command(name='bootstrap')
@click.argument('--environments', nargs=-1)
@click.pass_obj
def deploy_cloudformation(deploy_ctx,application,environments):
    # type: (DeployContext,str,list) -> None
    do_command(deploy_ctx,application,environments)


def do_command(deploy_ctx,application,environments):
    # type: (DeployContext,str,list) -> None
    client = boto3.client('ec2',region_name=deploy_ctx.region)
    for env in environments:
        key_name = "{env}-{application}".format(env=env, application=application)
        res = client.create_key_pair(KeyName=key_name)
        with open('{key_name}.pem'.format(key_name=key_name),'w') as new_pem:
            new_pem.writelines(res['KeyMaterial'])
            
        
        
        




