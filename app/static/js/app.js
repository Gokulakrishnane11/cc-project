/**
 * VM Resource Allocation Simulator - Main Application Controller
 * Handles UI interactions, state management, form submissions, presets,
 * and orchestrates ApiClient calls with ChartManager visualizations.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Application State
    const state = {
        hosts: [],
        vms: [],
        lastSimulationResult: null,
        lastComparisonResult: null,
        activeMode: 'standby', // 'standby' | 'single' | 'compare'
        isLoading: false,
    };

    // Predefined Workload Presets
    const PRESETS = {
        balanced: {
            name: 'Balanced Workload',
            hosts: [
                { host_id: 'host-1', name: 'Rack 1 - Node Alpha', total_cpu: 8, total_ram: 16 },
                { host_id: 'host-2', name: 'Rack 1 - Node Beta', total_cpu: 8, total_ram: 16 },
                { host_id: 'host-3', name: 'Rack 2 - High Compute', total_cpu: 16, total_ram: 32 },
            ],
            vms: [
                { vm_id: 'vm-web-1', cpu_required: 2, ram_required: 4 },
                { vm_id: 'vm-web-2', cpu_required: 2, ram_required: 4 },
                { vm_id: 'vm-app-1', cpu_required: 4, ram_required: 8 },
                { vm_id: 'vm-db-1', cpu_required: 4, ram_required: 12 },
                { vm_id: 'vm-cache-1', cpu_required: 2, ram_required: 4 },
                { vm_id: 'vm-worker-1', cpu_required: 4, ram_required: 8 },
            ]
        },
        cpu: {
            name: 'CPU-Heavy Compute Workload',
            hosts: [
                { host_id: 'host-cpu-1', name: 'Compute Node A', total_cpu: 16, total_ram: 16 },
                { host_id: 'host-cpu-2', name: 'Compute Node B', total_cpu: 16, total_ram: 16 },
                { host_id: 'host-cpu-3', name: 'Compute Node C', total_cpu: 8, total_ram: 8 },
            ],
            vms: [
                { vm_id: 'vm-render-1', cpu_required: 8, ram_required: 4 },
                { vm_id: 'vm-render-2', cpu_required: 8, ram_required: 4 },
                { vm_id: 'vm-ai-train-1', cpu_required: 8, ram_required: 4 },
                { vm_id: 'vm-ai-train-2', cpu_required: 8, ram_required: 4 },
                { vm_id: 'vm-analytics-1', cpu_required: 4, ram_required: 2 },
            ]
        },
        ram: {
            name: 'RAM-Heavy Caching Workload',
            hosts: [
                { host_id: 'host-mem-1', name: 'Memory Node Alpha', total_cpu: 8, total_ram: 32 },
                { host_id: 'host-mem-2', name: 'Memory Node Beta', total_cpu: 8, total_ram: 32 },
                { host_id: 'host-mem-3', name: 'Memory Node Gamma', total_cpu: 4, total_ram: 16 },
            ],
            vms: [
                { vm_id: 'vm-redis-cluster-1', cpu_required: 2, ram_required: 16 },
                { vm_id: 'vm-redis-cluster-2', cpu_required: 2, ram_required: 16 },
                { vm_id: 'vm-inmem-db-1', cpu_required: 2, ram_required: 16 },
                { vm_id: 'vm-inmem-db-2', cpu_required: 2, ram_required: 16 },
            ]
        },
        overloaded: {
            name: 'Overloaded Cluster (Allocation Failures Expected)',
            hosts: [
                { host_id: 'host-micro-1', name: 'Edge Host Alpha', total_cpu: 4, total_ram: 8 },
                { host_id: 'host-micro-2', name: 'Edge Host Beta', total_cpu: 4, total_ram: 8 },
            ],
            vms: [
                { vm_id: 'vm-heavy-1', cpu_required: 4, ram_required: 8 },
                { vm_id: 'vm-heavy-2', cpu_required: 4, ram_required: 8 },
                { vm_id: 'vm-overflow-3', cpu_required: 4, ram_required: 8 }, // Expected to fail
                { vm_id: 'vm-huge-monolith', cpu_required: 12, ram_required: 24 }, // Expected to fail
                { vm_id: 'vm-micro-service', cpu_required: 1, ram_required: 2 }, // Expected to fail
            ]
        }
    };

    // DOM Elements
    const elements = {
        apiBadge: document.getElementById('api-status-badge'),
        apiText: document.getElementById('api-status-text'),
        alertContainer: document.getElementById('alert-container'),

        // KPIs
        kpiHosts: document.getElementById('kpi-total-hosts'),
        kpiHostsSub: document.getElementById('kpi-hosts-sub'),
        kpiVms: document.getElementById('kpi-total-vms'),
        kpiVmsSub: document.getElementById('kpi-vms-sub'),
        kpiAllocated: document.getElementById('kpi-allocated-vms'),
        kpiSuccessRate: document.getElementById('kpi-success-rate'),
        kpiFailed: document.getElementById('kpi-failed-vms'),
        kpiFailedSub: document.getElementById('kpi-failed-sub'),
        kpiCpuUtil: document.getElementById('kpi-cpu-util'),
        kpiCpuBar: document.getElementById('kpi-cpu-bar'),
        kpiCpuDetails: document.getElementById('kpi-cpu-details'),
        kpiRamUtil: document.getElementById('kpi-ram-util'),
        kpiRamBar: document.getElementById('kpi-ram-bar'),
        kpiRamDetails: document.getElementById('kpi-ram-details'),

        // Forms & Tables
        formAddHost: document.getElementById('form-add-host'),
        hostIdInput: document.getElementById('host-id-input'),
        hostNameInput: document.getElementById('host-name-input'),
        hostCpuInput: document.getElementById('host-cpu-input'),
        hostRamInput: document.getElementById('host-ram-input'),
        hostsTbody: document.getElementById('hosts-tbody'),
        hostCountBadge: document.getElementById('host-count-badge'),

        formAddVm: document.getElementById('form-add-vm'),
        vmIdInput: document.getElementById('vm-id-input'),
        vmCpuInput: document.getElementById('vm-cpu-input'),
        vmRamInput: document.getElementById('vm-ram-input'),
        vmsTbody: document.getElementById('vms-tbody'),
        vmCountBadge: document.getElementById('vm-count-badge'),

        // Controls
        btnRunFf: document.getElementById('btn-run-ff'),
        btnRunBf: document.getElementById('btn-run-bf'),
        btnRunRr: document.getElementById('btn-run-rr'),
        btnRunCompare: document.getElementById('btn-run-compare'),
        btnQuickReset: document.getElementById('btn-quick-reset'),
        simActiveBadge: document.getElementById('sim-active-badge'),
        loadingOverlay: document.getElementById('loading-overlay'),
        loadingMsg: document.getElementById('loading-msg'),

        // Comparison & Results
        comparisonPanel: document.getElementById('comparison-summary-panel'),
        comparisonTbody: document.getElementById('comparison-tbody'),
        chartBenchmarkTitle: document.getElementById('chart-benchmark-title'),
        hostRacksGrid: document.getElementById('host-racks-grid'),
        racksStateBadge: document.getElementById('racks-state-badge'),
        resultsTbody: document.getElementById('results-tbody'),
        filterVmStatus: document.getElementById('filter-vm-status'),
    };

    // =========================================================================
    // UI Helpers & Alerts
    // =========================================================================

    function showAlert(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `alert-toast ${type}`;
        toast.innerHTML = `
            <div style="flex: 1;">${escapeHtml(message)}</div>
            <button class="alert-close" aria-label="Close notification">&times;</button>
        `;

        toast.querySelector('.alert-close').addEventListener('click', () => {
            toast.remove();
        });

        elements.alertContainer.appendChild(toast);
        setTimeout(() => {
            if (toast.parentElement) toast.remove();
        }, 4500);
    }

    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function setLoading(isLoading, message = 'Executing simulation...') {
        state.isLoading = isLoading;
        if (isLoading) {
            elements.loadingMsg.textContent = message;
            elements.loadingOverlay.classList.remove('hidden');
            elements.btnRunFf.disabled = true;
            elements.btnRunBf.disabled = true;
            elements.btnRunRr.disabled = true;
            elements.btnRunCompare.disabled = true;
        } else {
            elements.loadingOverlay.classList.add('hidden');
            elements.btnRunFf.disabled = false;
            elements.btnRunBf.disabled = false;
            elements.btnRunRr.disabled = false;
            elements.btnRunCompare.disabled = false;
        }
    }

    // =========================================================================
    // Initial Setup & Health Check
    // =========================================================================

    async function checkApiHealth() {
        try {
            const data = await ApiClient.getHealth();
            elements.apiBadge.className = 'status-badge online';
            elements.apiText.textContent = 'API Online';
        } catch (error) {
            elements.apiBadge.className = 'status-badge offline';
            elements.apiText.textContent = 'API Offline';
            showAlert('Backend REST API is not reachable. Ensure `python run.py` is running.', 'error');
        }
    }

    // =========================================================================
    // State & Table Rendering
    // =========================================================================

    function renderHostsTable() {
        elements.hostsTbody.innerHTML = '';
        elements.hostCountBadge.textContent = `${state.hosts.length} Host${state.hosts.length === 1 ? '' : 's'}`;

        if (state.hosts.length === 0) {
            elements.hostsTbody.innerHTML = `
                <tr>
                    <td colspan="4" class="empty-table-msg">No physical hosts added yet. Add hosts or load a preset above.</td>
                </tr>
            `;
            updateInitialKpis();
            return;
        }

        state.hosts.forEach((host, index) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>
                    <strong>${escapeHtml(host.name || host.host_id)}</strong>
                    <div style="font-size: 0.72rem; color: var(--text-muted); font-family: var(--font-mono);">${escapeHtml(host.host_id)}</div>
                </td>
                <td><span style="font-family: var(--font-mono);">${host.total_cpu}</span> cores</td>
                <td><span style="font-family: var(--font-mono);">${host.total_ram}</span> GB</td>
                <td>
                    <button class="btn-danger-outline" data-host-index="${index}" title="Remove this host">
                        Remove
                    </button>
                </td>
            `;
            elements.hostsTbody.appendChild(tr);
        });

        // Attach remove handlers
        elements.hostsTbody.querySelectorAll('[data-host-index]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const idx = parseInt(e.target.dataset.hostIndex, 10);
                const removed = state.hosts.splice(idx, 1)[0];
                renderHostsTable();
                resetSimulationView();
                showAlert(`Removed host '${removed.host_id}'.`, 'info');
            });
        });

        updateInitialKpis();
    }

    function renderVmsTable() {
        elements.vmsTbody.innerHTML = '';
        elements.vmCountBadge.textContent = `${state.vms.length} VM${state.vms.length === 1 ? '' : 's'}`;

        if (state.vms.length === 0) {
            elements.vmsTbody.innerHTML = `
                <tr>
                    <td colspan="4" class="empty-table-msg">No VM requests in queue.</td>
                </tr>
            `;
            updateInitialKpis();
            return;
        }

        state.vms.forEach((vm, index) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><code style="color: var(--accent-cyan);">${escapeHtml(vm.vm_id)}</code></td>
                <td><span style="font-family: var(--font-mono);">${vm.cpu_required}</span> cores</td>
                <td><span style="font-family: var(--font-mono);">${vm.ram_required}</span> GB</td>
                <td>
                    <button class="btn-danger-outline" data-vm-index="${index}" title="Remove this VM">
                        Remove
                    </button>
                </td>
            `;
            elements.vmsTbody.appendChild(tr);
        });

        elements.vmsTbody.querySelectorAll('[data-vm-index]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const idx = parseInt(e.target.dataset.vmIndex, 10);
                const removed = state.vms.splice(idx, 1)[0];
                renderVmsTable();
                resetSimulationView();
                showAlert(`Removed VM '${removed.vm_id}'.`, 'info');
            });
        });

        updateInitialKpis();
    }

    function updateInitialKpis() {
        const totalCpu = state.hosts.reduce((sum, h) => sum + Number(h.total_cpu), 0);
        const totalRam = state.hosts.reduce((sum, h) => sum + Number(h.total_ram), 0);

        elements.kpiHosts.textContent = state.hosts.length;
        elements.kpiHostsSub.textContent = `${totalCpu} Cores • ${totalRam} GB RAM`;

        elements.kpiVms.textContent = state.vms.length;
        elements.kpiVmsSub.textContent = `${state.vms.length} Pending Workload`;

        if (state.activeMode === 'standby') {
            elements.kpiAllocated.textContent = '--';
            elements.kpiSuccessRate.textContent = 'Success Rate: --%';
            elements.kpiFailed.textContent = '--';
            elements.kpiCpuUtil.textContent = '--%';
            elements.kpiCpuBar.style.width = '0%';
            elements.kpiCpuDetails.textContent = `Allocated: 0 / ${totalCpu} Cores`;
            elements.kpiRamUtil.textContent = '--%';
            elements.kpiRamBar.style.width = '0%';
            elements.kpiRamDetails.textContent = `Allocated: 0 / ${totalRam} GB`;
        }
    }

    function updateSimulationKpis(metrics) {
        if (!metrics) return;

        elements.kpiAllocated.textContent = metrics.successful_allocations;
        elements.kpiSuccessRate.textContent = `Success Rate: ${metrics.allocation_success_rate}%`;

        elements.kpiFailed.textContent = metrics.failed_allocations;
        elements.kpiFailedSub.textContent = metrics.failed_allocations > 0
            ? `${metrics.failed_allocations} VM${metrics.failed_allocations === 1 ? '' : 's'} could not fit`
            : '100% capacity accommodated';

        elements.kpiCpuUtil.textContent = `${metrics.cpu_utilization}%`;
        elements.kpiCpuBar.style.width = `${Math.min(100, metrics.cpu_utilization)}%`;
        elements.kpiCpuDetails.textContent = `Allocated: ${metrics.allocated_cpu} / ${metrics.total_cpu_capacity} Cores`;

        elements.kpiRamUtil.textContent = `${metrics.ram_utilization}%`;
        elements.kpiRamBar.style.width = `${Math.min(100, metrics.ram_utilization)}%`;
        elements.kpiRamDetails.textContent = `Allocated: ${metrics.allocated_ram} / ${metrics.total_ram_capacity} GB`;
    }

    // =========================================================================
    // Server Racks Visualizer
    // =========================================================================

    function renderHostRacks(hosts = []) {
        elements.hostRacksGrid.innerHTML = '';

        if (!hosts || hosts.length === 0) {
            elements.hostRacksGrid.innerHTML = `
                <div class="empty-state-box">No hosts available to display.</div>
            `;
            elements.racksStateBadge.textContent = 'No Hosts';
            return;
        }

        elements.racksStateBadge.textContent = 'Allocated State';

        hosts.forEach(host => {
            const card = document.createElement('div');
            card.className = 'rack-card';

            const cpuUtil = Math.min(100, host.cpu_utilization);
            const ramUtil = Math.min(100, host.ram_utilization);

            // Render hosted VM pills
            let vmsHtml = '<div class="rack-vms-label">Hosted Virtual Machines:</div>';
            if (host.allocated_vms && host.allocated_vms.length > 0) {
                host.allocated_vms.forEach(vm => {
                    vmsHtml += `
                        <span class="vm-tag" title="CPU: ${vm.cpu_required} cores, RAM: ${vm.ram_required} GB">
                            ${escapeHtml(vm.vm_id)} (${vm.cpu_required}C/${vm.ram_required}G)
                        </span>
                    `;
                });
            } else {
                vmsHtml += '<span style="font-size: 0.75rem; color: var(--text-muted); font-style: italic;">No active VMs hosted</span>';
            }

            card.innerHTML = `
                <div class="rack-header">
                    <div>
                        <div class="rack-title">${escapeHtml(host.name || host.host_id)}</div>
                        <div class="rack-sub">${escapeHtml(host.host_id)}</div>
                    </div>
                    <span class="badge ${host.allocated_vms && host.allocated_vms.length > 0 ? 'badge-allocated' : 'badge-pending'}">
                        ${host.allocated_vms ? host.allocated_vms.length : 0} VMs
                    </span>
                </div>

                <div class="rack-bars">
                    <div class="rack-bar-row">
                        <div class="rack-bar-label">
                            <span>CPU: ${host.allocated_cpu} / ${host.total_cpu} Cores</span>
                            <span class="util-val" style="color: var(--accent-cyan);">${cpuUtil}%</span>
                        </div>
                        <div class="progress-bar-bg">
                            <div class="progress-bar-fill fill-cyan" style="width: ${cpuUtil}%;"></div>
                        </div>
                    </div>

                    <div class="rack-bar-row">
                        <div class="rack-bar-label">
                            <span>RAM: ${host.allocated_ram} / ${host.total_ram} GB</span>
                            <span class="util-val" style="color: var(--accent-amber);">${ramUtil}%</span>
                        </div>
                        <div class="progress-bar-bg">
                            <div class="progress-bar-fill fill-amber" style="width: ${ramUtil}%;"></div>
                        </div>
                    </div>
                </div>

                <div class="rack-vms-list">
                    ${vmsHtml}
                </div>
            `;

            elements.hostRacksGrid.appendChild(card);
        });
    }

    // =========================================================================
    // VM Allocation Placements Table
    // =========================================================================

    function renderVmResultsTable(vms = []) {
        elements.resultsTbody.innerHTML = '';

        if (!vms || vms.length === 0) {
            elements.resultsTbody.innerHTML = `
                <tr>
                    <td colspan="6" class="empty-table-msg">No allocation records to display.</td>
                </tr>
            `;
            return;
        }

        const filter = elements.filterVmStatus.value;
        const filteredVms = vms.filter(vm => {
            if (filter === 'allocated') return vm.status === 'ALLOCATED';
            if (filter === 'rejected') return vm.status === 'REJECTED';
            return true;
        });

        if (filteredVms.length === 0) {
            elements.resultsTbody.innerHTML = `
                <tr>
                    <td colspan="6" class="empty-table-msg">No VMs match the selected filter (${filter}).</td>
                </tr>
            `;
            return;
        }

        filteredVms.forEach(vm => {
            const tr = document.createElement('tr');
            const isAllocated = vm.status === 'ALLOCATED';

            const statusBadge = isAllocated
                ? '<span class="badge badge-allocated">ALLOCATED</span>'
                : '<span class="badge badge-rejected">REJECTED</span>';

            const hostDisplay = isAllocated
                ? `<code style="color: #60a5fa; font-weight: 600;">${escapeHtml(vm.allocated_host_id)}</code>`
                : '<span style="color: var(--text-muted);">&mdash;</span>';

            const detailMsg = isAllocated
                ? '<span style="color: #34d399;">Successfully placed on host</span>'
                : `<span style="color: #fb7185;">${escapeHtml(vm.failure_reason || 'Insufficient host capacity')}</span>`;

            tr.innerHTML = `
                <td><code>${escapeHtml(vm.vm_id)}</code></td>
                <td><span style="font-family: var(--font-mono);">${vm.cpu_required}</span> cores</td>
                <td><span style="font-family: var(--font-mono);">${vm.ram_required}</span> GB</td>
                <td>${statusBadge}</td>
                <td>${hostDisplay}</td>
                <td>${detailMsg}</td>
            `;

            elements.resultsTbody.appendChild(tr);
        });
    }

    // =========================================================================
    // Comparison Table
    // =========================================================================

    function renderComparisonTable(summaryRows = []) {
        elements.comparisonTbody.innerHTML = '';
        if (!summaryRows || summaryRows.length === 0) return;

        summaryRows.forEach(row => {
            const tr = document.createElement('tr');
            const totalVms = (row.successful_allocations + row.failed_allocations);

            tr.innerHTML = `
                <td><strong>${escapeHtml(row.algorithm_name)}</strong></td>
                <td>
                    <span class="badge ${row.allocation_success_rate === 100 ? 'badge-allocated' : row.allocation_success_rate > 0 ? 'badge-pending' : 'badge-rejected'}">
                        ${row.allocation_success_rate}%
                    </span>
                </td>
                <td>
                    <span style="font-family: var(--font-mono);">${row.successful_allocations} / ${totalVms}</span>
                    <span style="font-size: 0.72rem; color: var(--text-muted);"> (${row.failed_allocations} failed)</span>
                </td>
                <td><span style="font-family: var(--font-mono); color: var(--accent-cyan);">${row.cpu_utilization}%</span> (${row.allocated_cpu}/${row.total_cpu_capacity} cores)</td>
                <td><span style="font-family: var(--font-mono); color: var(--accent-amber);">${row.ram_utilization}%</span> (${row.allocated_ram}/${row.total_ram_capacity} GB)</td>
                <td style="font-family: var(--font-mono); font-size: 0.78rem;">
                    ${row.remaining_cpu} Cores • ${row.remaining_ram} GB
                </td>
            `;
            elements.comparisonTbody.appendChild(tr);
        });
    }

    // =========================================================================
    // Reset View
    // =========================================================================

    function resetSimulationView() {
        state.lastSimulationResult = null;
        state.lastComparisonResult = null;
        state.activeMode = 'standby';

        elements.simActiveBadge.className = 'mode-badge standby';
        elements.simActiveBadge.textContent = 'Standby';

        elements.comparisonPanel.classList.add('hidden');
        elements.chartBenchmarkTitle.textContent = 'Algorithm Performance Comparison';

        elements.hostRacksGrid.innerHTML = `
            <div class="empty-state-box">Run an allocation simulation to inspect server rack utilization.</div>
        `;
        elements.racksStateBadge.textContent = 'Unallocated';

        elements.resultsTbody.innerHTML = `
            <tr>
                <td colspan="6" class="empty-table-msg">Run an algorithm to view VM placement details.</td>
            </tr>
        `;

        ChartManager.destroyAll();
        updateInitialKpis();
    }

    // =========================================================================
    // Simulation Runners
    // =========================================================================

    async function executeSingleSimulation(algorithmKey, displayName) {
        if (state.hosts.length === 0) {
            showAlert('Please configure at least one physical host before running allocation.', 'error');
            return;
        }
        if (state.vms.length === 0) {
            showAlert('Please configure at least one VM request in the queue.', 'error');
            return;
        }

        setLoading(true, `Executing ${displayName} allocation simulation...`);

        try {
            const result = await ApiClient.runSimulate(algorithmKey, state.hosts, state.vms);
            state.lastSimulationResult = result;
            state.lastComparisonResult = null;
            state.activeMode = 'single';

            // Update UI State
            elements.simActiveBadge.className = 'mode-badge active';
            elements.simActiveBadge.textContent = `Active: ${result.algorithm_name}`;
            elements.chartBenchmarkTitle.textContent = `${result.algorithm_name} Performance`;
            elements.comparisonPanel.classList.add('hidden');

            // Render KPIs, Racks, Table, and Charts
            updateSimulationKpis(result.metrics);
            renderHostRacks(result.hosts);
            renderVmResultsTable(result.vms);

            ChartManager.renderHostUtilizationChart(result.hosts);
            ChartManager.renderSingleAlgorithmPerformanceChart(result);
            ChartManager.renderResourceCapacityChart(result.metrics);
            ChartManager.renderOutcomesChart(result.metrics);

            showAlert(`Completed ${result.algorithm_name} simulation. Success Rate: ${result.metrics.allocation_success_rate}%.`, 'success');
        } catch (error) {
            showAlert(error.message || 'Simulation request failed.', 'error');
        } finally {
            setLoading(false);
        }
    }

    async function executeComparison() {
        if (state.hosts.length === 0) {
            showAlert('Please configure at least one physical host before running comparison.', 'error');
            return;
        }
        if (state.vms.length === 0) {
            showAlert('Please configure at least one VM request in the queue.', 'error');
            return;
        }

        setLoading(true, 'Running all 3 algorithms across identical cluster workload...');

        try {
            const comparison = await ApiClient.runCompare(state.hosts, state.vms);
            state.lastComparisonResult = comparison;
            state.lastSimulationResult = null;
            state.activeMode = 'compare';

            elements.simActiveBadge.className = 'mode-badge active';
            elements.simActiveBadge.textContent = 'Active: Benchmark Comparison';
            elements.chartBenchmarkTitle.textContent = 'Benchmark: All 3 Algorithms';
            elements.comparisonPanel.classList.remove('hidden');

            renderComparisonTable(comparison.summary);

            // Display Best Fit host placements as primary visual reference
            const referenceAlgo = comparison.algorithms.best_fit || comparison.algorithms.first_fit;
            if (referenceAlgo) {
                updateSimulationKpis(referenceAlgo.metrics);
                renderHostRacks(referenceAlgo.hosts);
                renderVmResultsTable(referenceAlgo.vms);

                ChartManager.renderHostUtilizationChart(referenceAlgo.hosts);
                ChartManager.renderComparisonBenchmarkChart(comparison.summary);
                ChartManager.renderResourceCapacityChart(referenceAlgo.metrics);
                ChartManager.renderOutcomesChart(referenceAlgo.metrics);
            }

            showAlert('Fair comparison benchmark completed across First Fit, Best Fit, and Round Robin.', 'success');
        } catch (error) {
            showAlert(error.message || 'Comparison request failed.', 'error');
        } finally {
            setLoading(false);
        }
    }

    // =========================================================================
    // Event Listeners
    // =========================================================================

    // Add Physical Host Form
    elements.formAddHost.addEventListener('submit', (e) => {
        e.preventDefault();
        const hostId = elements.hostIdInput.value.trim();
        const hostName = elements.hostNameInput.value.trim() || hostId;
        const totalCpu = parseFloat(elements.hostCpuInput.value);
        const totalRam = parseFloat(elements.hostRamInput.value);

        if (!hostId) {
            showAlert('Host ID cannot be empty.', 'error');
            return;
        }

        if (state.hosts.some(h => h.host_id.toLowerCase() === hostId.toLowerCase())) {
            showAlert(`A host with ID '${hostId}' already exists. Host IDs must be unique.`, 'error');
            return;
        }

        if (isNaN(totalCpu) || totalCpu <= 0) {
            showAlert('CPU cores must be a positive number greater than 0.', 'error');
            return;
        }

        if (isNaN(totalRam) || totalRam <= 0) {
            showAlert('RAM must be a positive number greater than 0.', 'error');
            return;
        }

        state.hosts.push({
            host_id: hostId,
            name: hostName,
            total_cpu: totalCpu,
            total_ram: totalRam,
        });

        elements.formAddHost.reset();
        renderHostsTable();
        resetSimulationView();
        showAlert(`Added physical host '${hostId}' (${totalCpu} cores, ${totalRam} GB RAM).`, 'success');
    });

    // Add VM Request Form
    elements.formAddVm.addEventListener('submit', (e) => {
        e.preventDefault();
        const vmId = elements.vmIdInput.value.trim();
        const cpuReq = parseFloat(elements.vmCpuInput.value);
        const ramReq = parseFloat(elements.vmRamInput.value);

        if (!vmId) {
            showAlert('VM ID cannot be empty.', 'error');
            return;
        }

        if (state.vms.some(v => v.vm_id.toLowerCase() === vmId.toLowerCase())) {
            showAlert(`A VM request with ID '${vmId}' already exists. VM IDs must be unique.`, 'error');
            return;
        }

        if (isNaN(cpuReq) || cpuReq <= 0) {
            showAlert('Required CPU must be a positive number greater than 0.', 'error');
            return;
        }

        if (isNaN(ramReq) || ramReq <= 0) {
            showAlert('Required RAM must be a positive number greater than 0.', 'error');
            return;
        }

        state.vms.push({
            vm_id: vmId,
            cpu_required: cpuReq,
            ram_required: ramReq,
        });

        elements.formAddVm.reset();
        renderVmsTable();
        resetSimulationView();
        showAlert(`Added VM request '${vmId}' (${cpuReq} cores, ${ramReq} GB RAM).`, 'success');
    });

    // Preset loading and confirmation modal
    let pendingPreset = null;

    function applyPreset(preset) {
        state.hosts = JSON.parse(JSON.stringify(preset.hosts));
        state.vms = JSON.parse(JSON.stringify(preset.vms));

        renderHostsTable();
        renderVmsTable();
        resetSimulationView();
        showAlert(`Loaded preset: ${preset.name} (${state.hosts.length} hosts, ${state.vms.length} VMs).`, 'info');
    }

    document.querySelectorAll('.btn-preset').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const presetKey = e.currentTarget.id.replace('preset-', '');
            const preset = PRESETS[presetKey];
            if (!preset) return;

            if (state.hosts.length > 0 || state.vms.length > 0) {
                pendingPreset = preset;
                const msg = document.getElementById('confirm-modal-msg');
                if (msg) {
                    msg.textContent = `Loading '${preset.name}' will replace your currently configured ${state.hosts.length} host(s) and ${state.vms.length} VM(s).`;
                }
                const modal = document.getElementById('confirm-modal');
                if (modal) modal.classList.remove('hidden');
                return;
            }

            applyPreset(preset);
        });
    });

    const modalCancel = document.getElementById('btn-modal-cancel');
    if (modalCancel) {
        modalCancel.addEventListener('click', () => {
            const modal = document.getElementById('confirm-modal');
            if (modal) modal.classList.add('hidden');
            pendingPreset = null;
        });
    }

    const modalConfirm = document.getElementById('btn-modal-confirm');
    if (modalConfirm) {
        modalConfirm.addEventListener('click', () => {
            const modal = document.getElementById('confirm-modal');
            if (modal) modal.classList.add('hidden');
            if (pendingPreset) {
                applyPreset(pendingPreset);
                pendingPreset = null;
            }
        });
    }

    // Algorithm Execution Controls
    elements.btnRunFf.addEventListener('click', () => executeSingleSimulation('first_fit', 'First Fit'));
    elements.btnRunBf.addEventListener('click', () => executeSingleSimulation('best_fit', 'Best Fit'));
    elements.btnRunRr.addEventListener('click', () => executeSingleSimulation('round_robin', 'Round Robin'));
    elements.btnRunCompare.addEventListener('click', () => executeComparison());

    // Reset button
    elements.btnQuickReset.addEventListener('click', () => {
        resetSimulationView();
        showAlert('Simulation results reset to standby state.', 'info');
    });

    // VM Filter Selector
    elements.filterVmStatus.addEventListener('change', () => {
        if (state.lastSimulationResult) {
            renderVmResultsTable(state.lastSimulationResult.vms);
        } else if (state.lastComparisonResult) {
            const ref = state.lastComparisonResult.algorithms.best_fit || state.lastComparisonResult.algorithms.first_fit;
            if (ref) renderVmResultsTable(ref.vms);
        }
    });

    // Load initial balanced preset by default for instant out-of-the-box readiness
    const defaultPreset = PRESETS.balanced;
    state.hosts = JSON.parse(JSON.stringify(defaultPreset.hosts));
    state.vms = JSON.parse(JSON.stringify(defaultPreset.vms));

    renderHostsTable();
    renderVmsTable();
    resetSimulationView();

    // Health check on startup
    checkApiHealth();
});
