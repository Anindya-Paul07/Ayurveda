import os
import sys

# Get the absolute path to the project root (one level above the tests directory)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Insert the project root at the beginning of sys.path if not already added
if project_root not in sys.path:
    sys.path.insert(0, project_root)