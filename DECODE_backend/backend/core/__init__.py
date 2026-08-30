"""
DECODE core package.

Keep package initialization lightweight.

Individual modules should be imported explicitly
by the code that needs them.

This prevents circular imports between:

core
    ↔
services
"""


__all__ = []
