"""Simulation service and algorithm comparison engine for VM resource allocation."""

from __future__ import annotations
from typing import Any, Dict, List, Type
from app.models.host import Host
from app.models.vm import VirtualMachine
from app.algorithms.base import BaseAllocationAlgorithm
from app.algorithms.first_fit import FirstFitAllocator
from app.algorithms.best_fit import BestFitAllocator
from app.algorithms.round_robin import RoundRobinAllocator


class SimulationEngine:
    """Coordinates VM allocation simulations and fair algorithm comparisons.
    
    Cloud Computing Objective:
    Allows evaluating and comparing multiple VM placement heuristics (First Fit,
    Best Fit, and Round Robin) using identical physical host configurations and
    workload sequences. Every simulation run uses fresh, isolated copies of the
    initial hosts and VMs to guarantee fair, non-interfering, and deterministic
    comparison.
    """

    ALGORITHMS: Dict[str, Type[BaseAllocationAlgorithm]] = {
        "first_fit": FirstFitAllocator,
        "best_fit": BestFitAllocator,
        "round_robin": RoundRobinAllocator,
    }

    ALGORITHM_DISPLAY_NAMES: Dict[str, str] = {
        "first_fit": "First Fit",
        "best_fit": "Best Fit",
        "round_robin": "Round Robin",
    }

    @classmethod
    def normalize_algorithm_key(cls, name: str) -> str:
        """Normalize user or API algorithm name to canonical key.
        
        Args:
            name: Algorithm name string (e.g., 'First Fit', 'first_fit', 'bestfit').
            
        Returns:
            Canonical algorithm key ('first_fit', 'best_fit', or 'round_robin').
            
        Raises:
            ValueError: If the algorithm name is not recognized.
        """
        if not isinstance(name, str):
            raise TypeError(f"Algorithm name must be a string, got {type(name).__name__}.")

        cleaned = name.strip().lower().replace(" ", "_").replace("-", "_")
        
        aliases = {
            "first_fit": "first_fit",
            "firstfit": "first_fit",
            "ff": "first_fit",
            "best_fit": "best_fit",
            "bestfit": "best_fit",
            "bf": "best_fit",
            "round_robin": "round_robin",
            "roundrobin": "round_robin",
            "rr": "round_robin",
        }

        if cleaned in aliases:
            return aliases[cleaned]

        valid_options = list(cls.ALGORITHMS.keys())
        raise ValueError(
            f"Unknown allocation algorithm '{name}'. Supported options are: {valid_options}."
        )

    @classmethod
    def get_allocator(cls, name: str) -> BaseAllocationAlgorithm:
        """Instantiate an allocator by algorithm name.
        
        Args:
            name: Name of the algorithm.
            
        Returns:
            An instance of BaseAllocationAlgorithm.
        """
        canonical_key = cls.normalize_algorithm_key(name)
        allocator_class = cls.ALGORITHMS[canonical_key]
        return allocator_class()

    @staticmethod
    def validate_inputs(hosts: List[Host], vms: List[VirtualMachine]) -> None:
        """Strictly validate input collections for hosts and virtual machines.
        
        Args:
            hosts: List of Host instances.
            vms: List of VirtualMachine instances.
            
        Raises:
            TypeError: If containers or items are of invalid types.
            ValueError: If duplicate host or VM IDs are detected.
        """
        if not isinstance(hosts, list):
            raise TypeError(f"'hosts' must be a list, got {type(hosts).__name__}.")
        if not isinstance(vms, list):
            raise TypeError(f"'vms' must be a list, got {type(vms).__name__}.")

        seen_host_ids = set()
        for idx, host in enumerate(hosts):
            if not isinstance(host, Host):
                raise TypeError(
                    f"Element at hosts[{idx}] is not a Host instance, got {type(host).__name__}."
                )
            if host.host_id in seen_host_ids:
                raise ValueError(f"Duplicate host_id detected: '{host.host_id}'.")
            seen_host_ids.add(host.host_id)

        seen_vm_ids = set()
        for idx, vm in enumerate(vms):
            if not isinstance(vm, VirtualMachine):
                raise TypeError(
                    f"Element at vms[{idx}] is not a VirtualMachine instance, got {type(vm).__name__}."
                )
            if vm.vm_id in seen_vm_ids:
                raise ValueError(f"Duplicate vm_id detected: '{vm.vm_id}'.")
            seen_vm_ids.add(vm.vm_id)

    @staticmethod
    def _clone_workload(
        hosts: List[Host], vms: List[VirtualMachine]
    ) -> tuple[List[Host], List[VirtualMachine]]:
        """Create pristine, independent copies of hosts and VMs for a simulation run.
        
        Ensures both hosts and VMs start in completely unallocated states regardless
        of previous operations, while preserving capacity definitions.
        """
        cloned_hosts = [h.clone() for h in hosts]
        for h in cloned_hosts:
            h.reset()

        cloned_vms = [v.clone() for v in vms]
        for v in cloned_vms:
            v.reset()

        return cloned_hosts, cloned_vms

    @classmethod
    def run_algorithm(
        cls,
        algorithm_name: str,
        hosts: List[Host],
        vms: List[VirtualMachine],
    ) -> Dict[str, Any]:
        """Execute a single allocation algorithm on cloned host and VM inputs.
        
        Args:
            algorithm_name: Identifier for the algorithm to run.
            hosts: List of Physical Hosts.
            vms: List of VirtualMachine requests.
            
        Returns:
            JSON-serializable dictionary with comprehensive simulation results.
        """
        cls.validate_inputs(hosts, vms)
        canonical_key = cls.normalize_algorithm_key(algorithm_name)
        allocator = cls.get_allocator(canonical_key)

        # Clone to guarantee non-destructive, isolated execution
        sim_hosts, sim_vms = cls._clone_workload(hosts, vms)

        # Handle empty host list explicitly
        if not sim_hosts and sim_vms:
            for vm in sim_vms:
                vm.mark_rejected("No physical hosts available for allocation.")
            steps = [
                {
                    "vm_id": vm.vm_id,
                    "cpu_required": vm.cpu_required,
                    "ram_required": vm.ram_required,
                    "status": vm.status,
                    "allocated_host_id": None,
                    "failure_reason": vm.failure_reason,
                }
                for vm in sim_vms
            ]
            summary_dict = cls._build_result_dict(
                canonical_key=canonical_key,
                algorithm_display_name=cls.ALGORITHM_DISPLAY_NAMES[canonical_key],
                hosts=sim_hosts,
                vms=sim_vms,
                steps=steps,
            )
            return summary_dict

        # Execute allocation workload
        summary = allocator.allocate_workload(vms=sim_vms, hosts=sim_hosts, in_place=True)

        return cls._build_result_dict(
            canonical_key=canonical_key,
            algorithm_display_name=summary.algorithm_name,
            hosts=summary.hosts,
            vms=summary.vms,
            steps=summary.steps,
        )

    @classmethod
    def compare_all(
        cls,
        hosts: List[Host],
        vms: List[VirtualMachine],
    ) -> Dict[str, Any]:
        """Run all three algorithms (First Fit, Best Fit, Round Robin) under identical conditions.
        
        Args:
            hosts: Initial physical host configurations.
            vms: Virtual machine workload in sequential arrival order.
            
        Returns:
            JSON-serializable comparison dictionary containing individual runs,
            a side-by-side comparison summary, and workload metadata.
        """
        cls.validate_inputs(hosts, vms)

        results: Dict[str, Dict[str, Any]] = {}
        summary_rows: List[Dict[str, Any]] = []

        algorithm_order = ["first_fit", "best_fit", "round_robin"]

        for key in algorithm_order:
            algo_result = cls.run_algorithm(algorithm_name=key, hosts=hosts, vms=vms)
            results[key] = algo_result

            metrics = algo_result["metrics"]
            summary_rows.append({
                "algorithm_key": key,
                "algorithm_name": cls.ALGORITHM_DISPLAY_NAMES[key],
                "successful_allocations": metrics["successful_allocations"],
                "failed_allocations": metrics["failed_allocations"],
                "allocation_success_rate": metrics["allocation_success_rate"],
                "cpu_utilization": metrics["cpu_utilization"],
                "ram_utilization": metrics["ram_utilization"],
                "allocated_cpu": metrics["allocated_cpu"],
                "allocated_ram": metrics["allocated_ram"],
                "remaining_cpu": metrics["remaining_cpu"],
                "remaining_ram": metrics["remaining_ram"],
                "total_cpu_capacity": metrics["total_cpu_capacity"],
                "total_ram_capacity": metrics["total_ram_capacity"],
            })

        initial_workload_meta = {
            "total_hosts": len(hosts),
            "total_cpu_capacity": sum(h.total_cpu for h in hosts),
            "total_ram_capacity": sum(h.total_ram for h in hosts),
            "total_vms_requested": len(vms),
            "total_cpu_requested": sum(v.cpu_required for v in vms),
            "total_ram_requested": sum(v.ram_required for v in vms),
        }

        return {
            "algorithms": results,
            "summary": summary_rows,
            "initial_workload": initial_workload_meta,
        }

    @classmethod
    def _build_result_dict(
        cls,
        canonical_key: str,
        algorithm_display_name: str,
        hosts: List[Host],
        vms: List[VirtualMachine],
        steps: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Construct the standardized, JSON-compliant result dictionary."""
        total_vms = len(vms)
        successful_allocations = sum(
            1 for vm in vms if vm.status == VirtualMachine.STATUS_ALLOCATED
        )
        failed_allocations = sum(
            1 for vm in vms if vm.status == VirtualMachine.STATUS_REJECTED
        )

        success_rate = (
            round((successful_allocations / total_vms) * 100.0, 2)
            if total_vms > 0
            else 0.0
        )

        total_cpu_capacity = sum(h.total_cpu for h in hosts)
        total_ram_capacity = sum(h.total_ram for h in hosts)

        allocated_cpu = round(sum(h.allocated_cpu for h in hosts), 2)
        allocated_ram = round(sum(h.allocated_ram for h in hosts), 2)

        remaining_cpu = round(sum(h.remaining_cpu for h in hosts), 2)
        remaining_ram = round(sum(h.remaining_ram for h in hosts), 2)

        cpu_utilization = (
            round((allocated_cpu / total_cpu_capacity) * 100.0, 2)
            if total_cpu_capacity > 0
            else 0.0
        )
        ram_utilization = (
            round((allocated_ram / total_ram_capacity) * 100.0, 2)
            if total_ram_capacity > 0
            else 0.0
        )

        failed_details = [
            {
                "vm_id": vm.vm_id,
                "cpu_required": vm.cpu_required,
                "ram_required": vm.ram_required,
                "failure_reason": vm.failure_reason or "Unknown capacity or placement constraint",
            }
            for vm in vms
            if vm.status == VirtualMachine.STATUS_REJECTED
        ]

        return {
            "algorithm_key": canonical_key,
            "algorithm_name": algorithm_display_name,
            "metrics": {
                "total_cpu_capacity": total_cpu_capacity,
                "allocated_cpu": allocated_cpu,
                "remaining_cpu": remaining_cpu,
                "cpu_utilization": cpu_utilization,
                "total_ram_capacity": total_ram_capacity,
                "allocated_ram": allocated_ram,
                "remaining_ram": remaining_ram,
                "ram_utilization": ram_utilization,
                "total_vms": total_vms,
                "successful_allocations": successful_allocations,
                "failed_allocations": failed_allocations,
                "allocation_success_rate": success_rate,
            },
            "hosts": [h.to_dict() for h in hosts],
            "vms": [v.to_dict() for v in vms],
            "failed_allocations": failed_details,
            "execution_steps": steps,
        }
