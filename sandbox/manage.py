#!/usr/bin/env python
import os
import sys
import debugpy

def initialize_debugger():
    if not os.getenv("RUN_MAIN"):
        debugpy.listen(("0.0.0.0", 4000))
        debugpy.wait_for_client()


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    from django.core.management import execute_from_command_line
    initialize_debugger()
    execute_from_command_line(sys.argv)
