"""Best Fit VM Allocation Algorithm."""

from __future__ import annotations
from typing import List, Optional, Tuple
from app.algorithms.base import BaseAllocationAlgorithm
from app.models.host import Host
from app.models.vm import VirtualMachine


class BestFitAllocator(BaseAllocationAlgorithm):
    """Allocates a VM to the feasible host that leaves the minimum residual resources.
    
    Cloud Computing Principle:
    Best Fit attempts to pack VMs as tightly as possible onto physical hosts to
    minimize residual/stranded capacity. The best host is selected based on the
    lowest normalized residual-resource score calculated AFTER the proposed allocation:
    
        score = (remaining_cpu / total_cpu) + (remaining_ram / total_ram)
        
    Where remaining_cpu and remaining_ram represent the projected capacity if
    the VM were allocated to that host.
    
    Tie-breaking:
    When multiple hosts yield identical residual scores, deterministic tie-breaking
    selects the host with the lowest index in the host list.
    """

    def __init__(self) -> None:
        super().__init__(name="Best Fit")

    @staticmethod
    def calculate_residual_score(host: Host, vm: VirtualMachine) -> float:
        """Calculate the normalized residual-resource score after proposed VM allocation.
        
        Formula:
            score = (projected_remaining_cpu / total_cpu) + (projected_remaining_ram / total_ram)
            
        Args:
            host: Candidate Physical Host.
            vm: VirtualMachine requesting allocation.
            
        Returns:
            Normalized residual resource score (lower is a tighter fit).
        """
        projected_rem_cpu = max(0.0, host.remaining_cpu - vm.cpu_required)
        projected_rem_ram = max(0.0, host.remaining_ram - vm.ram_required)

        cpu_ratio = projected_rem_cpu / host.total_cpu
        ram_ratio = projected_rem_ram / host.total_ram

        return cpu_ratio + ram_ratio

    def allocate_vm(
        self,
        vm: VirtualMachine,
        hosts: List[Host],
    ) -> Optional[Host]:
        """Allocate a VM to the feasible host with the lowest normalized residual score.
        
        Args:
            vm: VirtualMachine instance to allocate.
            hosts: Ordered list of Physical Hosts.
            
        Returns:
            The Host that accepted the VM, or None if no host had capacity.
        """
        if not hosts:
            vm.mark_rejected("No physical hosts available for allocation.")
            return None

        feasible_candidates: List[Tuple[float, int, Host]] = []

        for index, host in enumerate(hosts):
            if host.can_accommodate(vm):
                score = self.calculate_residual_score(host, vm)
                feasible_candidates.append((score, index, host))

        if not feasible_candidates:
            vm.mark_rejected(
                f"Insufficient CPU or RAM across all {len(hosts)} hosts for Best Fit. "
                f"Requested: (CPU: {vm.cpu_required}, RAM: {vm.ram_required} GB)."
            )
            return None

        # Sort by score ascending, then by host index ascending for deterministic tie-breaking
        # Round score to 8 decimal places to avoid floating-point jitter
        feasible_candidates.sort(key=lambda item: (round(item[0], 8), item[1]))

        best_host = feasible_candidates[0][2]
        best_host.allocate(vm)
        return best_host
