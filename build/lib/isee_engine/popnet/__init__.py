import importlib
import json
import sys
import os

# Load the correct dipde:
sys.path.insert(0, os.path.join('/data/mat/iSee_temp_shared', 'packages', 'dipde'))
import dipde

# Load the shared lgnmodel:
sys.path.insert(0, os.path.join('/data/mat/iSee_temp_shared', 'packages', 'lgnmodel'))
import lgnmodel

