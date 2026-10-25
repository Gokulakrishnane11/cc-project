"""Round Robin VM Allocation Algorithm."""

from __future__ import annotations
from typing import List, Optional
from app.algorithms.base import BaseAllocationAlgorithm, AllocationSummary
from app.models.host import Host
from app.models.vm import VirtualMachine


class RoundRobinAllocator(BaseAllocationAlgorithm):
    """Allocates VMs across physical hosts in circular sequential order.
    
    Cloud Computing Principle:
    Round Robin balances workload distribution across all available physical hosts
    by cycling through them sequentially. For each VM request, it evaluates hosts
    starting immediately after the previous allocation attempt.
    
    Before placing a VM, it validates that the candidate host has sufficient CPU
    and RAM. If the candidate cannot satisfy the request, it advances along the ring
    until a suitable host is found. If no host in the entire cluster has enough
    capacity, the allocation is recorded as failed.
    """

    def __init__(self, initial_index: int = 0) -> None:
        super().__init__(name="Round Robin")
        self.current_index: int = initial_index

    def reset_pointer(self, index: int = 0) -> None:
        """Reset the circular pointer to a specific host index (defaults to 0)."""
        self.current_index = index

    def allocate_vm(
        self,
        vm: VirtualMachine,
        hosts: List[Host],
    ) -> Optional[Host]:
        """Allocate a VM to the next available host in the circular sequence.
        
        Args:
            vm: VirtualMachine instance requesting resources.
            hosts: Ordered list of Physical Hosts.
            
        Returns:
            The Host that accepted the VM, or None if no host had capacity.
        """
        if not hosts:
            vm.mark_rejected("No physical hosts available for allocation.")
            return None

        num_hosts = len(hosts)
        start_attempt_index = self.current_index % num_hosts

        # Cycle through all hosts starting from the current pointer
        for offset in range(num_hosts):
            candidate_idx = (start_attempt_index + offset) % num_hosts
            candidate_host = hosts[candidate_idx]

            if candidate_host.can_accommodate(vm):
                candidate_host.allocate(vm)
                # Next allocation attempt starts strictly after this allocation
                self.current_index = (candidate_idx + 1) % num_hosts
                return candidate_host

        # No host had sufficient capacity in the full cycle
        vm.mark_rejected(
            f"No host could accommodate VM in Round Robin cycle across {num_hosts} hosts. "
            f"Requested: (CPU: {vm.cpu_required}, RAM: {vm.ram_required} GB)."
        )
        # Advance pointer past the failed attempt starting point
        self.current_index = (start_attempt_index + 1) % num_hosts
        return None

    def allocate_workload(
        self,
        vms: List[VirtualMachine],
        hosts: List[Host],
        in_place: bool = False,
    ) -> AllocationSummary:
        """Allocate a workload, ensuring independent state when in_place=False."""
        # Reset pointer for reproducible independent simulation runs if not running in-place
        if not in_place:
            saved_pointer = self.current_index
            self.reset_pointer(0)
            try:
                return super().allocate_workload(vms, hosts, in_place=in_place)
            finally:
                self.current_index = saved_pointer
        return super().allocate_workload(vms, hosts, in_place=in_place)
