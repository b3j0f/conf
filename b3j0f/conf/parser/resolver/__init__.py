"""lang package"""

__all__ = [
    'ExprResolver', 'ResolverRegistry', 'names', 'resolve', 'register',
    'loadresolvers', 'defaultname', 'resolvepy'
]

from .base import ExprResolver
from .registry import (
    ResolverRegistry, names, resolve, register, loadresolvers, defaultname
)
from .lang import resolvepy
