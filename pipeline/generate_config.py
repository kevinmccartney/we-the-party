import yaml
import os
from git import Repo
from pathlib import Path

from utils import get_changed_projects, load_template, Dumper
from constants import PROJECTS_SRC, PROJECTS_TERRAFORM

# https://stackoverflow.com/a/30682604
yaml.Dumper.ignore_aliases = lambda *args : True

git_dir = os.path.join(os.getcwd(), '../.git')
repo = Repo(git_dir) 
# TODO: uncomment this when we're ready to use live git changes
# diff: str = repo.git.diff('HEAD~1..HEAD', name_only=True)
# diff_list = diff.split('\n')
diff_list = ["projects/wtp-infra/terraform/terraform.tf"]

base = load_template('jobs/base.yml')

changed_projects = get_changed_projects([PROJECTS_SRC, PROJECTS_TERRAFORM], diff_list)

if 'infra_tf' in changed_projects:
  terraform_plan = os.path.join(os.getcwd(), 'jobs/terraform_plan.yml')
  terraform_plan_job = load_template(terraform_plan)
  approve_terraform_plan = os.path.join(os.getcwd(), 'jobs/approve-terraform-plan.yml')
  approve_terraform_plan_job = load_template(approve_terraform_plan)
  approve_terraform_plan = os.path.join(os.getcwd(), 'jobs/approve-terraform-plan.yml')
  approve_terraform_plan_job = load_template(approve_terraform_plan)
  terraform_apply = os.path.join(os.getcwd(), 'jobs/terraform-apply.yml')
  terraform_apply_job = load_template(terraform_apply)

  base["jobs"] = dict()
  base["jobs"]["terraform_plan"] = terraform_plan_job
  base["jobs"]["terraform_apply"] = terraform_apply_job
  base["workflows"]["wtp_infra"] = dict()
  base["workflows"]["wtp_infra"]["jobs"] = list()
  base["workflows"]["wtp_infra"]["jobs"].append({
    "terraform_plan": {
      "project": "wtp_infra"
    }
  })
  base["workflows"]["wtp_infra"]["jobs"].append({
    "approve_terraform_plan": approve_terraform_plan_job
  })
  base["workflows"]["wtp_infra"]["jobs"].append({
    "terraform_apply": {
      "project": "wtp_infra",
      "requires": ["approve_terraform_plan"]
    }
  })

circle_ci_generated_config = os.path.join(os.getcwd(), '../.circleci/generated_config.yml')

with open(circle_ci_generated_config, 'w') as write_file:
  documents = yaml.dump(base, write_file, Dumper=Dumper)

# https://stackoverflow.com/a/39591068
contents = Path(circle_ci_generated_config).read_text()
print(contents)

# conditionally apply workflows with params
