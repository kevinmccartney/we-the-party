import os
from typing import Dict, List, Set
import yaml


class Dumper(yaml.Dumper):
    def increase_indent(self, flow=False, *args, **kwargs):
        return super().increase_indent(flow=flow, indentless=False)


def contains_project(project: str, change: str):
    if project not in change:
        return False
    else:
        return True


def has_changes(project: str, project_changes: List[str]) -> bool:
    changes = list(filter(lambda x: contains_project(project, x), project_changes))

    return len(changes) > 0


def get_changed_projects(projects: Dict, changes: List[str]) -> Dict:
    changed_projects = {
        "wtp_admin": {
            "src": False,
            "terraform": False,
        },
        "wtp_api": {
            "src": False,
            "terraform": False,
        },
        "wtp_client": {
            "src": False,
            "terraform": False,
        },
        "wtp_infra": {
            "src": False,
            "terraform": False,
        },
    }

    for project_name, project in projects.items():
        for key, value in project.items():
            print(value)
            if has_changes(value, changes):
                changed_projects[project_name][key] = True

    print(changed_projects)

    return changed_projects


def load_template(path: str) -> Dict:
    with open(os.path.join(os.getcwd(), path), "r") as job_file:
        job = yaml.load(job_file, Loader=yaml.FullLoader)

        return job


def build_terraform_workflow(project: str, base: Dict) -> None:
    terraform_plan_job = load_template("jobs/terraform_plan.yml")
    approve_terraform_plan_job = load_template("jobs/approve_terraform_plan.yml")
    terraform_apply_job = load_template("jobs/terraform_apply.yml")

    if "jobs" not in base:
        base["jobs"] = dict()

    base["jobs"]["terraform_plan"] = terraform_plan_job
    base["jobs"]["terraform_apply"] = terraform_apply_job

    if "workflows" not in base:
        base["workflows"][project] = dict()

    base["workflows"][project]["jobs"].append({"terraform_plan": {"project": project}})
    base["workflows"][project]["jobs"].append(
        {"approve_terraform_plan": approve_terraform_plan_job}
    )
    base["workflows"][project]["jobs"].append(
        {
            "terraform_apply": {
                "project": project,
                "requires": ["approve_terraform_plan"],
            }
        }
    )
