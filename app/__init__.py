"""Flask Application Factory for VM Resource Allocation Simulator."""

from typing import Any, Dict, Optional
from flask import Flask, render_template
from app.routes.api import api_bp

__version__ = "1.0.0"


def create_app(test_config: Optional[Dict[str, Any]] = None) -> Flask:
    """Create and configure an instance of the Flask application.
    
    Args:
        test_config: Optional dictionary containing configuration overrides for testing.
        
    Returns:
        Configured Flask application instance.
    """
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder="templates",
        static_folder="static",
    )

    # Default configuration
    app.config.from_mapping(
        SECRET_KEY="dev-simulator-key-for-college-project",
        JSON_SORT_KEYS=False,
    )

    if test_config is not None:
        app.config.update(test_config)

    # Register API blueprint
    app.register_blueprint(api_bp)

    @app.route("/", methods=["GET"])
    def index():
        """Serve the simulation dashboard frontend."""
        return render_template("index.html")

    return app
