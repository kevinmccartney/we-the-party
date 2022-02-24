import yaml
import os
from git import Repo
from pathlib import Path

from utils import get_changed_projects, load_template, Dumper, build_terraform_workflow
from constants import PROJECTS

git_dir = os.path.join(os.getcwd(), "../.git")
repo = Repo(git_dir)
# TODO: uncomment this when we're ready to use live git changes
# diff: str = repo.git.diff('HEAD~1..HEAD', name_only=True)
# diff_list = diff.split('\n')
diff_list = [
    "projects/wtp_infra/terraform/terraform.tf",
    "projects/wtp_infra/src/ping/ping.py",
]

base = load_template("jobs/base.yml")

changed_projects = get_changed_projects(PROJECTS, diff_list)

for project in changed_projects.items():
    (project_name, change_status) = project

    if change_status["terraform"] == True:
        build_terraform_workflow(project_name, base)

    if change_status["src"] == True:
        print(project_name, "has src changes")

        deploy_infra_lambdas_job = load_template("jobs/deploy_infra_lambdas.yml")

        if "jobs" not in base:
            base["jobs"] = dict()
        base["jobs"]["deploy_infra_lambdas"] = deploy_infra_lambdas_job

        if "workflows" not in base:
            base["workflows"][project] = dict()

        base["workflows"][project]["jobs"] = list()
        base["workflows"][project]["jobs"].append("deploy_infra_lambdas")

circle_ci_generated_config = os.path.join(
    os.getcwd(), "../.circleci/generated_config.yml"
)

with open(circle_ci_generated_config, "w") as write_file:
    documents = yaml.dump(base, write_file, Dumper=Dumper, sort_keys=False)

# https://stackoverflow.com/a/39591068
# contents = Path(circle_ci_generated_config).read_text()
# print(contents)
