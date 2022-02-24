from typing import List
import yaml
import os
from git import Repo

PROJECTS_TERRAFORM = {
  'admin': 'projects/wtp-admin/terraform',
  'api': 'projects/wtp-api/terraform',
  'client': 'projects/wtp-client/terraform',
  'infra': 'projects/wtp-infra/terraform'
}

PROJECTS_SRC = {
  'admin': 'projects/wtp-admin/src',
  'api': 'projects/wtp-api/src',
  'client': 'projects/wtp-client/src',
  'infra': 'projects/wtp-infra/src'
}

git_dir = os.path.join(os.getcwd(), '../.git')
repo = Repo(git_dir) 
# TODO: uncomment this when we're ready to use live git changes
# diff: str = repo.git.diff('HEAD~1..HEAD', name_only=True)
# diff_list = diff.split('\n')
diff_list = ["projects/wtp-infra/terraform/terraform.tf"]

print(diff_list)

def contains_project(project: str, change: str):
  if project not in change:
    return False
  else:
    return True

def has_changes(project: str, project_changes: List[str]) -> bool:
  changes = list(filter(lambda x: contains_project(project, x), project_changes))
  # print(project_changes)

  return len(changes) > 0

def load_job(path: str) -> dict:
  with open(path, 'r') as job_file:
    job = yaml.load(job_file, Loader=yaml.FullLoader)
    return job
  

has_admin_terraform_changes = has_changes(PROJECTS_TERRAFORM['admin'], diff_list)
has_api_terraform_changes = has_changes(PROJECTS_TERRAFORM['api'], diff_list)
has_client_terraform_changes = has_changes(PROJECTS_TERRAFORM['client'], diff_list)
has_infra_terraform_changes = has_changes(PROJECTS_TERRAFORM['infra'], diff_list)
has_admin_src_changes = has_changes(PROJECTS_SRC['admin'], diff_list)
has_api_src_changes = has_changes(PROJECTS_SRC['api'], diff_list)
has_client_src_changes = has_changes(PROJECTS_SRC['client'], diff_list)
has_infra_src_changes = has_changes(PROJECTS_SRC['infra'], diff_list)


# print(has_admin_terraform_changes)
# print(has_api_terraform_changes)
# print(has_client_terraform_changes)
# print(has_client_terraform_changes)
# print(has_admin_src_changes)
# print(has_api_src_changes)
# print(has_client_src_changes)
# print(has_client_src_changes)


# load circleci templates
circle_ci_base_dir = os.path.join(os.getcwd(), 'jobs/base.yml')

with open(circle_ci_base_dir, 'r') as file:
    doc = yaml.load(file, Loader=yaml.FullLoader)

    # print(type(doc))
    # print(doc)

    if has_infra_terraform_changes:
      # terraform_plan = os.path.join(os.getcwd(), 'jobs/terraform_plan.yml')
      # terraform_plan_job = load_job(terraform_plan)
      # approve_terraform_plan = os.path.join(os.getcwd(), 'jobs/approve-terraform-plan.yml')
      # approve_terraform_plan_job = load_job(approve_terraform_plan)
      hello_world = os.path.join(os.getcwd(), 'jobs/hello_world.yml')
      hello_world_job = load_job(hello_world)

      # doc['workflows']["wtp_infra"]["jobs"]["terraform_plan"] = terraform_plan_job

      # print(type(doc["workflows"]["wtp_infra"]["jobs"]))


      # doc['workflows']["wtp_infra"]["terraform"] = approve_terraform_plan_job

      doc["jobs"] = list()

      doc["jobs"].append(hello_world)
      doc["workflows"]["wtp_infra"] = dict()
      doc["workflows"]["wtp_infra"]["jobs"] = list()
      doc["workflows"]["wtp_infra"]["jobs"].append(hello_world_job)
        
    sort_file = yaml.dump(doc)
    print(sort_file)

# conditionally apply workflows with params
