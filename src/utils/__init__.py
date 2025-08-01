"""
Utility modules
===============

Contains utility functions and helper modules.
"""

# Import only the essential korean_airlines_corp_codes module to avoid config dependency issues
try:
    from .korean_airlines_corp_codes import *
except ImportError as e:
    print(f"⚠️ Warning: Could not import korean_airlines_corp_codes: {e}")

# Only import get_corp_codes if configuration is available
try:
    from .get_corp_codes import *
except ImportError as e:
    print(f"⚠️ Warning: Could not import get_corp_codes (likely missing config): {e}")

__all__ = []