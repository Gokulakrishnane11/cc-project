"""Unit and integration tests for VM Allocation Algorithms."""

import pytest
from app.models.host import Host
from app.models.vm import VirtualMachine
from app.algorithms.first_fit import FirstFitAllocator
from app.algorithms.best_fit import BestFitAllocator
from app.algorithms.round_robin import RoundRobinAllocator


# ---------------------------------------------------------------------------
# First Fit Tests
# ---------------------------------------------------------------------------

def test_first_fit_basic_allocation():
    allocator = FirstFitAllocator()
    hosts = [
        Host(host_id="h0", total_cpu=4, total_ram=8),
        Host(host_id="h1", total_cpu=4, total_ram=8),
    ]
    vm1 = VirtualMachine(vm_id="vm1", cpu_required=2, ram_required=4)
    vm2 = VirtualMachine(vm_id="vm2", cpu_required=2, ram_required=4)

    # First Fit should put both into h0 since h0 has 4 CPU and 8 RAM
    res1 = allocator.allocate_vm(vm1, hosts)
    assert res1.host_id == "h0"
    assert hosts[0].remaining_cpu == 2.0

    res2 = allocator.allocate_vm(vm2, hosts)
    assert res2.host_id == "h0"
    assert hosts[0].remaining_cpu == 0.0
    assert hosts[0].remaining_ram == 0.0


def test_first_fit_skips_full_host():
    allocator = FirstFitAllocator()
    hosts = [
        Host(host_id="h0", total_cpu=2, total_ram=4),
        Host(host_id="h1", total_cpu=8, total_ram=16),
    ]
    # h0 only has 2 CPU, vm requires 4 CPU
    vm = VirtualMachine(vm_id="vm-large", cpu_required=4, ram_required=8)
    
    result = allocator.allocate_vm(vm, hosts)
    assert result is not None
    assert result.host_id == "h1"
    assert hosts[0].allocated_cpu == 0.0
    assert hosts[1].allocated_cpu == 4.0


def test_first_fit_rejection_when_no_capacity():
    allocator = FirstFitAllocator()
    hosts = [
        Host(host_id="h0", total_cpu=2, total_ram=4),
        Host(host_id="h1", total_cpu=2, total_ram=4),
    ]
    vm = VirtualMachine(vm_id="vm-impossible", cpu_required=8, ram_required=16)

    result = allocator.allocate_vm(vm, hosts)
    assert result is None
    assert vm.status == VirtualMachine.STATUS_REJECTED
    assert "Insufficient CPU or RAM" in vm.failure_reason


# ---------------------------------------------------------------------------
# Best Fit Tests
# ---------------------------------------------------------------------------

def test_best_fit_residual_score_calculation():
    host = Host(host_id="h1", total_cpu=8, total_ram=16)
    vm = VirtualMachine(vm_id="vm1", cpu_required=4, ram_required=8)

    # Projected remaining: 8 - 4 = 4 CPU, 16 - 8 = 8 RAM
    # score = (4 / 8) + (8 / 16) = 0.5 + 0.5 = 1.0
    score = BestFitAllocator.calculate_residual_score(host, vm)
    assert pytest.approx(score, 1e-6) == 1.0


def test_best_fit_selects_tighter_host():
    """Best fit must pick the host that leaves the minimum residual resources."""
    allocator = BestFitAllocator()
    h_spacious = Host(host_id="h-spacious", total_cpu=16, total_ram=32)
    h_tight = Host(host_id="h-tight", total_cpu=4, total_ram=8)
    hosts = [h_spacious, h_tight]

    vm = VirtualMachine(vm_id="vm-tight", cpu_required=4, ram_required=8)

    # For h-spacious: projected rem = 12 CPU, 24 RAM -> score = 12/16 + 24/32 = 0.75 + 0.75 = 1.5
    # For h-tight: projected rem = 0 CPU, 0 RAM -> score = 0/4 + 0/8 = 0.0
    # Best fit must pick h-tight!
    result = allocator.allocate_vm(vm, hosts)
    assert result.host_id == "h-tight"
    assert h_tight.remaining_cpu == 0.0
    assert h_tight.remaining_ram == 0.0
    assert h_spacious.allocated_cpu == 0.0


def test_best_fit_deterministic_tie_breaking():
    """When residual scores are equal, Best Fit must pick the host with the lowest index."""
    allocator = BestFitAllocator()
    h0 = Host(host_id="h0", total_cpu=8, total_ram=16)
    h1 = Host(host_id="h1", total_cpu=8, total_ram=16)
    hosts = [h0, h1]

    vm = VirtualMachine(vm_id="vm1", cpu_required=2, ram_required=4)

    # Both hosts have identical capacity and remaining resources -> identical score
    result = allocator.allocate_vm(vm, hosts)
    assert result.host_id == "h0"  # index 0 won tie-break


def test_best_fit_rejection_when_no_capacity():
    allocator = BestFitAllocator()
    hosts = [Host(host_id="h0", total_cpu=2, total_ram=2)]
    vm = VirtualMachine(vm_id="vm-too-big", cpu_required=4, ram_required=4)

    result = allocator.allocate_vm(vm, hosts)
    assert result is None
    assert vm.status == VirtualMachine.STATUS_REJECTED


# ---------------------------------------------------------------------------
# Round Robin Tests
# ---------------------------------------------------------------------------

def test_round_robin_circular_distribution():
    allocator = RoundRobinAllocator()
    hosts = [
        Host(host_id="h0", total_cpu=8, total_ram=16),
        Host(host_id="h1", total_cpu=8, total_ram=16),
        Host(host_id="h2", total_cpu=8, total_ram=16),
    ]
    vms = [
        VirtualMachine(vm_id=f"vm{i}", cpu_required=1, ram_required=2)
        for i in range(4)
    ]

    # VM0 -> h0
    r0 = allocator.allocate_vm(vms[0], hosts)
    assert r0.host_id == "h0"
    assert allocator.current_index == 1

    # VM1 -> h1
    r1 = allocator.allocate_vm(vms[1], hosts)
    assert r1.host_id == "h1"
    assert allocator.current_index == 2

    # VM2 -> h2
    r2 = allocator.allocate_vm(vms[2], hosts)
    assert r2.host_id == "h2"
    assert allocator.current_index == 0

    # VM3 -> wraps to h0
    r3 = allocator.allocate_vm(vms[3], hosts)
    assert r3.host_id == "h0"
    assert allocator.current_index == 1


def test_round_robin_skips_full_host_and_advances():
    allocator = RoundRobinAllocator(initial_index=1)
    hosts = [
        Host(host_id="h0", total_cpu=8, total_ram=16),
        Host(host_id="h1", total_cpu=1, total_ram=1),  # Cannot fit VM requiring 2 CPU
        Host(host_id="h2", total_cpu=8, total_ram=16),
    ]
    vm = VirtualMachine(vm_id="vm-skip", cpu_required=2, ram_required=4)

    # Pointer starts at index 1 (h1). h1 is rejected, checks h2 next.
    # h2 fits -> allocates to h2!
    # Next pointer starts after h2: (2 + 1) % 3 = 0.
    result = allocator.allocate_vm(vm, hosts)
    assert result.host_id == "h2"
    assert allocator.current_index == 0


def test_round_robin_rejection_advances_attempt():
    allocator = RoundRobinAllocator(initial_index=0)
    hosts = [
        Host(host_id="h0", total_cpu=1, total_ram=1),
        Host(host_id="h1", total_cpu=1, total_ram=1),
    ]
    vm_fail = VirtualMachine(vm_id="vm-fail", cpu_required=4, ram_required=4)

    # No host can fit vm_fail
    res = allocator.allocate_vm(vm_fail, hosts)
    assert res is None
    assert vm_fail.status == VirtualMachine.STATUS_REJECTED
    # Pointer advances past the attempted start (0 -> 1)
    assert allocator.current_index == 1


# ---------------------------------------------------------------------------
# Over-allocation and Boundary Tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("allocator_cls", [FirstFitAllocator, BestFitAllocator, RoundRobinAllocator])
def test_all_algorithms_strictly_prevent_over_allocation(allocator_cls):
    allocator = allocator_cls()
    hosts = [
        Host(host_id="h0", total_cpu=4, total_ram=8),
        Host(host_id="h1", total_cpu=4, total_ram=8),
    ]
    # Total cluster capacity: 8 CPU, 16 RAM
    # Workload requests 12 CPU, 24 RAM (exceeds capacity)
    vms = [
        VirtualMachine(vm_id=f"vm-{i}", cpu_required=2, ram_required=4)
        for i in range(6)
    ]

    summary = allocator.allocate_workload(vms, hosts, in_place=True)

    # Only 4 VMs should succeed, 2 must fail
    assert summary.successful_allocations == 4
    assert summary.failed_allocations == 2
    assert summary.success_rate == pytest.approx(66.67, 0.01)

    # Ensure no host exceeded total capacity
    for h in hosts:
        assert h.allocated_cpu <= h.total_cpu
        assert h.allocated_ram <= h.total_ram
        assert h.remaining_cpu >= 0.0
        assert h.remaining_ram >= 0.0


# ---------------------------------------------------------------------------
# Independent State Isolation Tests
# ---------------------------------------------------------------------------

def test_workload_state_isolation():
    """Ensure running an algorithm with in_place=False leaves original inputs pristine."""
    hosts = [
        Host(host_id="h0", total_cpu=4, total_ram=8),
        Host(host_id="h1", total_cpu=8, total_ram=16),
    ]
    vms = [
        VirtualMachine(vm_id="vm1", cpu_required=2, ram_required=4),
        VirtualMachine(vm_id="vm2", cpu_required=4, ram_required=8),
    ]

    ff = FirstFitAllocator().allocate_workload(vms, hosts, in_place=False)
    bf = BestFitAllocator().allocate_workload(vms, hosts, in_place=False)
    rr = RoundRobinAllocator().allocate_workload(vms, hosts, in_place=False)

    # Verify original inputs are untouched
    assert all(h.allocated_cpu == 0.0 for h in hosts)
    assert all(vm.status == VirtualMachine.STATUS_PENDING for vm in vms)

    # Verify all summaries contain valid independent results
    assert ff.successful_allocations == 2
    assert bf.successful_allocations == 2
    assert rr.successful_allocations == 2
