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
