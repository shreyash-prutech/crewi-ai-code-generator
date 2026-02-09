"""Utility package for code_genereator.

This package aggregates utility helpers and re-exports selected functions
for convenient access, such as validate_email.
"""

from .validators import validate_email

__all__ = ["validate_email"]
