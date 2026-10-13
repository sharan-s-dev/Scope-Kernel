"""Root shortcut for ScopeKernel UI app."""

import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Run scopekernel app
from scopekernel.ui.app import *  # noqa: F401, F403
