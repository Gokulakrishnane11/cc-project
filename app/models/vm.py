"""Virtual Machine (VM) resource request model."""

from __future__ import annotations
import math
from typing import Any, Dict, Optional


def validate_positive_number(value: Any, field_name: str) -> float:
    """Validate that a field is a positive finite number (int or float, not bool).
    
    Raises:
        TypeError: If value is not a float or int, or is a bool.
        ValueError: If value is not finite or is <= 0.
    """
    if isinstance(value, bool):
        raise TypeError(f"'{field_name}' must be a numeric value, not boolean.")
    if not isinstance(value, (int, float)):
        raise TypeError(f"'{field_name}' must be an integer or float, got {type(value).__name__}.")
    if math.isnan(value) or math.isinf(value):
        raise ValueError(f"'{field_name}' must be a finite number.")
    if value <= 0:
        raise ValueError(f"'{field_name}' must be greater than zero. Received: {value}")
    return float(value)


class VirtualMachine:
    """Represents a Virtual Machine requesting CPU and RAM resources."""

    STATUS_PENDING = "PENDING"
    STATUS_ALLOCATED = "ALLOCATED"
    STATUS_REJECTED = "REJECTED"

    def __init__(
        self,
        vm_id: str,
        cpu_required: float,
        ram_required: float,
        status: str = STATUS_PENDING,
        allocated_host_id: Optional[str] = None,
        failure_reason: Optional[str] = None,
    ) -> None:
        """Initialize and validate VirtualMachine attributes.
        
        Args:
            vm_id: Unique string identifier for the VM.
            cpu_required: Number of CPU cores required (> 0).
            ram_required: Amount of RAM required in GB (> 0).
            status: Allocation status ('PENDING', 'ALLOCATED', 'REJECTED').
            allocated_host_id: ID of the host hosting this VM (if allocated).
            failure_reason: Explanation if allocation failed.
        """
        if not isinstance(vm_id, str) or not vm_id.strip():
            raise ValueError("Virtual machine 'vm_id' must be a non-empty string.")

        self.vm_id: str = vm_id.strip()
        self.cpu_required: float = validate_positive_number(cpu_required, "cpu_required")
        self.ram_required: float = validate_positive_number(ram_required, "ram_required")

        valid_statuses = {self.STATUS_PENDING, self.STATUS_ALLOCATED, self.STATUS_REJECTED}
        if status not in valid_statuses:
            raise ValueError(f"Invalid status '{status}'. Must be one of {valid_statuses}.")

        self.status: str = status
        self.allocated_host_id: Optional[str] = allocated_host_id
        self.failure_reason: Optional[str] = failure_reason

    def mark_allocated(self, host_id: str) -> None:
        """Mark the VM as successfully allocated to a host."""
        if not isinstance(host_id, str) or not host_id.strip():
            raise ValueError("Host ID must be a non-empty string.")
        self.status = self.STATUS_ALLOCATED
        self.allocated_host_id = host_id.strip()
        self.failure_reason = None

    def mark_rejected(self, reason: str) -> None:
        """Mark the VM as rejected due to insufficient capacity or other constraint."""
        self.status = self.STATUS_REJECTED
        self.allocated_host_id = None
        self.failure_reason = reason

    def reset(self) -> None:
        """Reset the VM to pending status."""
        self.status = self.STATUS_PENDING
        self.allocated_host_id = None
        self.failure_reason = None

    def clone(self) -> VirtualMachine:
        """Return a deep, independent copy of this VirtualMachine instance."""
        return VirtualMachine(
            vm_id=self.vm_id,
            cpu_required=self.cpu_required,
            ram_required=self.ram_required,
            status=self.status,
            allocated_host_id=self.allocated_host_id,
            failure_reason=self.failure_reason,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the VM instance to a dictionary."""
        return {
            "vm_id": self.vm_id,
            "cpu_required": self.cpu_required,
            "ram_required": self.ram_required,
            "status": self.status,
            "allocated_host_id": self.allocated_host_id,
            "failure_reason": self.failure_reason,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> VirtualMachine:
        """Construct a VirtualMachine from a dictionary."""
        return cls(
            vm_id=str(data.get("vm_id", "")),
            cpu_required=data.get("cpu_required"),
            ram_required=data.get("ram_required"),
            status=data.get("status", cls.STATUS_PENDING),
            allocated_host_id=data.get("allocated_host_id"),
            failure_reason=data.get("failure_reason"),
        )

    def __repr__(self) -> str:
        return (
            f"VirtualMachine(id={self.vm_id!r}, cpu={self.cpu_required}, "
            f"ram={self.ram_required}, status={self.status!r}, "
            f"host={self.allocated_host_id!r})"
        )
