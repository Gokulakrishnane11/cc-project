"""Unit and integration tests for SimulationEngine and Comparison Service."""

import json
import pytest
from app.models.host import Host
from app.models.vm import VirtualMachine
from app.services.simulator import SimulationEngine


@pytest.fixture
def sample_hosts():
    return [
        Host(host_id="host-1", total_cpu=8, total_ram=16, name="Rack 1 - Node A"),
        Host(host_id="host-2", total_cpu=8, total_ram=16, name="Rack 1 - Node B"),
        Host(host_id="host-3", total_cpu=16, total_ram=32, name="Rack 2 - High Mem"),
    ]


@pytest.fixture
def sample_workload():
    return [
        VirtualMachine(vm_id="vm-web-1", cpu_required=2, ram_required=4),
        VirtualMachine(vm_id="vm-db-1", cpu_required=4, ram_required=8),
        VirtualMachine(vm_id="vm-cache-1", cpu_required=2, ram_required=4),
        VirtualMachine(vm_id="vm-batch-1", cpu_required=8, ram_required=16),
        VirtualMachine(vm_id="vm-web-2", cpu_required=2, ram_required=4),
    ]


# ---------------------------------------------------------------------------
# Individual Algorithm Execution Tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("algo_name", ["first_fit", "best_fit", "round_robin", "First Fit", "Best Fit", "Round Robin", "ff", "bf", "rr"])
def test_simulation_engine_runs_each_algorithm(algo_name, sample_hosts, sample_workload):
    result = SimulationEngine.run_algorithm(
        algorithm_name=algo_name,
        hosts=sample_hosts,
        vms=sample_workload,
    )

    assert "algorithm_key" in result
    assert "metrics" in result
    assert "hosts" in result
    assert "vms" in result
    assert "failed_allocations" in result
    assert "execution_steps" in result

    metrics = result["metrics"]
    assert metrics["total_vms"] == len(sample_workload)
    assert metrics["successful_allocations"] + metrics["failed_allocations"] == len(sample_workload)
    assert 0.0 <= metrics["allocation_success_rate"] <= 100.0
    assert 0.0 <= metrics["cpu_utilization"] <= 100.0
    assert 0.0 <= metrics["ram_utilization"] <= 100.0


# ---------------------------------------------------------------------------
# Comparison Engine Tests
# ---------------------------------------------------------------------------

def test_compare_all_structure(sample_hosts, sample_workload):
    comparison = SimulationEngine.compare_all(hosts=sample_hosts, vms=sample_workload)

    assert "algorithms" in comparison
    assert "summary" in comparison
    assert "initial_workload" in comparison

    algos = comparison["algorithms"]
    assert "first_fit" in algos
    assert "best_fit" in algos
    assert "round_robin" in algos

    summary = comparison["summary"]
    assert len(summary) == 3
    keys = [item["algorithm_key"] for item in summary]
    assert keys == ["first_fit", "best_fit", "round_robin"]

    workload = comparison["initial_workload"]
    assert workload["total_hosts"] == len(sample_hosts)
    assert workload["total_vms_requested"] == len(sample_workload)
    assert workload["total_cpu_capacity"] == sum(h.total_cpu for h in sample_hosts)


def test_state_isolation_and_original_input_preservation(sample_hosts, sample_workload):
    """Verify that running compare_all leaves original hosts and VMs in pristine unallocated state."""
    # Pre-record original state
    orig_host_alloc_cpu = [h.allocated_cpu for h in sample_hosts]
    orig_vm_statuses = [v.status for v in sample_workload]

    comparison = SimulationEngine.compare_all(hosts=sample_hosts, vms=sample_workload)

    # Ensure original instances were not altered
    assert [h.allocated_cpu for h in sample_hosts] == orig_host_alloc_cpu
    assert [v.status for v in sample_workload] == orig_vm_statuses

    # Verify that each algorithm ran independently
    for key, algo_result in comparison["algorithms"].items():
        assert algo_result["metrics"]["successful_allocations"] > 0


def test_deterministic_results(sample_hosts, sample_workload):
    """Running identical inputs repeatedly must produce identical simulation outputs."""
    run1 = SimulationEngine.compare_all(hosts=sample_hosts, vms=sample_workload)
    run2 = SimulationEngine.compare_all(hosts=sample_hosts, vms=sample_workload)

    assert run1["summary"] == run2["summary"]
    for key in ["first_fit", "best_fit", "round_robin"]:
        assert run1["algorithms"][key]["metrics"] == run2["algorithms"][key]["metrics"]


# ---------------------------------------------------------------------------
# Metric Calculation Accuracy
# ---------------------------------------------------------------------------

def test_metric_calculations_exact():
    hosts = [
        Host(host_id="h1", total_cpu=10, total_ram=20),
        Host(host_id="h2", total_cpu=10, total_ram=20),
    ]
    # Total capacity: 20 CPU, 40 RAM
    vms = [
        VirtualMachine(vm_id="v1", cpu_required=5, ram_required=10),
        VirtualMachine(vm_id="v2", cpu_required=5, ram_required=10),
    ]
    # Total requested: 10 CPU, 20 RAM (exactly 50% utilization, 100% success rate)
    result = SimulationEngine.run_algorithm("first_fit", hosts, vms)
    metrics = result["metrics"]

    assert metrics["total_cpu_capacity"] == 20.0
    assert metrics["total_ram_capacity"] == 40.0
    assert metrics["allocated_cpu"] == 10.0
    assert metrics["allocated_ram"] == 20.0
    assert metrics["remaining_cpu"] == 10.0
    assert metrics["remaining_ram"] == 20.0
    assert metrics["cpu_utilization"] == 50.0
    assert metrics["ram_utilization"] == 50.0
    assert metrics["total_vms"] == 2
    assert metrics["successful_allocations"] == 2
    assert metrics["failed_allocations"] == 0
    assert metrics["allocation_success_rate"] == 100.0


# ---------------------------------------------------------------------------
# Edge Cases: Empty Workloads and Empty Hosts
# ---------------------------------------------------------------------------

def test_empty_workload(sample_hosts):
    """An empty workload should yield 0% success rate, 0% utilization, and 0 allocations."""
    result = SimulationEngine.run_algorithm("first_fit", hosts=sample_hosts, vms=[])
    metrics = result["metrics"]

    assert metrics["total_vms"] == 0
    assert metrics["successful_allocations"] == 0
    assert metrics["failed_allocations"] == 0
    assert metrics["allocation_success_rate"] == 0.0
    assert metrics["cpu_utilization"] == 0.0
    assert metrics["ram_utilization"] == 0.0
    assert metrics["allocated_cpu"] == 0.0
    assert metrics["allocated_ram"] == 0.0
    assert result["failed_allocations"] == []


def test_empty_hosts_list(sample_workload):
    """An empty host list should gracefully mark all VMs rejected with clear failure reasons."""
    result = SimulationEngine.run_algorithm("first_fit", hosts=[], vms=sample_workload)
    metrics = result["metrics"]

    assert metrics["total_hosts" if "total_hosts" in metrics else "total_cpu_capacity"] == 0.0
    assert metrics["total_vms"] == len(sample_workload)
    assert metrics["successful_allocations"] == 0
    assert metrics["failed_allocations"] == len(sample_workload)
    assert metrics["allocation_success_rate"] == 0.0
    assert metrics["cpu_utilization"] == 0.0
    assert metrics["ram_utilization"] == 0.0

    assert len(result["failed_allocations"]) == len(sample_workload)
    for fail in result["failed_allocations"]:
        assert "No physical hosts available" in fail["failure_reason"]


def test_failed_allocations_details(sample_hosts):
    """Over-capacity VMs must populate failed_allocations with helpful context."""
    oversized_vms = [
        VirtualMachine(vm_id="vm-huge-1", cpu_required=128, ram_required=256),
        VirtualMachine(vm_id="vm-huge-2", cpu_required=64, ram_required=512),
    ]

    result = SimulationEngine.run_algorithm("best_fit", hosts=sample_hosts, vms=oversized_vms)
    failed = result["failed_allocations"]

    assert len(failed) == 2
    assert failed[0]["vm_id"] == "vm-huge-1"
    assert failed[0]["cpu_required"] == 128.0
    assert "Insufficient CPU or RAM" in failed[0]["failure_reason"]


# ---------------------------------------------------------------------------
# JSON Serialization Test
# ---------------------------------------------------------------------------

def test_results_are_json_serializable(sample_hosts, sample_workload):
    comparison = SimulationEngine.compare_all(hosts=sample_hosts, vms=sample_workload)
    
    # Must serialize without TypeError
    serialized_json = json.dumps(comparison)
    assert isinstance(serialized_json, str)
    assert len(serialized_json) > 0

    # Must deserialize accurately
    deserialized = json.loads(serialized_json)
    assert "algorithms" in deserialized
    assert "summary" in deserialized
    assert "initial_workload" in deserialized


# ---------------------------------------------------------------------------
# Input Validation & Error Handling
# ---------------------------------------------------------------------------

def test_validate_inputs_non_list():
    with pytest.raises(TypeError, match="'hosts' must be a list"):
        SimulationEngine.run_algorithm("first_fit", hosts="invalid", vms=[])

    with pytest.raises(TypeError, match="'vms' must be a list"):
        SimulationEngine.run_algorithm("first_fit", hosts=[], vms="invalid")


def test_validate_inputs_invalid_elements():
    with pytest.raises(TypeError, match="not a Host instance"):
        SimulationEngine.run_algorithm("first_fit", hosts=[{"id": "h1"}], vms=[])

    with pytest.raises(TypeError, match="not a VirtualMachine instance"):
        SimulationEngine.run_algorithm("first_fit", hosts=[], vms=["vm-1"])


def test_validate_inputs_duplicate_ids():
    h1 = Host(host_id="h-dup", total_cpu=4, total_ram=8)
    h2 = Host(host_id="h-dup", total_cpu=4, total_ram=8)
    with pytest.raises(ValueError, match="Duplicate host_id detected"):
        SimulationEngine.validate_inputs([h1, h2], [])

    v1 = VirtualMachine(vm_id="v-dup", cpu_required=2, ram_required=4)
    v2 = VirtualMachine(vm_id="v-dup", cpu_required=2, ram_required=4)
    with pytest.raises(ValueError, match="Duplicate vm_id detected"):
        SimulationEngine.validate_inputs([], [v1, v2])


def test_unknown_algorithm_rejection(sample_hosts, sample_workload):
    with pytest.raises(ValueError, match="Unknown allocation algorithm"):
        SimulationEngine.run_algorithm("genetic_algorithm", sample_hosts, sample_workload)

    with pytest.raises(TypeError, match="must be a string"):
        SimulationEngine.run_algorithm(12345, sample_hosts, sample_workload)
