# A PROJECT REPORT ON
# VIRTUAL MACHINE RESOURCE ALLOCATION SIMULATOR

---

### Submitted in partial fulfillment of the requirements for the degree of
### **BACHELOR OF TECHNOLOGY / BACHELOR OF ENGINEERING**
### in
### **COMPUTER SCIENCE AND ENGINEERING / INFORMATION TECHNOLOGY**

---

**Submitted by:**
- **[STUDENT NAME]** (Register No: **[REGISTER NUMBER]**)

**Under the Guidance of:**
- **[GUIDE NAME AND DESIGNATION]**

---

### **DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING**
### **[COLLEGE / INSTITUTION NAME]**
### **[AFFILIATED UNIVERSITY NAME]**
### **[CITY, STATE, PIN CODE]**
### **[ACADEMIC YEAR: 2025 – 2026]**

---

\newpage

## Certificate

This is to certify that the project report entitled **"Virtual Machine Resource Allocation Simulator"** is a bona fide record of work carried out by **[STUDENT NAME]** (Register No: **[REGISTER NUMBER]**) in partial fulfillment of the requirements for the award of the degree of **Bachelor of Technology / Bachelor of Engineering** in **Computer Science and Engineering** during the academic year **[ACADEMIC YEAR]**.

\vspace{2cm}

**[GUIDE NAME]**  
Project Guide  
Department of Computer Science and Engineering  
[Institution Name]  

\vspace{1.5cm}

**[HEAD OF DEPARTMENT NAME]**  
Head of the Department  
Department of Computer Science and Engineering  
[Institution Name]  

\vspace{1.5cm}

Submitted for the Viva-Voce examination held on: \underline{\hspace{4cm}}

\vspace{1.5cm}

**Internal Examiner** \hfill **External Examiner**

---

\newpage

## Acknowledgements

I express my deepest gratitude to our Principal, **[PRINCIPAL NAME]**, and to the Head of the Department, **[HOD NAME]**, Department of Computer Science and Engineering, for providing the necessary infrastructure and environment to complete this project.

I am profoundly indebted to my project supervisor, **[GUIDE NAME]**, for valuable guidance, continuous encouragement, and constructive critique throughout the design, implementation, and testing phases of this simulator.

I also extend my sincere thanks to all faculty members of the Department of Computer Science and Engineering for their direct and indirect support, and to my family and friends for their understanding and encouragement.

\vspace{1.5cm}
\hfill **[STUDENT NAME]**

---

\newpage

## Abstract

In modern Cloud Computing datacenters providing Infrastructure as a Service (IaaS), efficient resource allocation is fundamental to maximizing return on hardware investment, reducing energy consumption, and complying with Service Level Agreements (SLAs). When customers provision heterogeneous Virtual Machines (VMs) with specific central processing unit (CPU) and memory (RAM) sizing, the cloud orchestrator must solve a multi-dimensional bin packing problem to decide which physical host should service each request. Inappropriate VM placement leads to multi-dimensional resource fragmentation—where unallocated CPU cores are stranded because host RAM is exhausted—or server over-subscription, resulting in Quality of Service (QoS) degradation.

This project designs and implements the **Virtual Machine Resource Allocation Simulator**, a full-stack, modular web-based educational simulation system. The simulator models physical host clusters and sequential VM arrival queues, implementing three classic allocation heuristics: **First Fit (FF)**, **Best Fit (BF)** utilizing a normalized residual-resource scoring model, and **Round Robin (RR)**. The backend is engineered using Python 3.13 and Flask following a clean domain-driven architecture, exposing a decoupled RESTful API. The frontend features an interactive, dark-themed datacenter monitoring dashboard built with HTML5, CSS3, JavaScript, and Chart.js 4.4. A critical architectural contribution of the system is the **Simulation Engine**, which enforces fair comparative benchmarking by executing workloads across identical, isolated clones of the physical cluster without state contamination. The system is verified by an automated test suite comprising 95 unit and integration tests achieving a 100% pass rate. The project provides an accessible, visually engaging platform for evaluating cloud resource allocation trade-offs.

---

\newpage

## Table of Contents

1. [Introduction](#1-introduction)
2. [Problem Statement](#2-problem-statement)
3. [Objectives](#3-objectives)
4. [Scope of the Project](#4-scope-of-the-project)
5. [Cloud Computing Background](#5-cloud-computing-background)
6. [Existing System and Its Limitations](#6-existing-system-and-its-limitations)
7. [Proposed System](#7-proposed-system)
8. [Software and Hardware Requirements](#8-software-and-hardware-requirements)
9. [System Architecture](#9-system-architecture)
10. [Module Description](#10-module-description)
11. [Algorithm Design](#11-algorithm-design)
    - 11.1 [First Fit Allocation](#111-first-fit-allocation)
    - 11.2 [Best Fit Allocation](#112-best-fit-allocation)
    - 11.3 [Round Robin Allocation](#113-round-robin-allocation)
12. [Best Fit Mathematical Formulation](#12-best-fit-mathematical-formulation)
13. [System Workflow](#13-system-workflow)
14. [API Design](#14-api-design)
15. [User Interface and Dashboard Design](#15-user-interface-and-dashboard-design)
16. [Testing Methodology](#16-testing-methodology)
17. [Test Results and Verification](#17-test-results-and-verification)
18. [Sample Simulation and Algorithm Comparison](#18-sample-simulation-and-algorithm-comparison)
19. [Advantages of the Proposed System](#19-advantages-of-the-proposed-system)
20. [Limitations](#20-limitations)
21. [Future Enhancements](#21-future-enhancements)
22. [Conclusion](#22-conclusion)
23. [References](#23-references)

---

\newpage

## 1. Introduction

Cloud computing has revolutionized modern enterprise IT by transforming computational power, storage, and networking into utility-based commodities delivered over the Internet. Under the Infrastructure as a Service (IaaS) delivery model, cloud service providers (CSPs) maintain vast hyperscale datacenters housing thousands of physical servers, commonly referred to as physical hosts. Through hardware virtualization, hypervisors partition physical compute, memory, and storage capacities into isolated, self-contained computational environments known as Virtual Machines (VMs).

A core operational challenge faced by cloud hypervisors and cluster orchestration platforms (such as OpenStack Nova, Kubernetes, VMware vSphere, and AWS EC2) is the **Virtual Machine Placement (VMP) problem**. When tenants submit requests to provision VMs with specific hardware footprints (such as 2 CPU cores and 4 GB of RAM), the management layer must determine which physical host should accommodate the request. 

Because physical servers possess multi-dimensional resource bounds (CPU cores, RAM capacity, network bandwidth, and disk I/O), placing VMs is a multi-capacity variant of the classic NP-hard bin packing problem. Different placement strategies exhibit distinct trade-offs: some focus on packing servers densely to allow idle hosts to be powered down (server consolidation for energy efficiency), while others distribute the workload uniformly to balance thermal load and hardware wear.

This project, titled **Virtual Machine Resource Allocation Simulator**, implements a web-based platform that allows students, educators, and cloud engineers to experiment with, visualize, and benchmark three fundamental allocation heuristics: First Fit, Best Fit, and Round Robin.

---

## 2. Problem Statement

In cloud datacenters, naive or uncontrolled VM placement introduces severe infrastructural inefficiencies:
1. **Multi-Dimensional Resource Fragmentation**: CPU cores and memory operate on completely different numerical scales. If an allocation algorithm places VMs without evaluating remaining capacity across both dimensions, a host may exhaust its RAM while 70% of its CPU cores remain idle. These unallocated cores become "stranded" and unusable, wasting expensive datacenter resources.
2. **Resource Over-Subscription & SLA Violations**: If admission control is not strictly enforced, allocating virtual instances beyond physical hardware capacities leads to CPU throttling, memory swapping, kernel panics, and direct violations of tenant Service Level Agreements (SLAs).
3. **Lack of Transparent Educational Tooling**: Commercial cloud hypervisors operate as proprietary black boxes. Students and practitioners cannot easily inspect step-by-step heuristic decisions, observe multi-dimensional packing trade-offs, or evaluate algorithms against identical workloads under controlled conditions.

---

## 3. Objectives

The primary objectives of this project are:
1. To model heterogeneous Physical Hosts and Virtual Machine resource requests with configurable CPU cores and RAM capacities in gigabytes.
2. To implement three classic allocation heuristics: **First Fit**, **Best Fit** (using normalized residual-resource scoring), and **Round Robin**.
3. To enforce strict admission control to prevent CPU and RAM over-allocation.
4. To engineer a **Simulation Engine** capable of executing workloads against independent, isolated clones of host pools to guarantee fair, non-interfering comparative benchmarking.
5. To expose backend simulation capabilities via a decoupled, robust Flask RESTful API.
6. To build an interactive, responsive datacenter monitoring dashboard utilizing HTML5, CSS3, JavaScript, and Chart.js for real-time visualization.
7. To substantiate the software engineering rigor of the system through automated unit and integration testing.

---

## 4. Scope of the Project

- **In Scope**:
  - Simulating static VM placement across heterogeneous physical hosts in Python memory.
  - Multi-capacity constraint verification (CPU cores and RAM in GB).
  - Tracking allocated, remaining, and utilization metrics per host and cluster-wide.
  - Tracking placement outcomes, including explicit failure reasons for rejected requests.
  - Side-by-side comparative benchmarking of First Fit, Best Fit, and Round Robin.
  - Interactive web UI with live server rack state cards and Chart.js graphs.
  - Comprehensive automated test suite using pytest.
- **Out of Scope**:
  - Deploying real virtual machines or interacting with external commercial cloud APIs (AWS, Azure, GCP).
  - Simulating dynamic runtime lifecycles (dynamic deallocation, live VM migration).
  - Modeling network bandwidth, disk I/O latency, or electrical power consumption.
  - Long-term persistent storage via a database (simulations reside in memory).

---

## 5. Cloud Computing Background

### 5.1 Infrastructure as a Service (IaaS)
IaaS provides virtualized computing resources over the internet. Physical servers in a datacenter are pooled, and hypervisors instantiate virtual instances on demand. The efficiency of an IaaS platform depends directly on its scheduling scheduler.

### 5.2 Multi-Dimensional Bin Packing
In single-dimensional bin packing, items of various sizes must be packed into the minimum number of fixed-size bins. In cloud computing, the problem is multi-dimensional because both CPU and RAM (as well as storage and network bandwidth) act as independent hard constraints. A host cannot accept a VM if either resource is insufficient.

### 5.3 Admission Control
Admission control is the validation gatekeeper in cloud scheduling. When a VM request arrives, admission control evaluates whether the cluster possesses sufficient remaining capacity. If no host can fulfill the constraints, the request is rejected immediately, shielding active tenants from performance degradation.

---

## 6. Existing System and Its Limitations

### 6.1 Description of Existing Approaches
In academic and training environments, VM allocation concepts are conventionally taught through static mathematical proofs, spreadsheet exercises, or command-line scripts that output raw terminal text. Heavy simulation frameworks such as CloudSim exist, but they carry steep learning curves, require complex Java enterprise setups, and lack intuitive visual web dashboards.

### 6.2 Limitations of the Existing System
- **No Interactive Visualization**: Terminal scripts fail to convey how individual server racks fill up in real time.
- **Lack of Fair Benchmarking**: Manual spreadsheet models rarely test First Fit, Best Fit, and Round Robin against the exact same initial state without error-prone manual resets.
- **Complex Setup**: Heavy enterprise simulators require extensive runtime configurations and IDE dependencies, distracting students from core algorithmic concepts.
- **Missing API Decoupling**: Standalone CLI scripts tightly couple business logic with terminal input/output, preventing integration with modern web frontends.

---

## 7. Proposed System

The proposed **Virtual Machine Resource Allocation Simulator** resolves these limitations by delivering a modular, web-based simulation platform:
- **Clean Architectural Separation**: The system separates domain models (`Host`, `VirtualMachine`), allocation algorithms (`FirstFit`, `BestFit`, `RoundRobin`), simulation management (`SimulationEngine`), and API controllers (`api.py`).
- **Fair Benchmark Comparison**: The engine creates pristine deep copies of physical hosts and VM queues for each algorithm, guaranteeing completely isolated and deterministic comparison.
- **Normalized Multi-Dimensional Scoring**: Best Fit uses a normalized formula that harmonizes CPU cores and RAM gigabytes onto a uniform 0.0 to 1.0 scale.
- **Modern Datacenter UI**: The responsive dashboard presents real-time KPI cards, interactive Chart.js visualizations, and live server rack representations.
- **Robust Automated Verification**: A 95-test automated test suite validates all boundary limits, edge cases, and API status codes.

---

## 8. Software and Hardware Requirements

### 8.1 Software Requirements
- **Operating System**: Microsoft Windows 10/11, Linux (Ubuntu 20.04+), or macOS 12+
- **Backend Language**: Python 3.10 or higher (Python 3.13 tested)
- **Web Framework**: Flask 3.1+ (Application Factory Pattern, Blueprints)
- **Automated Test Framework**: Pytest 9.1+
- **Frontend Technologies**: HTML5, CSS3, Vanilla JavaScript (ES6 Modules)
- **Charting Library**: Chart.js 4.4 (Loaded via CDN)
- **Web Browser**: Google Chrome, Mozilla Firefox, or Microsoft Edge

### 8.2 Hardware Requirements
- **Processor**: Intel Core i3 / AMD Ryzen 3 or higher (Dual-Core 2.0 GHz minimum)
- **RAM**: 4 GB minimum (8 GB recommended)
- **Storage**: 200 MB free hard disk space for project code and Python virtual environment
- **Network**: Internet connection required only for loading the Chart.js CDN library on initial browser load

---

## 9. System Architecture

The simulator is structured into four distinct layers following the principle of separation of concerns:

```mermaid
graph TD
    subgraph Presentation_Layer ["Presentation Tier (Browser)"]
        UI["Dashboard UI (HTML5 / CSS3 / ES6 JS)"]
        Charts["Chart.js Visualizations (4 Charts)"]
        Racks["Server Rack Cards & Placement Table"]
    end

    subgraph API_Layer ["REST API Tier (Flask)"]
        HealthEndpoint["GET /api/health"]
        AlgoEndpoint["GET /api/algorithms"]
        SimEndpoint["POST /api/simulate"]
        CompEndpoint["POST /api/compare"]
    end

    subgraph Service_Layer ["Simulation & Benchmark Service Tier"]
        Engine["SimulationEngine"]
        Cloner["Workload Cloner & State Isolation"]
        Metrics["Metric Aggregator (AllocationSummary)"]
    end

    subgraph Core_Layer ["Core Domain & Algorithm Tier"]
        FF["FirstFitAllocator"]
        BF["BestFitAllocator"]
        RR["RoundRobinAllocator"]
        HostModel["Host Model (Cores, RAM, VMS)"]
        VMModel["VirtualMachine Model (Lifecycle, Status)"]
    end

    UI -->|JSON over HTTP| API_Layer
    API_Layer -->|Instantiate & Validate| Engine
    Engine --> Cloner
    Cloner -->|Dispatch Pristine Copies| FF
    Cloner -->|Dispatch Pristine Copies| BF
    Cloner -->|Dispatch Pristine Copies| RR
    FF --> HostModel
    BF --> HostModel
    RR --> HostModel
    HostModel --> VMModel
    Engine --> Metrics
    Metrics -->|JSON Response| UI
```

### Architectural Flow Explanation:
1. **Presentation Layer**: Captures user inputs (host capacities, VM requirements, demo presets) and renders live Chart.js charts and server rack status cards.
2. **REST API Tier**: Validates HTTP payloads, verifies data types, enforces unique IDs, handles exceptions safely, and dispatches requests to the service layer.
3. **Service Layer (`SimulationEngine`)**: Clones independent copies of hosts and VMs to guarantee isolated runs, coordinates multi-algorithm comparisons, and calculates utilization metrics.
4. **Core Domain Tier**: Implements the mathematical and algorithmic placement logic, strictly enforcing capacity constraints.

---

## 10. Module Description

The project codebase is organized into five modular packages:

### 10.1 `app.models` (Domain Entities)
- `vm.py` (`VirtualMachine`): Represents a virtual machine request. Contains `vm_id`, `cpu_required`, `ram_required`, lifecycle `status` (`PENDING`, `ALLOCATED`, `REJECTED`), `allocated_host_id`, and `failure_reason`. Includes strict numeric validation (`validate_positive_number`) preventing boolean coercion, non-positive values, NaN, and infinity. Provides `.clone()` and `.to_dict()`.
- `host.py` (`Host`): Models a physical server node. Tracks `total_cpu`, `total_ram`, `allocated_vms`, and dynamically calculates `allocated_cpu`, `allocated_ram`, `remaining_cpu`, `remaining_ram`, `cpu_utilization`, and `ram_utilization`. Enforces admission control in `can_accommodate()` and prevents over-allocation in `allocate()`.

### 10.2 `app.algorithms` (Allocation Heuristics)
- `base.py` (`BaseAllocationAlgorithm`, `AllocationSummary`): Abstract base class defining `allocate_vm()` and `allocate_workload()`. `AllocationSummary` calculates cluster-wide metrics (success rates, total capacity, utilized capacity).
- `first_fit.py` (`FirstFitAllocator`): Sequential allocation from host index 0.
- `best_fit.py` (`BestFitAllocator`): Minimizes projected residual capacity using normalized scoring.
- `round_robin.py` (`RoundRobinAllocator`): Circular round-robin allocator with stateful attempt tracking.

### 10.3 `app.services` (Simulation & Benchmarking Engine)
- `simulator.py` (`SimulationEngine`): Provides `run_algorithm()` for single-heuristic simulations and `compare_all()` for side-by-side benchmarking. Guarantees non-destructive execution through `_clone_workload()`.

### 10.4 `app.routes` (REST API Controllers)
- `api.py` (`api_bp`): Flask Blueprint providing JSON endpoints (`/health`, `/algorithms`, `/simulate`, `/compare`). Implements `parse_hosts()` and `parse_vms()` to convert incoming JSON dictionaries into validated domain instances.

### 10.5 `app.static` & `app.templates` (Web Dashboard)
- `index.html`: Semantic single-page application dashboard layout.
- `style.css`: Professional dark datacenter UI styling with responsive grid layouts.
- `api.js`: Network client handling `fetch()` calls and error normalization.
- `charts.js`: `ChartManager` managing Chart.js lifecycles and canvas destruction.
- `app.js`: Main controller managing state, form events, preset loading, and DOM updates.

---

## 11. Algorithm Design

### 11.1 First Fit Allocation
- **Strategy**: Scans physical hosts sequentially from index $0$ to $N-1$.
- **Logic**: For an incoming VM $V$, inspect host $H_i$. If $H_i$ has both $\text{remaining\_cpu} \ge V_{\text{cpu}}$ and $\text{remaining\_ram} \ge V_{\text{ram}}$, immediately allocate $V$ to $H_i$ and terminate search.
- **Failure Mode**: If all $N$ hosts cannot accommodate $V$, mark $V$ as `REJECTED`.
- **Complexity**: Best case $O(1)$, worst case $O(N)$.

### 11.2 Best Fit Allocation
- **Strategy**: Evaluates all $N$ physical hosts to locate the host that leaves the **minimum residual resource capacity** after the proposed placement.
- **Logic**:
  1. Filter all hosts where $\text{can\_accommodate}(V)$ is `True`.
  2. For each feasible host, compute the projected normalized residual score.
  3. Sort feasible candidates in ascending order of score.
  4. Select the candidate with the lowest score. If multiple hosts have identical scores, apply deterministic tie-breaking by choosing the candidate with the lowest host list index.
- **Complexity**: $O(N)$ because all hosts must be examined.

### 11.3 Round Robin Allocation
- **Strategy**: Evenly distributes workloads across physical hosts in circular ring order.
- **Logic**:
  1. Maintain pointer `current_index` (initially $0$).
  2. For an incoming VM $V$, check candidate hosts starting at `start_index = current_index % N`.
  3. Check up to $N$ hosts in circular sequence: $\text{candidate\_idx} = (\text{start\_index} + \text{offset}) \pmod N$.
  4. If a candidate host accommodates $V$, allocate $V$ and update $\text{current\_index} = (\text{candidate\_idx} + 1) \pmod N$.
  5. If no host in the full cycle accommodates $V$, mark $V$ as `REJECTED` and advance $\text{current\_index} = (\text{start\_index} + 1) \pmod N$ past the failed attempt.
- **Complexity**: $O(N)$ worst case.

---

## 12. Best Fit Mathematical Formulation

In heterogeneous cloud computing, physical hosts have varying capacities, and VMs request multi-dimensional resources. To combine CPU and RAM into a single scalar metric, the simulator evaluates the **Normalized Residual-Resource Score**:

$$\text{Score}(H, V) = \left( \frac{\text{remaining\_cpu}_H - \text{cpu\_required}_V}{\text{total\_cpu}_H} \right) + \left( \frac{\text{remaining\_ram}_H - \text{ram\_required}_V}{\text{total\_ram}_H} \right)$$

### Formula Characteristics:
1. **Dimension Normalization**: Dividing remaining resources by total capacity produces unitless fractions between $0.0$ and $1.0$, preventing RAM (measured in tens of gigabytes) from numerically overpowering CPU (measured in single or double-digit cores).
2. **Minimization Objective**: A lower score indicates that a smaller fraction of the host's total resources will remain idle after allocation, representing a tighter packing fit.
3. **Tie-Breaking Determinism**:
   $$\text{Candidate Key} = \left(\text{round}(\text{Score}, 8), \, \text{host\_index}\right)$$
   Rounding to 8 decimal places eliminates floating-point precision jitter, while `host_index` provides a predictable tie-breaker.

---

## 13. System Workflow

The following sequence diagram illustrates the lifecycle of a simulation request:

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Browser
    participant API as Flask REST API (/api/simulate)
    participant Engine as SimulationEngine
    participant Allocator as BaseAllocationAlgorithm
    participant Host as Host Models

    User->>API: POST /api/simulate (JSON payload)
    Note over API: Parse & validate JSON body<br/>Check non-numeric/duplicate IDs
    API->>Engine: run_algorithm(algo, hosts, vms)
    Note over Engine: _clone_workload(hosts, vms)<br/>Reset counters & create isolated state
    Engine->>Allocator: allocate_workload(cloned_vms, cloned_hosts)
    loop For each VM in workload
        Allocator->>Host: can_accommodate(vm)
        alt Capacity is Sufficient
            Host-->>Allocator: True
            Allocator->>Host: allocate(vm)
            Note over Host: Update allocated_cpu/ram<br/>Mark VM ALLOCATED
        else Insufficient CPU or RAM
            Host-->>Allocator: False
            Note over Allocator: Check next candidate host<br/>If none fit: Mark VM REJECTED
        end
    end
    Allocator-->>Engine: AllocationSummary
    Note over Engine: Compute cluster utilization %<br/>Compile failed_allocations details
    Engine-->>API: JSON-serializable Result Dictionary
    API-->>User: HTTP 200 OK (JSON)
    Note over User: Update KPI cards, Racks & Chart.js
```

---

## 14. API Design

The Flask backend exposes four core RESTful endpoints under the `/api` prefix:

| Endpoint | Method | Purpose | Success Code | Error Codes |
| :--- | :---: | :--- | :---: | :---: |
| `/api/health` | `GET` | Service liveness health check | `200 OK` | `500` |
| `/api/algorithms` | `GET` | Retrieve list of available allocation heuristics | `200 OK` | `500` |
| `/api/simulate` | `POST` | Execute a single allocation algorithm on a workload | `200 OK` | `400`, `405`, `500` |
| `/api/compare` | `POST` | Run First Fit, Best Fit, and Round Robin on identical input | `200 OK` | `400`, `405`, `500` |

### 14.1 Standardized Error Contract
All client errors return HTTP 400 with a consistent JSON envelope:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Duplicate host_id detected: 'host-1'."
  }
}
```
Error codes include `INVALID_REQUEST`, `MISSING_FIELD`, `INVALID_TYPE`, `VALIDATION_ERROR`, and `UNKNOWN_ALGORITHM`. Stack traces and internal file paths are strictly suppressed from error responses.

---

## 15. User Interface and Dashboard Design

The web interface is styled using a modern **Dark Datacenter Design System** (`#0a0f1d` background, `#12192b` cards) that mimics cloud monitoring dashboards:

1. **Top Header**: Displays project identity and a live API status badge (`API Online` / `API Offline`).
2. **KPI Summary Cards**: Six metric cards displaying Physical Hosts, Requested VMs, Allocated VMs, Failed Allocations, Cluster CPU Utilization (with progress bar), and Cluster RAM Utilization (with progress bar).
3. **Physical Hosts Pool Panel**: Interactive form to add custom hosts with ID, name, CPU, and RAM, alongside a table of configured nodes with removal buttons.
4. **VM Workload Queue Panel**: Form to add VM requests and four demo preset buttons (*Balanced*, *CPU-Heavy*, *RAM-Heavy*, *Overloaded*) with an in-app confirmation modal.
5. **Execution Controls Bar**: Quick-action buttons to run First Fit, Best Fit, Round Robin, or Compare All Algorithms, complete with a loading overlay.
6. **Server Rack Visualizer**: Live visual node cards showing CPU and RAM utilization bars, numerical metrics, and hosted VM pill tags.
7. **Chart.js Grid**: Four responsive chart canvases:
   - *Chart A*: Per-Host Resource Utilization (Bar chart: CPU % vs. RAM %).
   - *Chart B*: Algorithm Performance Benchmark (Grouped bar chart: Success Rate %, CPU Util %, RAM Util %).
   - *Chart C*: Total Cluster Allocation (Stacked bar: Allocated vs. Remaining cores and GB).
   - *Chart D*: Allocation Outcomes (Doughnut chart: Allocated vs. Rejected count).
8. **VM Allocation Placements Table**: Filterable table displaying VM ID, required CPU/RAM, status badge (`ALLOCATED` / `REJECTED`), assigned host, and detailed placement or rejection explanations.

---

## 16. Testing Methodology

The project adheres to automated testing standards to ensure stability, edge-case resilience, and mathematical correctness:

1. **Unit Testing (`pytest`)**:
   - Model tests (`test_models.py`): Verifies valid initialization, boundary capacity rejection, rejection of booleans/NaNs/strings, property calculation, `.clone()` independence, and `.to_dict()` serialization.
   - Algorithm tests (`test_algorithms.py`): Verifies sequential placement in First Fit, residual score accuracy and tie-breaking in Best Fit, circular pointer advancement in Round Robin, and strict over-allocation prevention.
2. **Integration Testing**:
   - Simulator tests (`test_simulator.py`): Verifies `SimulationEngine` execution, comparison structure, state isolation, determinism, empty host lists, empty workloads, and JSON serialization.
   - API tests (`test_api.py`): Uses Flask's test client to verify HTTP status codes (200, 400, 404, 405, 500), payload parsing, missing fields, duplicate IDs, and internal exception containment.
3. **Browser Smoke Testing**:
   - Automated browser interaction verifies page loading, API health checking, preset loading via modal confirmation, chart rendering, and table filtering.

---

## 17. Test Results and Verification

### 17.1 Automated Backend Test Execution
All 95 automated test cases were executed using pytest within the virtual environment:

```powershell
.venv\Scripts\pytest -v tests/
```

### Summary of Results:
```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\gkt35\full stack training\My Projects\CC Project
collected 95 items

tests/test_algorithms.py (14 tests) .................... PASSED [ 14%]
tests/test_api.py (27 tests) ........................... PASSED [ 43%]
tests/test_models.py (34 tests) ........................ PASSED [ 77%]
tests/test_simulator.py (20 tests) ..................... PASSED [100%]

============================= 95 passed in 0.90s =============================
```
- **Test Pass Rate**: **100% (95 passed, 0 failed, 0 skipped, 0 warnings)**.

### 17.2 Browser Integration Observations
- The web dashboard was launched via `python run.py` at `http://127.0.0.1:5000`.
- Verified that all static CSS and JavaScript assets loaded with HTTP 200/304.
- Verified that Chart.js canvases render without JavaScript console errors.
- Verified that canvas instances are properly destroyed and re-instantiated upon consecutive simulation runs.

---

## 18. Sample Simulation and Algorithm Comparison

To evaluate algorithm behavior, two representative workloads were executed through the simulation engine:

### 18.1 Experiment A: Balanced Workload (Example Observation)
- **Cluster Capacity**: 3 Physical Hosts (Total: 32 Cores, 64 GB RAM)
  - `host-1`: 8 Cores, 16 GB RAM
  - `host-2`: 8 Cores, 16 GB RAM
  - `host-3`: 16 Cores, 32 GB RAM
- **Workload**: 6 VMs requesting 18 Cores and 40 GB RAM total.

#### Results Comparison Table:
| Metric | First Fit | Best Fit | Round Robin |
| :--- | :---: | :---: | :---: |
| **VMs Allocated / Requested** | 6 / 6 | 6 / 6 | 6 / 6 |
| **Allocation Success Rate** | **100.0%** | **100.0%** | **100.0%** |
| **Cluster CPU Utilization** | 56.25% (18/32) | 56.25% (18/32) | 56.25% (18/32) |
| **Cluster RAM Utilization** | 62.50% (40/64) | 62.50% (40/64) | 62.50% (40/64) |
| **Placement Distribution** | Concentrated on hosts 1 & 2 | Distributed to minimize residual | Evenly spread across 1, 2, 3 |

*Observation*: When cluster capacity is abundant, all three algorithms achieve 100% allocation success. However, First Fit leaves Host 3 underutilized, Best Fit tightly packs smaller nodes, and Round Robin distributes the compute load evenly.

### 18.2 Experiment B: Overloaded Workload with Rejection (Example Observation)
- **Cluster Capacity**: 2 Micro Hosts (Total: 8 Cores, 16 GB RAM)
  - `host-micro-1`: 4 Cores, 8 GB RAM
  - `host-micro-2`: 4 Cores, 8 GB RAM
- **Workload**: 5 VMs requesting 25 Cores and 50 GB RAM total (including one 12-core monolith VM).

#### Results Comparison Table:
| Metric | First Fit | Best Fit | Round Robin |
| :--- | :---: | :---: | :---: |
| **VMs Allocated / Requested** | 2 / 5 | 2 / 5 | 2 / 5 |
| **Failed Allocations** | 3 | 3 | 3 |
| **Allocation Success Rate** | **40.0%** | **40.0%** | **40.0%** |
| **Cluster CPU Utilization** | 100.0% (8/8) | 100.0% (8/8) | 100.0% (8/8) |
| **Cluster RAM Utilization** | 100.0% (16/16) | 100.0% (16/16) | 100.0% (16/16) |
| **Admission Control Status** | Rejections logged | Rejections logged | Rejections logged |

*Observation*: When workload demand exceeds capacity, all three algorithms correctly enforce admission control. The simulator records explicit rejection reasons (e.g., `Insufficient CPU or RAM across all 2 hosts`) without crashing or corrupting cluster state.

---

## 19. Advantages of the Proposed System

1. **Fair Comparison Guarantees**: Deep cloning of workload states ensures that no heuristic benefits from a prior algorithm's placements.
2. **Multi-Dimensional Constraint Handling**: Simultaneously balances CPU cores and RAM gigabytes on normalized mathematical scales.
3. **Decoupled Architecture**: Flask REST API allows independent testing and potential integration with alternative frontends (e.g., CLI, mobile apps).
4. **Rich Visual Feedback**: Interactive Chart.js charts and live server rack representations make complex allocation concepts intuitive.
5. **Zero Complex Dependencies**: Does not require heavy databases, Docker daemons, or Node.js build pipelines; runs natively with Python and standard browsers.
6. **High Code Quality**: Backed by 95 automated tests with 100% pass rate.

---

## 20. Limitations

1. **In-Memory Volatility**: Physical host configurations and VM workloads reside in server memory; data resets when the Python server restarts.
2. **Static Scheduling Scope**: VMs are allocated in static arrival order; dynamic VM departures, runtime durations, and live migrations are not modeled.
3. **Single Cluster Horizon**: Does not simulate multi-datacenter geographic latency, network bandwidth limits, or power grid telemetry.
4. **Frontend CDN Dependency**: The Chart.js library is loaded via CDN; initial dashboard rendering requires an active internet connection.

---

## 21. Future Enhancements

1. **Dynamic Lifecycle Simulation**: Introducing a time-stepped simulation engine with VM lifespan clocks and dynamic deallocation events.
2. **Live VM Migration & Defragmentation**: Implementing hypervisor defragmentation policies that migrate running instances to consolidate underutilized hosts.
3. **Energy-Aware Metaheuristics**: Adding Genetic Algorithms (GA) or Particle Swarm Optimization (PSO) to optimize multi-objective fitness functions (Energy Consumption vs. SLA Violations).
4. **Database Persistence**: Integrating SQLite or PostgreSQL with SQLAlchemy to store custom cluster topologies and export historical CSV/PDF benchmark reports.
5. **Offline CDN Bundling**: Packaging Chart.js locally in the `static/js/` directory for completely offline intranet laboratory environments.

---

## 22. Conclusion

The **Virtual Machine Resource Allocation Simulator** successfully achieves all its design and educational objectives. By implementing First Fit, Best Fit (with normalized residual scoring), and Round Robin within a clean domain-driven Python architecture, the project provides a rigorous yet accessible simulation of cloud resource management.

The decoupled Flask REST API, paired with a modern dark-themed datacenter dashboard and dynamic Chart.js visualizations, offers an intuitive interface for exploring multi-dimensional bin packing, admission control, and datacenter efficiency trade-offs. Backed by 95 passing automated tests and verified browser interactions, this project provides a solid technical foundation for academic demonstration and further research in cloud computing resource scheduling.

---

\newpage

## 23. References

1. **Mell, P., & Grance, T.** (2011). *The NIST Definition of Cloud Computing*. National Institute of Standards and Technology (NIST), Special Publication 800-145.
2. **Buyya, R., Yeo, C. S., Venugopal, S., Broberg, J., & Brandic, I.** (2009). *Cloud computing and emerging IT platforms: Vision, hype, and reality for delivering computing as the 5th utility*. Future Generation Computer Systems, 25(6), 599-616.
3. **Armbrust, M., Fox, A., Griffith, R., Joseph, A. D., Katz, R., Konwinski, A., Lee, P., Patterson, D., Rabkin, A., Stoica, I., & Zaharia, M.** (2010). *A view of cloud computing*. Communications of the ACM, 53(4), 50-58.
4. **Beloglazov, A., & Buyya, R.** (2012). *Optimal online deterministic algorithms and adaptive heuristics for energy and performance efficient dynamic consolidation of virtual machines in Cloud data centers*. Concurrency and Computation: Practice and Experience, 24(13), 1397-1420.
5. **Coffman, E. G., Garey, M. R., & Johnson, D. S.** (1996). *Approximation algorithms for bin packing: A survey*. Approximation algorithms for NP-hard problems, PWS Publishing, 46-93.
6. **Grinberg, M.** (2018). *Flask Web Development: Developing Web Applications with Python* (2nd ed.). O'Reilly Media.
