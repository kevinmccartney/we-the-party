# Python

## Debugging

To debug Python code you can use any of the launch configurations or pdb. It really depends on what kind of process you're trying to debug.

### Applications

#### _PID_

---

If it's a server (like the wtp_cli command `wtp start aws-lambda`), you can attach to the PID using `Python: Attach using Process Id` debug configuration.

#### _Port_

---

For processes that run & exit (like wtp_cli `wtp generate config`) are probably better debugged by attaching to a process (that is suspended until a debugger is attached) on a port by using the `pytest` module like this -

```bash
python -m pytest --listen localhost:5678 --wait-for-client projects/wtp_cli/wtp_cli/cli.py generate config vscode
```

Then using the `Python: Remote Attach` debug configuration.

#### _Current File_

---

You can also debug files on a per file basis using the `Python: Current File` debug configuration.

**NOTE:**

You may need to add a name check & run the code you're interested in if you're using the current file method like this -

```python
if __name__ == "__main__":
    foo()
```

### Tests

#### _PID_

---

It would be pretty hard to attach to a test process to a PID when running the `pytest` module, so you might want to do something like this -

```python
import os
import sys

import pytest


def run_tests():
    print(os.getpid())

    path = sys.argv[1:]

    input("Press any button to run the tests")

    exit_code = pytest.main()

    print(f"py.test exited with code: {exit_code}")


if __name__ == "__main__":
    run_tests()
```

The PID of the process will be printed out & you can use `Python: Attach using Process Id` to debug the tests.

#### _Port_

---

You can also debug over a port by using a command like this -

```bash
python -m debugpy --listen 5678 --wait-for-client -m pytest
```

Then use the `Python: Remote Attach` debug target.

### IDE Support

We haven't tested in other IDEs besides VS Code. `pytest` is using the Debugger Adapter Protocol, but it looks like adapters using are almost exclusively targeting VS Code. If you want to use another IDE besides VS Code (which is allowed but not supported), you are responsible for finding debugging methods of your own. If all else fails, there's always `pdb` :wink:
