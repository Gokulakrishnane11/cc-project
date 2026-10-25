"""Integration tests for Flask REST API routes."""

import json
import pytest
from unittest.mock import patch
from app import create_app


@pytest.fixture
def app():
    """Create Flask application instance configured for testing."""
    test_app = create_app({"TESTING": True})
    return test_app


@pytest.fixture
def client(app):
    """Create a Flask test client."""
    return test_app.test_client() if 'test_app' in locals() else app.test_client()


@pytest.fixture
def sample_payload():
    return {
        "hosts": [
            {"host_id": "h1", "total_cpu": 8, "total_ram": 16, "name": "Host 1"},
            {"host_id": "h2", "total_cpu": 8, "total_ram": 16, "name": "Host 2"},
        ],
        "vms": [
            {"vm_id": "v1", "cpu_required": 2, "ram_required": 4},
            {"vm_id": "v2", "cpu_required": 4, "ram_required": 8},
        ],
    }


# ---------------------------------------------------------------------------
# 1. Health Endpoint Tests
# ---------------------------------------------------------------------------

def test_health_endpoint_success(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data


def test_index_dashboard_endpoint_success(client):
    response = client.get("/")
    assert response.status_code == 200
    html_content = response.get_data(as_text=True)
    assert "VM Resource Allocation Simulator" in html_content
    assert "chart-host-utilization" in html_content



# ---------------------------------------------------------------------------
# 2. Algorithm Listing Endpoint Tests
# ---------------------------------------------------------------------------

def test_algorithms_endpoint_success(client):
    response = client.get("/api/algorithms")
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert "algorithms" in data
    algo_ids = [a["id"] for a in data["algorithms"]]
    assert "first_fit" in algo_ids
    assert "best_fit" in algo_ids
    assert "round_robin" in algo_ids

    for item in data["algorithms"]:
        assert "name" in item
        assert "description" in item


# ---------------------------------------------------------------------------
# 3. Simulate Endpoint Tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("algo", ["first_fit", "best_fit", "round_robin"])
def test_simulate_endpoint_success(client, sample_payload, algo):
    payload = {
        "algorithm": algo,
        "hosts": sample_payload["hosts"],
        "vms": sample_payload["vms"],
    }
    response = client.post("/api/simulate", json=payload)
    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()
    assert data["algorithm_key"] == algo
    assert "metrics" in data
    assert "hosts" in data
    assert "vms" in data
    assert "failed_allocations" in data

    metrics = data["metrics"]
    assert metrics["total_vms"] == 2
    assert metrics["successful_allocations"] == 2
    assert metrics["allocation_success_rate"] == 100.0


# ---------------------------------------------------------------------------
# 4. Compare Endpoint Tests
# ---------------------------------------------------------------------------

def test_compare_endpoint_success(client, sample_payload):
    response = client.post("/api/compare", json=sample_payload)
    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()
    assert "algorithms" in data
    assert "summary" in data
    assert "initial_workload" in data

    assert "first_fit" in data["algorithms"]
    assert "best_fit" in data["algorithms"]
    assert "round_robin" in data["algorithms"]
    assert len(data["summary"]) == 3


# ---------------------------------------------------------------------------
# 5. Missing JSON Body Tests
# ---------------------------------------------------------------------------

def test_simulate_missing_json_body(client):
    response = client.post("/api/simulate", data="", content_type="application/json")
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert data["error"]["code"] == "INVALID_REQUEST"


def test_simulate_non_json_content_type(client):
    response = client.post("/api/simulate", data="plain text data", content_type="text/plain")
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "INVALID_REQUEST"


def test_compare_missing_json_body(client):
    response = client.post("/api/compare")
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "INVALID_REQUEST"


# ---------------------------------------------------------------------------
# 6. Missing Required Fields Tests
# ---------------------------------------------------------------------------

def test_simulate_missing_algorithm_field(client, sample_payload):
    payload = {"hosts": sample_payload["hosts"], "vms": sample_payload["vms"]}
    response = client.post("/api/simulate", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "MISSING_FIELD"
    assert "'algorithm'" in data["error"]["message"]


def test_simulate_missing_hosts_field(client, sample_payload):
    payload = {"algorithm": "first_fit", "vms": sample_payload["vms"]}
    response = client.post("/api/simulate", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "MISSING_FIELD"
    assert "'hosts'" in data["error"]["message"]


def test_compare_missing_vms_field(client, sample_payload):
    payload = {"hosts": sample_payload["hosts"]}
    response = client.post("/api/compare", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "MISSING_FIELD"
    assert "'vms'" in data["error"]["message"]


# ---------------------------------------------------------------------------
# 7. Invalid Host Configuration Tests
# ---------------------------------------------------------------------------

def test_simulate_hosts_not_list(client, sample_payload):
    payload = {
        "algorithm": "first_fit",
        "hosts": "not-a-list",
        "vms": sample_payload["vms"],
    }
    response = client.post("/api/simulate", json=payload)
    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "VALIDATION_ERROR"


def test_simulate_host_missing_cpu(client, sample_payload):
    bad_hosts = [{"host_id": "h1", "total_ram": 16}]
    payload = {
        "algorithm": "first_fit",
        "hosts": bad_hosts,
        "vms": sample_payload["vms"],
    }
    response = client.post("/api/simulate", json=payload)
    assert response.status_code == 400
    assert "total_cpu" in response.get_json()["error"]["message"]


def test_simulate_host_negative_capacity(client, sample_payload):
    bad_hosts = [{"host_id": "h1", "total_cpu": -8, "total_ram": 16}]
    payload = {
        "algorithm": "first_fit",
        "hosts": bad_hosts,
        "vms": sample_payload["vms"],
    }
    response = client.post("/api/simulate", json=payload)
    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "VALIDATION_ERROR"


# ---------------------------------------------------------------------------
# 8. Invalid VM Configuration Tests
# ---------------------------------------------------------------------------

def test_simulate_vms_not_list(client, sample_payload):
    payload = {
        "algorithm": "first_fit",
        "hosts": sample_payload["hosts"],
        "vms": {"vm_id": "v1"},
    }
    response = client.post("/api/simulate", json=payload)
    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "VALIDATION_ERROR"


def test_simulate_vm_boolean_ram(client, sample_payload):
    bad_vms = [{"vm_id": "v1", "cpu_required": 2, "ram_required": True}]
    payload = {
        "algorithm": "first_fit",
        "hosts": sample_payload["hosts"],
        "vms": bad_vms,
    }
    response = client.post("/api/simulate", json=payload)
    assert response.status_code == 400
    assert "boolean" in response.get_json()["error"]["message"]


# ---------------------------------------------------------------------------
# 9. Duplicate IDs Tests
# ---------------------------------------------------------------------------

def test_simulate_duplicate_host_id(client, sample_payload):
    dup_hosts = [
        {"host_id": "h-dup", "total_cpu": 8, "total_ram": 16},
        {"host_id": "h-dup", "total_cpu": 8, "total_ram": 16},
    ]
    payload = {
        "algorithm": "first_fit",
        "hosts": dup_hosts,
        "vms": sample_payload["vms"],
    }
    response = client.post("/api/simulate", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "Duplicate host_id" in data["error"]["message"]


def test_compare_duplicate_vm_id(client, sample_payload):
    dup_vms = [
        {"vm_id": "v-dup", "cpu_required": 2, "ram_required": 4},
        {"vm_id": "v-dup", "cpu_required": 4, "ram_required": 8},
    ]
    payload = {
        "hosts": sample_payload["hosts"],
        "vms": dup_vms,
    }
    response = client.post("/api/compare", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "Duplicate vm_id" in data["error"]["message"]


# ---------------------------------------------------------------------------
# 10. Unknown Algorithm Tests
# ---------------------------------------------------------------------------

def test_simulate_unknown_algorithm(client, sample_payload):
    payload = {
        "algorithm": "genetic_annealing_allocator",
        "hosts": sample_payload["hosts"],
        "vms": sample_payload["vms"],
    }
    response = client.post("/api/simulate", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "UNKNOWN_ALGORITHM"
    assert "Unknown allocation algorithm" in data["error"]["message"]


# ---------------------------------------------------------------------------
# 11. Empty VM Workload Tests
# ---------------------------------------------------------------------------

def test_simulate_empty_workload(client, sample_payload):
    payload = {
        "algorithm": "first_fit",
        "hosts": sample_payload["hosts"],
        "vms": [],
    }
    response = client.post("/api/simulate", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["metrics"]["total_vms"] == 0
    assert data["metrics"]["allocation_success_rate"] == 0.0


# ---------------------------------------------------------------------------
# 12. Empty Host List Tests
# ---------------------------------------------------------------------------

def test_simulate_empty_hosts_list(client, sample_payload):
    payload = {
        "algorithm": "first_fit",
        "hosts": [],
        "vms": sample_payload["vms"],
    }
    response = client.post("/api/simulate", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["metrics"]["total_vms"] == 2
    assert data["metrics"]["successful_allocations"] == 0
    assert data["metrics"]["failed_allocations"] == 2
    assert data["metrics"]["allocation_success_rate"] == 0.0


# ---------------------------------------------------------------------------
# 13. JSON Response Serialization Tests
# ---------------------------------------------------------------------------

def test_json_serialization(client, sample_payload):
    response = client.post("/api/compare", json=sample_payload)
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/json")
    # Verify it can be dumped and re-loaded cleanly
    dumped = json.dumps(response.get_json())
    loaded = json.loads(dumped)
    assert loaded["summary"][0]["algorithm_key"] == "first_fit"


# ---------------------------------------------------------------------------
# 14. HTTP Status Codes and Error Handlers Tests
# ---------------------------------------------------------------------------

def test_not_found_endpoint(client):
    response = client.get("/api/nonexistent_route")
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"]["code"] == "NOT_FOUND"


def test_method_not_allowed(client):
    response = client.get("/api/simulate")  # /api/simulate only allows POST
    assert response.status_code == 405
    data = response.get_json()
    assert data["error"]["code"] == "METHOD_NOT_ALLOWED"


# ---------------------------------------------------------------------------
# 15. Unexpected Internal Exception Handling (No Stack Trace Leak)
# ---------------------------------------------------------------------------

def test_unexpected_internal_exception_handling(client, sample_payload):
    with patch("app.services.simulator.SimulationEngine.run_algorithm") as mock_run:
        mock_run.side_effect = RuntimeError("Fatal DB/driver crash at /secret/path/to/driver.py")
        
        payload = {
            "algorithm": "first_fit",
            "hosts": sample_payload["hosts"],
            "vms": sample_payload["vms"],
        }
        response = client.post("/api/simulate", json=payload)
        assert response.status_code == 500
        data = response.get_json()
        assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
        # Must NOT leak stack trace or internal paths
        assert "secret/path" not in data["error"]["message"]
        assert "Fatal DB" not in data["error"]["message"]
        assert data["error"]["message"] == "An unexpected internal error occurred during simulation."
