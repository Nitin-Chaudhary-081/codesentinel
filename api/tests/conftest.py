"""Test configuration."""

import os

# Isolate tests from the live dev database: tests create/drop their own DB,
# never touching codesentinel_dev.db. Must be set before any `src` import.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_codesentinel.db")
