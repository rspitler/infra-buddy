import click

from infra_buddy.aws.s3 import S3Buddy
from infra_buddy.context.deploy import Deploy
from testcase_parent import ParentTestCase


class TemplateManagerTestCase(ParentTestCase):
    def tearDown(self):
        pass

    @classmethod
    def setUpClass(cls):
        super(TemplateManagerTestCase, cls).setUpClass()

    def test_s3_template(self):
        s3 = S3Buddy(self.test_deploy_ctx)
        template = ParentTestCase._get_resource_path("template_tests/test-template.zip")
        s3.upload(file=template)
        key = s3._get_upload_bucket_key_name(template,file_name=None)
        s3_url = "s3://{bucket}/{key}".format(bucket=self.test_deploy_ctx.cf_bucket_name, key=key)
        self._validate_template(self.test_deploy_ctx.template_manager, {"type": "s3", "location": s3_url})

    def _validate_template(self, manager, template_def, service_name="test-template", has_config_dir=True):
        manager._load_templates({service_name: template_def})
        template = manager.get_known_service(service_name)
        self.assertIsNotNone(template, "Failed to locate service")
        self.assertIsNotNone(template.get_template_file_path(), "Failed to locate template file")
        self.assertIsNotNone(template.get_parameter_file_path(), "Failed to locate param file")
        if has_config_dir:
            self.assertIsNotNone(template.get_config_dir(), "Failed to locate config dir")

    def test_github_template(self):
        self._validate_template(self.test_deploy_ctx.template_manager,
                                service_name='vpc',
                                has_config_dir=False,
                                template_def={
                                    "type": "github",
                                    "owner": "AlienVault-Engineering",
                                    "repo": "service-template-vpc"
                                })


    def test_invalid_template(self):
        template = self.test_deploy_ctx.template_manager.get_resource_service(
                ParentTestCase._get_resource_path("template_tests/invalid_template"))
        self.assertIsNone(template,"Failed to return none for invalid template")

        template = self.test_deploy_ctx.template_manager.get_resource_service(
                ParentTestCase._get_resource_path("template_tests/valid_template"))
        self.assertIsNotNone(template,"Failed to return deploy for valid template")

    def test_validate_defaults(self):

        template = self.test_deploy_ctx.template_manager.get_resource_service(ParentTestCase._get_resource_path("template_tests/valid_template"))
        deploy = Deploy(stack_name=self.test_deploy_ctx.resource_stack_name,
                                              template=template,
                                              deploy_ctx=self.test_deploy_ctx)
        self.assertEqual(deploy.defaults['app'],"foo","Failed to render template value")
        self.assertEqual(deploy.defaults['val'],"discrete","Failed to render template value")
        self.assertEqual(self.test_deploy_ctx.expandvars("${KEY_NAME}"),"unit-test-foo","Failed to render expected key value")
        self.test_deploy_ctx.push_deploy_ctx(deploy)
        self.assertEqual(self.test_deploy_ctx.stack_name,"unit-test-foo-bar-{}-resources".format(self.run_random_word),"Failed to update stack_name")
        self.assertEqual(self.test_deploy_ctx.expandvars("${app}"),"foo","Failed to render deploy default")
        self.assertEqual(self.test_deploy_ctx.expandvars("${KEY_NAME}"),"override","Failed to render deploy default")
        self.test_deploy_ctx.pop_deploy_ctx()
        self.assertEqual(self.test_deploy_ctx.stack_name,"unit-test-foo-bar-{}".format(self.run_random_word),"Failed to update stack_name after pop")
        self.assertEqual(self.test_deploy_ctx.expandvars("${KEY_NAME}"),"unit-test-foo","Failed to render expected key value after pop")

        # self.assertEqual(deploy.defaults['val'],"discrete","Failed to call func")
