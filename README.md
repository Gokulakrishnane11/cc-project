# Virtual Machine Resource Allocation Simulator

A modular, web-based cloud computing simulation system that demonstrates and compares how multi-tenant cloud datacenters schedule and allocate virtual machine (VM) resource requests across heterogeneous physical hosts.

Developed for the **Cloud Computing** subject curriculum.

---

## 1. Project Overview

Cloud infrastructure providers (such as AWS EC2, Google Compute Engine, and Microsoft Azure) manage vast clusters of physical servers (hosts). When users request virtual machine instances with specific CPU and memory requirements, the hypervisor/cloud orchestrator must decide which physical host should accommodate each request. 

This project simulates physical host clusters, receives multi-VM workloads, and visualizes the allocation process using three core scheduling heuristics:
1. **First Fit (FF)**
2. **Best Fit (BF)** (with normalized residual-resource scoring)
3. **Round Robin (RR)**

The system provides an interactive dashboard powered by a Flask REST API and Chart.js, rendering real-time resource utilization, allocation success rates, server rack visualizations, and fair algorithm benchmark comparisons.

> [!NOTE]
> This application is an educational **simulation**. It simulates host capacities and virtual machine provisioning in Python memory; it does not launch hardware-level virtual machines or incur paid cloud infrastructure costs.

---

## 2. Problem Statement

In a cloud datacenter, virtual machine provisioning faces two competing challenges:
1. **Resource Fragmentation & Wastage**: Placing VMs arbitrarily can strand unallocated CPU on one machine and unallocated RAM on another, leading to low overall cluster utilization.
2. **Over-Allocation & Congestion**: Overloading physical servers beyond their rated CPU core or RAM capacity degrades Quality of Service (QoS) and breaches Service Level Agreements (SLAs).

Understanding how different placement heuristics manage residual capacity, balance workloads, and prevent over-allocation is fundamental to Cloud Computing architecture.

---

## 3. Project Objectives

- Model physical hosts with independent CPU (cores) and RAM (GB) constraints.
- Model virtual machine requests with configurable CPU and RAM sizing.
- Implement and benchmark three classic allocation algorithms: **First Fit**, **Best Fit**, and **Round Robin**.
- Enforce strict capacity limits and prevent CPU or RAM over-allocation.
- Guarantee **fair algorithm comparison** by executing workloads against pristine, isolated copies of identical cluster configurations.
- Expose a clean, decoupled RESTful API using Flask.
- Provide a responsive dashboard featuring interactive Chart.js visualizations, live host rack representations, and preset demonstration workloads.
- Ensure production-grade code quality backed by a comprehensive automated test suite (95 tests).

---

## 4. Cloud Computing Concepts Demonstrated

- **Infrastructure as a Service (IaaS)**: Simulating host clusters and virtual compute instances.
- **Resource Heterogeneity**: Managing physical nodes with unequal hardware specifications.
- **Bin Packing & VM Placement Heuristics**: Formulating multi-dimensional resource packing (CPU + RAM).
- **Residual Resource Fragmentation**: Measuring stranded host resources after placement.
- **Multi-Tenant Scheduling Fair Comparison**: Evaluating multiple schedulers using identical initial conditions and sequential arrival queues.
- **Admission Control & Capacity Constraints**: Preventing hardware exhaustion through strict rejection mechanisms.

---

## 5. Key Features

- **Interactive Datacenter Dashboard**: Dark-themed monitoring UI displaying KPI cards, server racks, and placement tables.
- **Real-Time Visualization (Chart.js)**:
  - Per-Host CPU and RAM utilization percentages.
  - Multi-metric algorithm benchmark comparison (Success Rate vs. CPU Util vs. RAM Util).
  - Total cluster capacity allocation (Allocated vs. Remaining).
  - Allocation outcomes (Successful vs. Rejected doughnut breakdown).
- **Physical Server Rack Visualizer**: Visual host cards showing live progress bars, remaining capacities, and hosted VM pill tags.
- **Workload Presets**:
  - *Balanced*: 3 hosts, 6 mixed workloads (100% allocation success).
  - *CPU-Heavy*: Compute-bound workload demonstrating CPU bottlenecks.
  - *RAM-Heavy*: Memory-bound workload demonstrating memory exhaustion.
  - *Overloaded*: Constrained cluster demonstrating admission control and explicit failure reasons.
- **Safe Preset Confirmation**: In-app modal dialog preventing accidental replacement of configured workloads.
- **Status Filtering**: Filter placement tables by *All*, *Allocated Only*, or *Rejected Only*.
- **Comprehensive REST API**: Clean endpoints for health, algorithm metadata, single-algorithm runs, and 3-algorithm comparisons.

---

## 6. Technology Stack

- **Backend Runtime**: Python 3.13
- **Web Framework**: Flask 3.1 (Application Factory Pattern, Blueprints)
- **Frontend Core**: HTML5, Vanilla CSS3 (Custom Dark Datacenter Design System), Vanilla JavaScript (ES6 Modules)
- **Data Visualization**: Chart.js 4.4 (Loaded via CDN)
- **Automated Testing**: Pytest 9.1

---

## 7. Project Directory Structure

```text
CC Project/
├── .gitignore                    # Git exclusion rules (__pycache__, .venv, cache)
├── requirements.txt              # Production and test dependencies (Flask, pytest)
├── run.py                        # Application entry point (http://127.0.0.1:5000)
├── README.md                     # Comprehensive project documentation
├── docs/
│   ├── VIVA_PREPARATION.md       # Oral examination guide, 60s pitch, 30 Q&As
│   └── DEMO_GUIDE.md             # 5-minute practical demonstration walkthrough
├── app/
│   ├── __init__.py               # Flask application factory (create_app)
│   ├── models/
│   │   ├── __init__.py           # Exports Host, VirtualMachine, validators
│   │   ├── host.py               # Physical Host model & capacity logic
│   │   └── vm.py                 # Virtual Machine model & lifecycle states
│   ├── algorithms/
│   │   ├── __init__.py           # Exports allocators & AllocationSummary
│   │   ├── base.py               # Abstract BaseAllocationAlgorithm interface
│   │   ├── first_fit.py          # First Fit implementation
│   │   ├── best_fit.py           # Best Fit implementation (residual scoring)
│   │   └── round_robin.py        # Round Robin implementation (circular)
│   ├── services/
│   │   ├── __init__.py           # Exports SimulationEngine
│   │   └── simulator.py          # Simulation engine & fair comparison service
│   ├── routes/
│   │   ├── __init__.py           # Exports api_bp
│   │   └── api.py                # REST API endpoints & input validation
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css         # Dark datacenter styling, responsive grid
│   │   └── js/
│   │       ├── api.js            # Network client for Flask API
│   │       ├── charts.js         # ChartManager (lifecycle & canvas handling)
│   │       └── app.js            # Frontend controller, state & table rendering
│   └── templates/
│       └── index.html            # Single-page simulation dashboard
└── tests/
    ├── __init__.py
    ├── test_models.py            # Unit tests for Host & VM validation (34 tests)
    ├── test_algorithms.py        # Unit tests for allocation heuristics (14 tests)
    ├── test_simulator.py         # Unit tests for SimulationEngine (20 tests)
    └── test_api.py               # Integration tests for Flask REST API (27 tests)
```

---

## 8. System Architecture

The project strictly follows a layered architecture to ensure separation of concerns:

```
┌────────────────────────────────────────────────────────┐
│                   Web Browser UI                       │
│    (HTML5 / CSS3 / JavaScript ES6 / Chart.js 4.4)      │
└───────────────────────────┬────────────────────────────┘
                            │ JSON over HTTP (fetch)
                            ▼
┌────────────────────────────────────────────────────────┐
│             Flask REST API Layer (app/routes/api.py)   │
│       Input Parsing • Type Validation • Error Handlers │
└───────────────────────────┬────────────────────────────┘
                            │ Instantiates clean models
                            ▼
┌────────────────────────────────────────────────────────┐
│         Simulation Service (app/services/simulator.py) │
│       Workload Cloning • State Isolation • Metrics     │
└───────────────────────────┬────────────────────────────┘
                            │ Dispatches to allocator
                            ▼
┌────────────────────────────────────────────────────────┐
│     Allocation Algorithms (app/algorithms/)            │
│       First Fit    •    Best Fit    •    Round Robin   │
└───────────────────────────┬────────────────────────────┘
                            │ Mutates cloned host state
                            ▼
┌────────────────────────────────────────────────────────┐
│              Domain Models (app/models/)               │
│          Host (Cores, RAM) • VirtualMachine            │
└────────────────────────────────────────────────────────┘
```

---

## 9. Allocation Algorithms Explained

### A. First Fit
- **Principle**: Scans physical hosts sequentially starting from the first host (index 0). Allocates the incoming VM to the first host that possesses sufficient unallocated CPU cores and RAM.
- **Advantages**: Fast, low computational overhead ($O(1)$ to $O(N)$ lookup).
- **Disadvantages**: Tends to heavily pack the first few hosts while leaving trailing hosts underutilized, creating uneven wear and resource fragmentation.

### B. Best Fit
- **Principle**: Evaluates all feasible hosts that can satisfy the VM request and chooses the host that leaves the **minimum residual resource capacity** after placement.
- **Advantages**: Maximizes packing density; leaves larger contiguous free blocks on other hosts for future large VMs.
- **Disadvantages**: Can lead to small, unusable "slivers" of stranded resources if VMs are deallocated dynamically.

### C. Round Robin
- **Principle**: Distributes VM allocations cyclically across all physical hosts in a ring sequence. Starts evaluating hosts immediately after the previous allocation attempt.
- **Advantages**: Promotes even thermal and load distribution across the datacenter cluster.
- **Disadvantages**: May fragment large host blocks and result in earlier allocation rejections if large VMs arrive later.

---

## 10. Best Fit Scoring Formula & Tie-Breaking

To balance multi-dimensional resources (CPU cores and RAM in GB), Best Fit calculates a **Normalized Residual Resource Score** for every candidate host capable of accommodating the VM:

$$\text{score} = \left(\frac{\text{remaining\_cpu} - \text{vm.cpu\_required}}{\text{total\_cpu}}\right) + \left(\frac{\text{remaining\_ram} - \text{vm.ram\_required}}{\text{total\_ram}}\right)$$

Where:
- $\text{remaining\_cpu} - \text{vm.cpu\_required}$: Projected remaining CPU cores after placement.
- $\text{remaining\_ram} - \text{vm.ram\_required}$: Projected remaining RAM after placement.
- Lower score indicates a tighter, more efficient fit.

**Deterministic Tie-Breaking Rule**:
When two or more hosts yield identical residual scores, Best Fit deterministically selects the host with the **lowest list index** `(round(score, 8), host_index)`.

---

## 11. CPU and RAM Allocation Constraints

A physical host $H$ can accommodate virtual machine $V$ if and only if both conditions are simultaneously satisfied:

$$\text{remaining\_cpu}_H \ge \text{cpu\_required}_V \quad \text{AND} \quad \text{remaining\_ram}_H \ge \text{ram\_required}_V$$

- If CPU fits but RAM is insufficient: Allocation is refused.
- If RAM fits but CPU is insufficient: Allocation is refused.
- If allocation is refused across all hosts: VM status is marked `REJECTED`, and the detailed reason is logged in `failed_allocations`.

---

## 12. Simulation Metrics & Formulas

1. **CPU Utilization Percentage**:
   $$\text{CPU Utilization (\%)} = \left(\frac{\sum \text{allocated\_cpu}}{\sum \text{total\_cpu\_capacity}}\right) \times 100$$

2. **RAM Utilization Percentage**:
   $$\text{RAM Utilization (\%)} = \left(\frac{\sum \text{allocated\_ram}}{\sum \text{total\_ram\_capacity}}\right) \times 100$$

3. **Allocation Success Rate**:
   $$\text{Success Rate (\%)} = \left(\frac{\text{Successful Allocations}}{\text{Total Requested VMs}}\right) \times 100$$
   *(Defined strictly as 0.0% when workload contains 0 VMs).*

4. **Remaining Cluster Capacity**:
   $$\text{Remaining CPU} = \text{Total CPU} - \text{Allocated CPU}$$
   $$\text{Remaining RAM} = \text{Total RAM} - \text{Allocated RAM}$$

---

## 13. Installation & Setup Instructions (Windows PowerShell)

### Prerequisites
- Python 3.10 or newer (Python 3.13 tested)
- Modern web browser (Chrome, Edge, Firefox)

### Step 1: Open PowerShell and Navigate to Project
```powershell
cd "c:\Users\gkt35\full stack training\My Projects\CC Project"
```

### Step 2: Initialize Virtual Environment
```powershell
python -m venv .venv
```

### Step 3: Activate Virtual Environment
```powershell
.venv\Scripts\Activate.ps1
```
*(If PowerShell execution policies block script execution, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 14. Starting the Application

With the virtual environment active, run:

```powershell
python run.py
```

Expected output:
```text
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

---

## 15. Opening the Dashboard

Open your web browser and navigate to:
```text
http://127.0.0.1:5000
```

The status badge in the top right header will indicate **"API Online"** with a glowing green indicator.

---

## 16. REST API Documentation

### 1. Health Check
- **Route:** `GET /api/health`
- **Response (200 OK):**
```json
{
  "service": "VM Resource Allocation Simulator API",
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. Available Algorithms
- **Route:** `GET /api/algorithms`
- **Response (200 OK):**
```json
{
  "algorithms": [
    {
      "id": "first_fit",
      "name": "First Fit",
      "description": "Sequentially assigns each VM to the first physical host with sufficient available CPU cores and RAM capacity."
    },
    {
      "id": "best_fit",
      "name": "Best Fit",
      "description": "Selects the feasible physical host that leaves the minimum normalized residual-resource score (tightest fit) after the proposed allocation."
    },
    {
      "id": "round_robin",
      "name": "Round Robin",
      "description": "Evenly distributes VM allocations cyclically across physical hosts, verifying CPU and RAM limits before placement."
    }
  ]
}
```

### 3. Run Single Simulation
- **Route:** `POST /api/simulate`
- **Headers:** `Content-Type: application/json`
- **Request Body:**
```json
{
  "algorithm": "first_fit",
  "hosts": [
    { "host_id": "host-1", "name": "Node A", "total_cpu": 8, "total_ram": 16 },
    { "host_id": "host-2", "name": "Node B", "total_cpu": 8, "total_ram": 16 }
  ],
  "vms": [
    { "vm_id": "vm-web-1", "cpu_required": 2, "ram_required": 4 },
    { "vm_id": "vm-db-1", "cpu_required": 4, "ram_required": 8 }
  ]
}
```
- **Response (200 OK):**
```json
{
  "algorithm_key": "first_fit",
  "algorithm_name": "First Fit",
  "metrics": {
    "allocated_cpu": 6.0,
    "allocated_ram": 12.0,
    "allocation_success_rate": 100.0,
    "cpu_utilization": 37.5,
    "failed_allocations": 0,
    "ram_utilization": 37.5,
    "remaining_cpu": 10.0,
    "remaining_ram": 20.0,
    "successful_allocations": 2,
    "total_cpu_capacity": 16.0,
    "total_ram_capacity": 32.0,
    "total_vms": 2
  },
  "hosts": [ ... ],
  "vms": [ ... ],
  "failed_allocations": [],
  "execution_steps": [ ... ]
}
```

### 4. Compare All Algorithms
- **Route:** `POST /api/compare`
- **Headers:** `Content-Type: application/json`
- **Request Body:**
```json
{
  "hosts": [
    { "host_id": "h1", "total_cpu": 4, "total_ram": 8 },
    { "host_id": "h2", "total_cpu": 8, "total_ram": 16 }
  ],
  "vms": [
    { "vm_id": "v1", "cpu_required": 2, "ram_required": 4 },
    { "vm_id": "v2", "cpu_required": 4, "ram_required": 8 }
  ]
}
```
- **Response (200 OK):**
```json
{
  "algorithms": {
    "first_fit": { ... },
    "best_fit": { ... },
    "round_robin": { ... }
  },
  "summary": [
    {
      "algorithm_key": "first_fit",
      "algorithm_name": "First Fit",
      "allocation_success_rate": 100.0,
      "cpu_utilization": 50.0,
      "ram_utilization": 50.0,
      "successful_allocations": 2,
      "failed_allocations": 0
    },
    { ... },
    { ... }
  ],
  "initial_workload": {
    "total_hosts": 2,
    "total_cpu_capacity": 12.0,
    "total_ram_capacity": 24.0,
    "total_vms_requested": 2,
    "total_cpu_requested": 6.0,
    "total_ram_requested": 12.0
  }
}
```

### 5. Error Response Format
All client or server errors return a standardized JSON structure:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Duplicate host_id detected: 'host-1'."
  }
}
```

---

## 17. Running the Test Suite

Execute pytest from the project root using the virtual environment:

```powershell
.venv\Scripts\pytest -v tests/
```

All 95 unit and integration tests will execute and pass:
```text
tests/test_models.py (34 tests) .................... PASSED
tests/test_algorithms.py (14 tests) ................ PASSED
tests/test_simulator.py (20 tests) ................. PASSED
tests/test_api.py (27 tests) ....................... PASSED
============================= 95 passed in ~1.0s =============================
```

---

## 18. Demonstration Workflow Using Presets

1. **Step 1: Inspect Default Cluster**:
   - On initial load, the dashboard pre-loads the **Balanced** preset: 3 hosts (32 cores, 64 GB RAM) and 6 VMs.
2. **Step 2: Run First Fit**:
   - Click **First Fit**. Notice how VMs pack into `Rack 1 - Node Alpha` first before spilling over.
3. **Step 3: Run Best Fit**:
   - Click **Best Fit**. Notice tighter residual capacity matching.
4. **Step 4: Run Round Robin**:
   - Click **Round Robin**. Observe that VMs are spread across `host-1`, `host-2`, and `host-3` sequentially.
5. **Step 5: Benchmark Comparison**:
   - Click **Compare All Algorithms**.
   - Review the **Algorithm Benchmark Comparison Table** and the **Grouped Bar Chart** showing side-by-side Success Rate and CPU/RAM utilization.
6. **Step 6: Demonstrate Capacity Limits & Rejections**:
   - Click the **Overloaded** preset button.
   - In the confirmation modal, click **Replace & Load**.
   - Click **Compare All Algorithms**.
   - Inspect the **Failed Allocations** KPI (3 rejected) and the VM table displaying red `REJECTED` badges with explicit reasons like `"Insufficient CPU or RAM across all 2 hosts for Best Fit"`.

---

## 19. Limitations & Future Enhancements

### Current Limitations
- **In-Memory Volatility**: Physical hosts and VM workloads reside in Python memory for the session; no SQL/NoSQL database persistence is used.
- **Static Scheduling**: VMs are placed sequentially without simulated runtime durations or dynamic deallocation events.
- **Single-Cluster Scope**: Network bandwidth, inter-rack latency, and power consumption metrics are not modeled.

### Proposed Future Enhancements
- **Dynamic VM Lifecycles**: Adding time-series simulation with VM departure and dynamic defragmentation (Live Migration).
- **Genetic / Multi-Objective Heuristics**: Implementing metaheuristic schedulers (Genetic Algorithms or Particle Swarm Optimization) to optimize energy consumption alongside utilization.
- **Database Persistence**: Integrating SQLite or PostgreSQL for saving custom host topologies and historical benchmark logs.

---

## 20. Conclusion

The **Virtual Machine Resource Allocation Simulator** offers a comprehensive, visually engaging platform to explore core Cloud Computing concepts. By combining rigorous mathematical modeling in Python with an interactive modern dashboard and automated testing, the project demonstrates how allocation heuristics directly impact datacenter efficiency, fragmentation, and quality of service.
