"""Base allocation algorithm interface and simulation summary metrics."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.models.host import Host
from app.models.vm import VirtualMachine


class AllocationSummary:
    """Encapsulates the statistical results of an algorithm simulation run."""

    def __init__(
        self,
        algorithm_name: str,
        hosts: List[Host],
        vms: List[VirtualMachine],
        steps: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        self.algorithm_name: str = algorithm_name
        self.hosts: List[Host] = hosts
        self.vms: List[VirtualMachine] = vms
        self.steps: List[Dict[str, Any]] = steps or []

        self.total_vms: int = len(vms)
        self.successful_allocations: int = sum(
            1 for vm in vms if vm.status == VirtualMachine.STATUS_ALLOCATED
        )
        self.failed_allocations: int = sum(
            1 for vm in vms if vm.status == VirtualMachine.STATUS_REJECTED
        )
        self.pending_allocations: int = sum(
            1 for vm in vms if vm.status == VirtualMachine.STATUS_PENDING
        )

        self.success_rate: float = (
            round((self.successful_allocations / self.total_vms) * 100.0, 2)
            if self.total_vms > 0
            else 0.0
        )

        self.total_cpu_capacity: float = sum(h.total_cpu for h in hosts)
        self.total_ram_capacity: float = sum(h.total_ram for h in hosts)

        self.allocated_cpu: float = round(sum(h.allocated_cpu for h in hosts), 2)
        self.allocated_ram: float = round(sum(h.allocated_ram for h in hosts), 2)

        self.remaining_cpu: float = round(sum(h.remaining_cpu for h in hosts), 2)
        self.remaining_ram: float = round(sum(h.remaining_ram for h in hosts), 2)

        self.cpu_utilization: float = (
            round((self.allocated_cpu / self.total_cpu_capacity) * 100.0, 2)
            if self.total_cpu_capacity > 0
            else 0.0
        )
        self.ram_utilization: float = (
            round((self.allocated_ram / self.total_ram_capacity) * 100.0, 2)
            if self.total_ram_capacity > 0
            else 0.0
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert simulation summary to dictionary representation."""
        return {
            "algorithm_name": self.algorithm_name,
            "total_vms": self.total_vms,
            "successful_allocations": self.successful_allocations,
            "failed_allocations": self.failed_allocations,
            "pending_allocations": self.pending_allocations,
            "success_rate": self.success_rate,
            "total_cpu_capacity": self.total_cpu_capacity,
            "total_ram_capacity": self.total_ram_capacity,
            "allocated_cpu": self.allocated_cpu,
            "allocated_ram": self.allocated_ram,
            "remaining_cpu": self.remaining_cpu,
            "remaining_ram": self.remaining_ram,
            "cpu_utilization": self.cpu_utilization,
            "ram_utilization": self.ram_utilization,
            "hosts": [h.to_dict() for h in self.hosts],
            "vms": [vm.to_dict() for vm in self.vms],
            "steps": self.steps,
        }


class BaseAllocationAlgorithm(ABC):
    """Abstract base class for all VM resource allocation algorithms."""

    def __init__(self, name: str) -> None:
        self.name: str = name

    @abstractmethod
    def allocate_vm(
        self,
        vm: VirtualMachine,
        hosts: List[Host],
    ) -> Optional[Host]:
        """Attempt to allocate a single VM onto one of the available hosts.
        
        Args:
            vm: VirtualMachine instance requesting resources.
            hosts: List of available Physical Hosts.
            
        Returns:
            The Host that accepted the allocation, or None if allocation failed.
        """
        pass

    def allocate_workload(
        self,
        vms: List[VirtualMachine],
        hosts: List[Host],
        in_place: bool = False,
    ) -> AllocationSummary:
        """Allocate an entire batch/workload of VMs across the provided hosts.
        
        Args:
            vms: List of VirtualMachine requests.
            hosts: List of Physical Hosts.
            in_place: If False, clones hosts and VMs so the input instances remain untouched.
            
        Returns:
            AllocationSummary containing execution statistics and state.
        """
        target_hosts = hosts if in_place else [h.clone() for h in hosts]
        target_vms = vms if in_place else [vm.clone() for vm in vms]

        steps: List[Dict[str, Any]] = []

        for vm in target_vms:
            allocated_host = self.allocate_vm(vm, target_hosts)
            step_record = {
                "vm_id": vm.vm_id,
                "cpu_required": vm.cpu_required,
                "ram_required": vm.ram_required,
                "status": vm.status,
                "allocated_host_id": allocated_host.host_id if allocated_host else None,
                "failure_reason": vm.failure_reason,
            }
            steps.append(step_record)

        return AllocationSummary(
            algorithm_name=self.name,
            hosts=target_hosts,
            vms=target_vms,
            steps=steps,
        )
