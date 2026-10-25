"""Unit tests for Physical Host and Virtual Machine domain models."""

import pytest
from app.models.host import Host
from app.models.vm import VirtualMachine, validate_positive_number


# ---------------------------------------------------------------------------
# Validation Function Tests
# ---------------------------------------------------------------------------

def test_validate_positive_number_valid():
    assert validate_positive_number(4, "cpu") == 4.0
    assert validate_positive_number(2.5, "ram") == 2.5


@pytest.mark.parametrize("invalid_val", [0, -1, -0.01, -100])
def test_validate_positive_number_non_positive(invalid_val):
    with pytest.raises(ValueError, match="must be greater than zero"):
        validate_positive_number(invalid_val, "cpu")


@pytest.mark.parametrize("invalid_type", [True, False, "4", None, [4], {"cpu": 4}])
def test_validate_positive_number_invalid_types(invalid_type):
    with pytest.raises(TypeError):
        validate_positive_number(invalid_type, "field")


def test_validate_positive_number_nan_inf():
    with pytest.raises(ValueError, match="must be a finite number"):
        validate_positive_number(float("nan"), "cpu")
    with pytest.raises(ValueError, match="must be a finite number"):
        validate_positive_number(float("inf"), "cpu")


# ---------------------------------------------------------------------------
# VirtualMachine Model Tests
# ---------------------------------------------------------------------------

def test_vm_creation_valid():
    vm = VirtualMachine(vm_id="vm-1", cpu_required=2, ram_required=4.0)
    assert vm.vm_id == "vm-1"
    assert vm.cpu_required == 2.0
    assert vm.ram_required == 4.0
    assert vm.status == VirtualMachine.STATUS_PENDING
    assert vm.allocated_host_id is None
    assert vm.failure_reason is None


@pytest.mark.parametrize("invalid_id", ["", "   ", None, 123])
def test_vm_creation_invalid_id(invalid_id):
    with pytest.raises(ValueError):
        VirtualMachine(vm_id=invalid_id, cpu_required=2, ram_required=4)


def test_vm_allocation_and_rejection_lifecycle():
    vm = VirtualMachine(vm_id="vm-test", cpu_required=2, ram_required=4)
    
    # Mark allocated
    vm.mark_allocated("host-1")
    assert vm.status == VirtualMachine.STATUS_ALLOCATED
    assert vm.allocated_host_id == "host-1"
    assert vm.failure_reason is None

    # Reset
    vm.reset()
    assert vm.status == VirtualMachine.STATUS_PENDING
    assert vm.allocated_host_id is None

    # Mark rejected
    vm.mark_rejected("Insufficient CPU")
    assert vm.status == VirtualMachine.STATUS_REJECTED
    assert vm.allocated_host_id is None
    assert vm.failure_reason == "Insufficient CPU"


def test_vm_clone_is_independent():
    vm1 = VirtualMachine(vm_id="vm-orig", cpu_required=4, ram_required=8)
    vm2 = vm1.clone()

    assert vm1.vm_id == vm2.vm_id
    assert vm1.cpu_required == vm2.cpu_required
    assert vm1.ram_required == vm2.ram_required

    # Mutate vm2, vm1 must remain unaffected
    vm2.mark_allocated("host-99")
    assert vm2.status == VirtualMachine.STATUS_ALLOCATED
    assert vm1.status == VirtualMachine.STATUS_PENDING
    assert vm1.allocated_host_id is None


def test_vm_to_dict_and_from_dict():
    vm = VirtualMachine(vm_id="vm-1", cpu_required=2, ram_required=4)
    vm.mark_allocated("host-1")
    data = vm.to_dict()

    assert data["vm_id"] == "vm-1"
    assert data["cpu_required"] == 2.0
    assert data["ram_required"] == 4.0
    assert data["status"] == VirtualMachine.STATUS_ALLOCATED
    assert data["allocated_host_id"] == "host-1"

    restored = VirtualMachine.from_dict(data)
    assert restored.vm_id == vm.vm_id
    assert restored.cpu_required == vm.cpu_required
    assert restored.ram_required == vm.ram_required
    assert restored.status == vm.status


# ---------------------------------------------------------------------------
# Host Model Tests
# ---------------------------------------------------------------------------

def test_host_creation_valid():
    host = Host(host_id="host-1", total_cpu=16, total_ram=64, name="Primary Host")
    assert host.host_id == "host-1"
    assert host.name == "Primary Host"
    assert host.total_cpu == 16.0
    assert host.total_ram == 64.0
    assert host.allocated_cpu == 0.0
    assert host.allocated_ram == 0.0
    assert host.remaining_cpu == 16.0
    assert host.remaining_ram == 64.0
    assert host.cpu_utilization == 0.0
    assert host.ram_utilization == 0.0


@pytest.mark.parametrize("invalid_id", ["", "   ", None])
def test_host_creation_invalid_id(invalid_id):
    with pytest.raises(ValueError):
        Host(host_id=invalid_id, total_cpu=8, total_ram=16)


@pytest.mark.parametrize("invalid_cap", [0, -4, True, "16", None])
def test_host_creation_invalid_capacity(invalid_cap):
    with pytest.raises((ValueError, TypeError)):
        Host(host_id="host-err", total_cpu=invalid_cap, total_ram=16)


def test_host_can_accommodate():
    host = Host(host_id="host-1", total_cpu=4, total_ram=8)

    vm_fits = VirtualMachine(vm_id="vm-fits", cpu_required=4, ram_required=8)
    assert host.can_accommodate(vm_fits) is True

    vm_exceeds_cpu = VirtualMachine(vm_id="vm-no-cpu", cpu_required=5, ram_required=4)
    assert host.can_accommodate(vm_exceeds_cpu) is False

    vm_exceeds_ram = VirtualMachine(vm_id="vm-no-ram", cpu_required=2, ram_required=9)
    assert host.can_accommodate(vm_exceeds_ram) is False

    vm_exceeds_both = VirtualMachine(vm_id="vm-no-both", cpu_required=6, ram_required=12)
    assert host.can_accommodate(vm_exceeds_both) is False


def test_host_allocate_and_over_allocation_prevention():
    host = Host(host_id="host-1", total_cpu=8, total_ram=16)
    vm1 = VirtualMachine(vm_id="vm-1", cpu_required=4, ram_required=8)
    
    host.allocate(vm1)
    assert host.allocated_cpu == 4.0
    assert host.allocated_ram == 8.0
    assert host.remaining_cpu == 4.0
    assert host.remaining_ram == 8.0
    assert host.cpu_utilization == 50.0
    assert host.ram_utilization == 50.0
    assert vm1.status == VirtualMachine.STATUS_ALLOCATED
    assert vm1.allocated_host_id == "host-1"

    # Attempt to allocate another VM that exceeds remaining CPU
    vm_too_large = VirtualMachine(vm_id="vm-large", cpu_required=5, ram_required=4)
    with pytest.raises(ValueError, match="resource over-allocation"):
        host.allocate(vm_too_large)

    # Verify state was not modified after failed allocation
    assert host.allocated_cpu == 4.0
    assert host.allocated_ram == 8.0
    assert len(host.allocated_vms) == 1


def test_host_deallocate_and_reset():
    host = Host(host_id="host-1", total_cpu=8, total_ram=16)
    vm1 = VirtualMachine(vm_id="vm-1", cpu_required=2, ram_required=4)
    vm2 = VirtualMachine(vm_id="vm-2", cpu_required=4, ram_required=8)

    host.allocate(vm1)
    host.allocate(vm2)
    assert len(host.allocated_vms) == 2
    assert host.allocated_cpu == 6.0

    # Deallocate vm1
    removed = host.deallocate("vm-1")
    assert removed is not None
    assert removed.vm_id == "vm-1"
    assert removed.status == VirtualMachine.STATUS_PENDING
    assert len(host.allocated_vms) == 1
    assert host.allocated_cpu == 4.0

    # Reset host
    host.reset()
    assert len(host.allocated_vms) == 0
    assert host.allocated_cpu == 0.0
    assert host.allocated_ram == 0.0
    assert vm2.status == VirtualMachine.STATUS_PENDING


def test_host_clone_independence():
    host = Host(host_id="host-1", total_cpu=8, total_ram=16)
    vm = VirtualMachine(vm_id="vm-1", cpu_required=2, ram_required=4)
    host.allocate(vm)

    cloned = host.clone()
    assert cloned.host_id == host.host_id
    assert cloned.allocated_cpu == host.allocated_cpu
    assert len(cloned.allocated_vms) == 1

    # Mutate cloned host: allocate a new VM to cloned only
    vm2 = VirtualMachine(vm_id="vm-2", cpu_required=2, ram_required=4)
    cloned.allocate(vm2)

    assert cloned.allocated_cpu == 4.0
    assert host.allocated_cpu == 2.0
    assert len(host.allocated_vms) == 1
    assert len(cloned.allocated_vms) == 2
