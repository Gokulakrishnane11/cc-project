"""REST API routes for VM Resource Allocation Simulator."""

from __future__ import annotations
from typing import Any, Dict, List, Tuple
from flask import Blueprint, jsonify, request, Response
from werkzeug.exceptions import HTTPException

from app.models.host import Host
from app.models.vm import VirtualMachine
from app.services.simulator import SimulationEngine

api_bp = Blueprint("api", __name__, url_prefix="/api")


def error_response(code: str, message: str, status_code: int) -> Tuple[Response, int]:
    """Generate a standardized JSON error response."""
    return jsonify({
        "error": {
            "code": code,
            "message": message,
        }
    }), status_code


def parse_hosts(hosts_raw: Any) -> List[Host]:
    """Parse and validate a list of host configuration dictionaries.
    
    Args:
        hosts_raw: Raw input expected to be a list of dicts.
        
    Returns:
        List of validated Host instances.
        
    Raises:
        TypeError: If input is not a list or elements are not dictionaries.
        ValueError: If required fields are missing or duplicate IDs exist.
    """
    if not isinstance(hosts_raw, list):
        raise TypeError("Field 'hosts' must be a list of host configurations.")

    hosts: List[Host] = []
    seen_ids = set()

    for idx, item in enumerate(hosts_raw):
        if not isinstance(item, dict):
            raise TypeError(f"Host at index {idx} must be a dictionary/object, got {type(item).__name__}.")

        for required_key in ("host_id", "total_cpu", "total_ram"):
            if required_key not in item:
                raise ValueError(f"Host at index {idx} is missing required field: '{required_key}'.")

        host_id = item["host_id"]
        if not isinstance(host_id, str) or not host_id.strip():
            raise ValueError(f"Host at index {idx} has an invalid 'host_id'. It must be a non-empty string.")

        host_id_clean = host_id.strip()
        if host_id_clean in seen_ids:
            raise ValueError(f"Duplicate host_id detected: '{host_id_clean}'.")
        seen_ids.add(host_id_clean)

        host = Host(
            host_id=host_id_clean,
            total_cpu=item["total_cpu"],
            total_ram=item["total_ram"],
            name=item.get("name"),
        )
        hosts.append(host)

    return hosts


def parse_vms(vms_raw: Any) -> List[VirtualMachine]:
    """Parse and validate a list of VM request dictionaries.
    
    Args:
        vms_raw: Raw input expected to be a list of dicts.
        
    Returns:
        List of validated VirtualMachine instances.
        
    Raises:
        TypeError: If input is not a list or elements are not dictionaries.
        ValueError: If required fields are missing or duplicate IDs exist.
    """
    if not isinstance(vms_raw, list):
        raise TypeError("Field 'vms' must be a list of virtual machine configurations.")

    vms: List[VirtualMachine] = []
    seen_ids = set()

    for idx, item in enumerate(vms_raw):
        if not isinstance(item, dict):
            raise TypeError(f"VM at index {idx} must be a dictionary/object, got {type(item).__name__}.")

        for required_key in ("vm_id", "cpu_required", "ram_required"):
            if required_key not in item:
                raise ValueError(f"VM at index {idx} is missing required field: '{required_key}'.")

        vm_id = item["vm_id"]
        if not isinstance(vm_id, str) or not vm_id.strip():
            raise ValueError(f"VM at index {idx} has an invalid 'vm_id'. It must be a non-empty string.")

        vm_id_clean = vm_id.strip()
        if vm_id_clean in seen_ids:
            raise ValueError(f"Duplicate vm_id detected: '{vm_id_clean}'.")
        seen_ids.add(vm_id_clean)

        vm = VirtualMachine(
            vm_id=vm_id_clean,
            cpu_required=item["cpu_required"],
            ram_required=item["ram_required"],
        )
        vms.append(vm)

    return vms


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint confirming API service status."""
    return jsonify({
        "status": "healthy",
        "service": "VM Resource Allocation Simulator API",
        "version": "1.0.0",
    }), 200


@api_bp.route("/algorithms", methods=["GET"])
def list_algorithms():
    """List all supported allocation algorithms and their descriptions."""
    algorithms = [
        {
            "id": "first_fit",
            "name": "First Fit",
            "description": (
                "Sequentially assigns each VM to the first physical host with sufficient "
                "available CPU cores and RAM capacity."
            ),
        },
        {
            "id": "best_fit",
            "name": "Best Fit",
            "description": (
                "Selects the feasible physical host that leaves the minimum normalized "
                "residual-resource score (tightest fit) after the proposed allocation."
            ),
        },
        {
            "id": "round_robin",
            "name": "Round Robin",
            "description": (
                "Evenly distributes VM allocations cyclically across physical hosts, "
                "verifying CPU and RAM limits before placement."
            ),
        },
    ]
    return jsonify({"algorithms": algorithms}), 200


@api_bp.route("/simulate", methods=["POST"])
def simulate_workload():
    """Run a single allocation algorithm against provided hosts and VMs."""
    if not request.is_json:
        return error_response(
            "INVALID_REQUEST",
            "Request body must be valid JSON with 'Content-Type: application/json'.",
            400,
        )

    data = request.get_json(silent=True)
    if data is None:
        return error_response("INVALID_REQUEST", "Malformed or empty JSON body.", 400)

    if not isinstance(data, dict):
        return error_response("INVALID_REQUEST", "Request payload must be a JSON object.", 400)

    # Validate required top-level fields
    for field in ("algorithm", "hosts", "vms"):
        if field not in data:
            return error_response("MISSING_FIELD", f"Missing required field: '{field}'.", 400)

    algo_name = data["algorithm"]
    if not isinstance(algo_name, str) or not algo_name.strip():
        return error_response("INVALID_TYPE", "Field 'algorithm' must be a non-empty string.", 400)

    try:
        hosts = parse_hosts(data["hosts"])
        vms = parse_vms(data["vms"])
        result = SimulationEngine.run_algorithm(
            algorithm_name=algo_name,
            hosts=hosts,
            vms=vms,
        )
        return jsonify(result), 200
    except ValueError as val_err:
        err_msg = str(val_err)
        if "Unknown allocation algorithm" in err_msg:
            return error_response("UNKNOWN_ALGORITHM", err_msg, 400)
        return error_response("VALIDATION_ERROR", err_msg, 400)
    except TypeError as type_err:
        return error_response("VALIDATION_ERROR", str(type_err), 400)
    except Exception:
        return error_response(
            "INTERNAL_SERVER_ERROR",
            "An unexpected internal error occurred during simulation.",
            500,
        )


@api_bp.route("/compare", methods=["POST"])
def compare_workloads():
    """Run all three algorithms under identical initial conditions and compare results."""
    if not request.is_json:
        return error_response(
            "INVALID_REQUEST",
            "Request body must be valid JSON with 'Content-Type: application/json'.",
            400,
        )

    data = request.get_json(silent=True)
    if data is None:
        return error_response("INVALID_REQUEST", "Malformed or empty JSON body.", 400)

    if not isinstance(data, dict):
        return error_response("INVALID_REQUEST", "Request payload must be a JSON object.", 400)

    for field in ("hosts", "vms"):
        if field not in data:
            return error_response("MISSING_FIELD", f"Missing required field: '{field}'.", 400)

    try:
        hosts = parse_hosts(data["hosts"])
        vms = parse_vms(data["vms"])
        comparison = SimulationEngine.compare_all(hosts=hosts, vms=vms)
        return jsonify(comparison), 200
    except (ValueError, TypeError) as val_err:
        return error_response("VALIDATION_ERROR", str(val_err), 400)
    except Exception:
        return error_response(
            "INTERNAL_SERVER_ERROR",
            "An unexpected internal error occurred during comparison.",
            500,
        )


# ---------------------------------------------------------------------------
# Blueprint Error Handlers
# ---------------------------------------------------------------------------

@api_bp.app_errorhandler(404)
def handle_not_found(e):
    return error_response("NOT_FOUND", "The requested resource was not found.", 404)


@api_bp.app_errorhandler(405)
def handle_method_not_allowed(e):
    return error_response("METHOD_NOT_ALLOWED", "The HTTP method is not allowed for this endpoint.", 405)


@api_bp.app_errorhandler(500)
def handle_internal_error(e):
    return error_response("INTERNAL_SERVER_ERROR", "An unexpected internal server error occurred.", 500)
