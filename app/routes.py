from .routes_api_v1 import api_v1_bp
from .routes_shell import shell_bp

registered_blueprints = (shell_bp, api_v1_bp)
