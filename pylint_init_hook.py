import os
import sys

projects = ("wtp_admin_api", "wtp_api", "wtp_cli")

for project in projects:
    sys.path.append(os.path.join(os.getcwd(), "projects", project))
