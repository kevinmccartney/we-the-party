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

def get_changed_projects(projects: List[Dict], changes: List[str]) -> Set[str]:
  changed_projects = []
  
  for project in projects:
    for key, value in project.items():
      if has_changes(value, changes):
        # append project to changed list
        changed_projects.append(key)

  # # filter out non-unique values
  return set(changed_projects)


def load_template(path: str) -> dict:
  with open(os.path.join(os.getcwd(), path), 'r') as job_file:
    job = yaml.load(job_file, Loader=yaml.FullLoader)
    
    return job
