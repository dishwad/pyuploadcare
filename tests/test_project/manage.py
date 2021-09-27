#!/usr/bin/env python

import os

from django.core import management


if "DJANGO_SETTINGS_MODULE" not in os.environ:
    os.environ["DJANGO_SETTINGS_MODULE"] = "test_project.settings"


if __name__ == "__main__":
    management.execute_from_command_line()
