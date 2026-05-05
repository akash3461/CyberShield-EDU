import os
import sys

# Add both project root and backend folder to sys.path
# This ensures that both 'backend.app' and just 'app' work reliably
proj_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, proj_root)
sys.path.insert(0, os.path.join(proj_root, "backend"))
