# Demonstration Guide & Presentation Script

**Project:** Virtual Machine Resource Allocation Simulator  
**Subject:** Cloud Computing Practical Defense  
**Estimated Demo Time:** 5 Minutes

---

## 1. Prerequisites

Before starting the presentation, ensure you have:
1. A laptop running Windows (or Linux/macOS) with Python 3.10+ installed.
2. A terminal / PowerShell prompt open at the project root directory.
3. Google Chrome, Microsoft Edge, or Mozilla Firefox.
4. Internet access (to load the Chart.js library via CDN).

---

## 2. Quick Application Startup

### Step 1: Open PowerShell
```powershell
cd "c:\Users\gkt35\full stack training\My Projects\CC Project"
```

### Step 2: Activate the Virtual Environment
```powershell
.venv\Scripts\Activate.ps1
```
*(You will see `(.venv)` at the beginning of your command line prompt).*

### Step 3: Run the Test Suite (Optional Quick Check)
```powershell
pytest -v tests/
```
*(Takes ~1 second and displays 95 passed tests).*

### Step 4: Start the Server
```powershell
python run.py
```
*(Server will listen at `http://127.0.0.1:5000`).*

### Step 5: Launch the Browser
Open:
```text
http://127.0.0.1:5000
```

---

## 3. The 5-Minute Demonstration Sequence

Follow this step-by-step walkthrough to present the simulator smoothly to examiners or faculty:

```
[0:00 - 0:45] Intro & Dashboard Tour
      │
[0:45 - 1:45] Run Single Algorithm (First Fit & Best Fit)
      │
[1:45 - 2:30] Run Round Robin & Explain Load Balancing
      │
[2:30 - 3:30] Run "Compare All Algorithms" Benchmark
      │
[3:30 - 4:30] Demonstrate Overload & Admission Control
      │
[4:30 - 5:00] Conclusion & Wrap-up
```

---

### Phase 1: Dashboard Overview (0:00 - 0:45)
1. **Show the Header**: Point to the status badge in the top right corner:
   - *"The green badge indicates that our Flask REST API is live and healthy."*
2. **Point to the KPI Cards**:
   - *"At the top, we have 6 overview cards: Physical Hosts, Requested VMs, Allocated VMs, Failed Allocations, Cluster CPU Utilization, and Cluster RAM Utilization."*
   - *"Notice they currently display standby states (`--`) because no simulation has run yet."*
3. **Show the Configured Cluster**:
   - *"On initial load, the system has loaded our default Balanced preset: 3 physical hosts totaling 32 CPU cores and 64 GB of RAM, and a queue of 6 virtual machine requests."*

---

### Phase 2: First Fit vs. Best Fit (0:45 - 1:45)
1. **Click the 'First Fit' Button**:
   - Observe the active badge update to `Active: First Fit`.
   - Point out that **Allocated VMs** is `6` (100% success rate).
   - Point out **Cluster CPU Util** (50%) and **Cluster RAM Util** (56.25%).
   - Scroll down to the **Physical Host Server Racks State**:
     - *"Notice how First Fit packed VMs sequentially into Host 1 (Node Alpha) and Host 2 first, while Host 3 only received spillover."*
2. **Click the 'Best Fit' Button**:
   - Observe the active badge update to `Active: Best Fit`.
   - Explain the residual scoring formula:
     $$\text{score} = \left(\frac{\text{remaining\_cpu}}{\text{total\_cpu}}\right) + \left(\frac{\text{remaining\_ram}}{\text{total\_ram}}\right)$$
   - *"Best Fit evaluated all candidate hosts for each VM and chose the machine that minimized residual capacity, resulting in tighter packing."*

---

### Phase 3: Round Robin Load Balancing (1:45 - 2:30)
1. **Click the 'Round Robin' Button**:
   - Observe the active badge update to `Active: Round Robin`.
   - Point to the **Host Server Racks State**:
     - *"Notice how Round Robin balanced the load evenly across all three hosts rather than packing the first host. Every host now shares the active compute burden."*
   - Point to the **Per-Host Resource Utilization (%)** bar chart:
     - Show that CPU and RAM bars across the 3 nodes are more evenly balanced compared to First Fit.

---

### Phase 4: Compare All Algorithms Benchmark (2:30 - 3:30)
1. **Click the 'Compare All Algorithms' Button**:
   - Notice the loading indicator for a split second as the backend executes all three algorithms against identical cloned copies of the workload.
2. **Explain the Benchmark Comparison Table**:
   - Point out the side-by-side comparison table:
     - **Success Rate** for all 3 algorithms.
     - **Allocated / Total VMs**.
     - **CPU Utilization (%)**.
     - **RAM Utilization (%)**.
     - **Remaining Cores and RAM**.
3. **Explain the Grouped Bar Chart (Chart B)**:
   - Point to the **Benchmark: All 3 Algorithms** chart:
     - Blue bars: CPU utilization across FF, BF, and RR.
     - Amber bars: RAM utilization.
     - Green bars: Success rate (100% in this balanced scenario).

---

### Phase 5: Overloaded Cluster & Failure Handling (3:30 - 4:30)
1. **Click the 'Overloaded' Preset Button**:
   - Point out the custom confirmation dialog:
     - *"Notice our in-app modal confirmation preventing accidental loss of custom cluster configurations."*
   - Click **Replace & Load**.
   - Show that the cluster now only has **2 small hosts** (8 cores, 16 GB RAM total), while the workload requests **25 cores and 50 GB RAM**.
2. **Click 'Compare All Algorithms'**:
   - Point to the KPI card: **Failed Allocations** now shows `3`, and **Success Rate** is `40%`.
   - Scroll to the **VM Allocation Placements Table**:
     - Filter by **Rejected Only** using the dropdown.
     - Highlight the red `REJECTED` badges.
     - Read the explicit failure reason for `vm-huge-monolith`:
       - *"Notice the reason: 'Insufficient CPU or RAM across all 2 hosts for Best Fit. Requested: (CPU: 12.0, RAM: 24.0 GB)'. The system strictly prevents over-allocation and logs precise reasons."*
3. **Point to the Allocation Outcomes Doughnut Chart (Chart D)**:
   - Green segment shows the 2 accommodated VMs; red segment shows the 3 rejected VMs.

---

### Phase 6: Conclusion (4:30 - 5:00)
- *"To conclude, our simulator effectively models multi-dimensional bin packing in the cloud, proves the trade-offs between packing density and load balancing, enforces strict admission control, and visualizes everything through a modern, responsive web dashboard."*
- *"Thank you. I am now ready for questions."*

---

## 4. Key Charts & Metrics to Highlight During Viva

1. **Per-Host Resource Utilization (%) (Chart A)**:
   - Highlights node heterogeneity. Shows whether a specific server is running out of memory while having idle CPU cores (stranded resources).
2. **Algorithm Performance Comparison (Chart B)**:
   - Compares the three algorithms side-by-side on identical workloads. Essential for explaining why one heuristic outperforms another under different workload patterns.
3. **Total Cluster Allocation (Chart C)**:
   - Stacked bar chart showing Allocated vs. Remaining CPU cores and RAM in GB.
4. **Allocation Outcomes (Chart D)**:
   - Doughnut chart showing the percentage of successful vs. rejected VMs.

---

## 5. Troubleshooting Common Startup Issues

### Problem 1: `Activate.ps1 cannot be loaded because running scripts is disabled`
- **Cause:** Windows PowerShell script execution policy is restricted by default.
- **Fix:** In PowerShell, run:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  .venv\Scripts\Activate.ps1
  ```

### Problem 2: `Address already in use (Port 5000)`
- **Cause:** Another process or previous server instance is using port 5000.
- **Fix:**
  In PowerShell, find and kill the process occupying port 5000:
  ```powershell
  Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess | Stop-Process -Force
  python run.py
  ```
  Or change the port in `run.py` to `5001`.

### Problem 3: Status Badge shows "API Offline"
- **Cause:** Flask development server has stopped or was not started.
- **Fix:** Ensure `python run.py` is actively running in a terminal window.

### Problem 4: Charts are blank or not rendering
- **Cause:** Device has no internet connection to download the Chart.js script from `cdn.jsdelivr.net`.
- **Fix:** Ensure the machine is connected to Wi-Fi/Ethernet.
