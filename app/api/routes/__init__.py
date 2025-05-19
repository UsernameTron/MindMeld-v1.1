"""
API routes package for the MindMeld application.

This package contains the route modules for different features of the MindMeld API,
such as authentication, sentiment analysis, chat completions, and content rewriting.
"""

from . import sentiment
from .analyze import router as analyze_router
from .auth import router as auth_router
from .chat import router as chat_router
from .data import router as data_router
from .persona import router as persona_router
from .rewrite import router as rewrite_router
