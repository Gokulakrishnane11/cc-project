"""First Fit VM Allocation Algorithm."""

from __future__ import annotations
from typing import List, Optional
from app.algorithms.base import BaseAllocationAlgorithm
from app.models.host import Host
from app.models.vm import VirtualMachine


class FirstFitAllocator(BaseAllocationAlgorithm):
    """Allocates a VM to the first host that has sufficient CPU and RAM.
    
    Cloud Computing Principle:
    First Fit sequentially scans the list of physical hosts from the very first
    host (index 0) and immediately assigns the incoming VM to the first host
    with adequate unallocated CPU and RAM. It minimizes search time (O(n) worst-case,
    often O(1) in underloaded systems) but may cause resource fragmentation at the
    head of the host list.
    """

    def __init__(self) -> None:
        super().__init__(name="First Fit")

    def allocate_vm(
        self,
        vm: VirtualMachine,
        hosts: List[Host],
    ) -> Optional[Host]:
        """Allocate a VM to the first host with enough capacity.
        
        Args:
            vm: VirtualMachine instance to allocate.
            hosts: Ordered list of Physical Hosts.
            
        Returns:
            The Host that accommodated the VM, or None if no host had capacity.
        """
        if not hosts:
            vm.mark_rejected("No physical hosts available for allocation.")
            return None

        for host in hosts:
            if host.can_accommodate(vm):
                host.allocate(vm)
                return host

        # No host could accommodate the VM
        vm.mark_rejected(
            f"Insufficient CPU or RAM across all {len(hosts)} hosts. "
            f"Requested: (CPU: {vm.cpu_required}, RAM: {vm.ram_required} GB)."
        )
        return None
