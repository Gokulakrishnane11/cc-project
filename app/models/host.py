"""Physical Host resource model."""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from app.models.vm import VirtualMachine, validate_positive_number

EPSILON = 1e-7


class Host:
    """Represents a Physical Host with fixed CPU and RAM capacity."""

    def __init__(
        self,
        host_id: str,
        total_cpu: float,
        total_ram: float,
        name: Optional[str] = None,
    ) -> None:
        """Initialize and validate Physical Host attributes.
        
        Args:
            host_id: Unique string identifier for the host (e.g., 'host-1').
            total_cpu: Total CPU capacity in cores (> 0).
            total_ram: Total RAM capacity in GB (> 0).
            name: Human-friendly name for the host (defaults to host_id).
        """
        if not isinstance(host_id, str) or not host_id.strip():
            raise ValueError("Host 'host_id' must be a non-empty string.")

        self.host_id: str = host_id.strip()
        self.name: str = name.strip() if (name and isinstance(name, str) and name.strip()) else self.host_id
        self.total_cpu: float = validate_positive_number(total_cpu, "total_cpu")
        self.total_ram: float = validate_positive_number(total_ram, "total_ram")
        
        self.allocated_vms: List[VirtualMachine] = []

    @property
    def allocated_cpu(self) -> float:
        """Sum of CPU cores allocated across all active VMs on this host."""
        return sum(vm.cpu_required for vm in self.allocated_vms)

    @property
    def allocated_ram(self) -> float:
        """Sum of RAM (GB) allocated across all active VMs on this host."""
        return sum(vm.ram_required for vm in self.allocated_vms)

    @property
    def remaining_cpu(self) -> float:
        """Remaining unallocated CPU cores on this host."""
        rem = self.total_cpu - self.allocated_cpu
        return max(0.0, round(rem, 6))

    @property
    def remaining_ram(self) -> float:
        """Remaining unallocated RAM (GB) on this host."""
        rem = self.total_ram - self.allocated_ram
        return max(0.0, round(rem, 6))

    @property
    def cpu_utilization(self) -> float:
        """Percentage of total CPU capacity currently allocated."""
        if self.total_cpu <= 0:
            return 0.0
        return round((self.allocated_cpu / self.total_cpu) * 100.0, 2)

    @property
    def ram_utilization(self) -> float:
        """Percentage of total RAM capacity currently allocated."""
        if self.total_ram <= 0:
            return 0.0
        return round((self.allocated_ram / self.total_ram) * 100.0, 2)

    def can_accommodate(self, vm: VirtualMachine) -> bool:
        """Check whether this host has sufficient remaining CPU and RAM for the VM.
        
        Args:
            vm: VirtualMachine instance requesting resources.
            
        Returns:
            bool: True if both CPU and RAM can accommodate the VM, False otherwise.
        """
        if not isinstance(vm, VirtualMachine):
            raise TypeError(f"Expected VirtualMachine instance, got {type(vm).__name__}.")

        has_cpu = (self.remaining_cpu + EPSILON) >= vm.cpu_required
        has_ram = (self.remaining_ram + EPSILON) >= vm.ram_required
        return has_cpu and has_ram

    def allocate(self, vm: VirtualMachine) -> None:
        """Allocate a VM to this host if capacity permits.
        
        Args:
            vm: VirtualMachine instance to allocate.
            
        Raises:
            ValueError: If the VM cannot be accommodated without exceeding capacity.
        """
        if not self.can_accommodate(vm):
            raise ValueError(
                f"Cannot allocate VM '{vm.vm_id}' (CPU: {vm.cpu_required}, RAM: {vm.ram_required}) "
                f"to host '{self.host_id}' (Remaining CPU: {self.remaining_cpu}, Remaining RAM: {self.remaining_ram}). "
                "Allocation would cause resource over-allocation."
            )

        # Mark VM state
        vm.mark_allocated(self.host_id)
        self.allocated_vms.append(vm)

    def deallocate(self, vm_id: str) -> Optional[VirtualMachine]:
        """Remove a VM by ID from this host.
        
        Args:
            vm_id: ID of the VM to remove.
            
        Returns:
            The removed VirtualMachine if found, None otherwise.
        """
        for i, vm in enumerate(self.allocated_vms):
            if vm.vm_id == vm_id:
                vm.reset()
                return self.allocated_vms.pop(i)
        return None

    def reset(self) -> None:
        """Clear all allocated VMs from this host and reset their statuses."""
        for vm in self.allocated_vms:
            vm.reset()
        self.allocated_vms.clear()

    def clone(self) -> Host:
        """Create a deep, independent copy of this Host and its allocated VMs."""
        cloned_host = Host(
            host_id=self.host_id,
            total_cpu=self.total_cpu,
            total_ram=self.total_ram,
            name=self.name,
        )
        for vm in self.allocated_vms:
            cloned_vm = vm.clone()
            cloned_host.allocated_vms.append(cloned_vm)
        return cloned_host

    def to_dict(self) -> Dict[str, Any]:
        """Serialize host state to a dictionary for API and frontend display."""
        return {
            "host_id": self.host_id,
            "name": self.name,
            "total_cpu": self.total_cpu,
            "total_ram": self.total_ram,
            "allocated_cpu": round(self.allocated_cpu, 2),
            "allocated_ram": round(self.allocated_ram, 2),
            "remaining_cpu": round(self.remaining_cpu, 2),
            "remaining_ram": round(self.remaining_ram, 2),
            "cpu_utilization": self.cpu_utilization,
            "ram_utilization": self.ram_utilization,
            "allocated_vms": [vm.to_dict() for vm in self.allocated_vms],
            "vm_count": len(self.allocated_vms),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Host:
        """Construct a Host from a dictionary."""
        host = cls(
            host_id=str(data.get("host_id", "")),
            total_cpu=data.get("total_cpu"),
            total_ram=data.get("total_ram"),
            name=data.get("name"),
        )
        for vm_data in data.get("allocated_vms", []):
            vm = VirtualMachine.from_dict(vm_data)
            host.allocated_vms.append(vm)
        return host

    def __repr__(self) -> str:
        return (
            f"Host(id={self.host_id!r}, name={self.name!r}, "
            f"cpu={self.allocated_cpu}/{self.total_cpu}, "
            f"ram={self.allocated_ram}/{self.total_ram}, "
            f"vms={len(self.allocated_vms)})"
        )
