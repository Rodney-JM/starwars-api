import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps
from flask import request, jsonify
import logging

from config import Config

# configurando o logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DECORATORS
