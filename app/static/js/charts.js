/**
 * ChartManager - Coordinates Chart.js lifecycle, configuration, and data rendering.
 * Safely destroys previous instances before rendering to prevent memory leaks and canvas overlap.
 */

const ChartManager = {
    instances: {
        hostUtil: null,
        benchmark: null,
        capacity: null,
        outcomes: null,
    },

    // Chart.js global dark theme defaults
    getDarkThemeOptions(titleText = '', yAxisUnit = '%') {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#cbd5e1',
                        font: { family: 'Inter', size: 12, weight: 500 },
                        padding: 12,
                        boxWidth: 14,
                        boxHeight: 14,
                        usePointStyle: true,
                    },
                },
                tooltip: {
                    backgroundColor: '#1e293b',
                    titleColor: '#f8fafc',
                    bodyColor: '#cbd5e1',
                    borderColor: '#334155',
                    borderWidth: 1,
                    padding: 10,
                    callbacks: {
                        label: function (context) {
                            let label = context.dataset.label || '';
                            if (label) label += ': ';
                            if (context.parsed.y !== null && context.parsed.y !== undefined) {
                                label += context.parsed.y + (yAxisUnit ? ' ' + yAxisUnit : '');
                            } else if (context.parsed !== null) {
                                label += context.parsed;
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8', font: { family: 'Inter', size: 11 } }
                },
                y: {
                    beginAtZero: true,
                    max: yAxisUnit === '%' ? 100 : undefined,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: {
                        color: '#94a3b8',
                        font: { family: 'Inter', size: 11 },
                        callback: (value) => yAxisUnit === '%' ? value + '%' : value,
                    }
                }
            }
        };
    },

    /**
     * Safely destroy a registered chart instance.
     */
    destroyChart(key) {
        if (this.instances[key]) {
            this.instances[key].destroy();
            this.instances[key] = null;
        }
    },

    /**
     * Destroy all active chart instances.
     */
    destroyAll() {
        Object.keys(this.instances).forEach(key => this.destroyChart(key));
    },

    /**
     * Render Chart A & C: Per-Host CPU and RAM Utilization (%)
     * @param {Array<Object>} hosts
     */
    renderHostUtilizationChart(hosts = []) {
        this.destroyChart('hostUtil');
        const ctx = document.getElementById('chart-host-utilization');
        if (!ctx) return;

        const labels = hosts.length > 0 ? hosts.map(h => h.name || h.host_id) : ['No Hosts'];
        const cpuData = hosts.length > 0 ? hosts.map(h => Math.min(100, h.cpu_utilization)) : [0];
        const ramData = hosts.length > 0 ? hosts.map(h => Math.min(100, h.ram_utilization)) : [0];

        this.instances.hostUtil = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    {
                        label: 'CPU Util (%)',
                        data: cpuData,
                        backgroundColor: 'rgba(6, 182, 212, 0.75)',
                        borderColor: '#06b6d4',
                        borderWidth: 1.5,
                        borderRadius: 4,
                    },
                    {
                        label: 'RAM Util (%)',
                        data: ramData,
                        backgroundColor: 'rgba(245, 158, 11, 0.75)',
                        borderColor: '#f59e0b',
                        borderWidth: 1.5,
                        borderRadius: 4,
                    }
                ]
            },
            options: this.getDarkThemeOptions('Per-Host Utilization', '%')
        });
    },

    /**
     * Render Chart B: Algorithm Comparison Benchmark (Grouped Bar Chart)
     * Compares CPU Util %, RAM Util %, and Success Rate % across First Fit, Best Fit, and Round Robin.
     * @param {Array<Object>} summaryRows
     */
    renderComparisonBenchmarkChart(summaryRows = []) {
        this.destroyChart('benchmark');
        const ctx = document.getElementById('chart-comparison');
        if (!ctx) return;

        const labels = summaryRows.map(r => r.algorithm_name);
        const successRateData = summaryRows.map(r => r.allocation_success_rate);
        const cpuUtilData = summaryRows.map(r => r.cpu_utilization);
        const ramUtilData = summaryRows.map(r => r.ram_utilization);

        this.instances.benchmark = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Success Rate (%)',
                        data: successRateData,
                        backgroundColor: 'rgba(16, 185, 129, 0.8)',
                        borderColor: '#10b981',
                        borderWidth: 1.5,
                        borderRadius: 4,
                    },
                    {
                        label: 'CPU Utilization (%)',
                        data: cpuUtilData,
                        backgroundColor: 'rgba(59, 130, 246, 0.8)',
                        borderColor: '#3b82f6',
                        borderWidth: 1.5,
                        borderRadius: 4,
                    },
                    {
                        label: 'RAM Utilization (%)',
                        data: ramUtilData,
                        backgroundColor: 'rgba(245, 158, 11, 0.8)',
                        borderColor: '#f59e0b',
                        borderWidth: 1.5,
                        borderRadius: 4,
                    }
                ]
            },
            options: this.getDarkThemeOptions('Algorithm Benchmark Comparison', '%')
        });
    },

    /**
     * Render single algorithm performance in comparison chart position when in single mode.
     */
    renderSingleAlgorithmPerformanceChart(result) {
        this.destroyChart('benchmark');
        const ctx = document.getElementById('chart-comparison');
        if (!ctx) return;

        const metrics = result.metrics || {};
        this.instances.benchmark = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Success Rate (%)', 'CPU Util (%)', 'RAM Util (%)'],
                datasets: [
                    {
                        label: result.algorithm_name || 'Current Algorithm',
                        data: [
                            metrics.allocation_success_rate || 0,
                            metrics.cpu_utilization || 0,
                            metrics.ram_utilization || 0,
                        ],
                        backgroundColor: [
                            'rgba(16, 185, 129, 0.8)',
                            'rgba(6, 182, 212, 0.8)',
                            'rgba(245, 158, 11, 0.8)',
                        ],
                        borderColor: ['#10b981', '#06b6d4', '#f59e0b'],
                        borderWidth: 1.5,
                        borderRadius: 4,
                    }
                ]
            },
            options: {
                ...this.getDarkThemeOptions('Heuristic Metrics', '%'),
                plugins: {
                    ...this.getDarkThemeOptions().plugins,
                    legend: { display: false }
                }
            }
        });
    },

    /**
     * Render Chart C: Cluster Capacity Allocation (Allocated vs Remaining CPU & RAM)
     * @param {Object} metrics
     */
    renderResourceCapacityChart(metrics = {}) {
        this.destroyChart('capacity');
        const ctx = document.getElementById('chart-resource-capacity');
        if (!ctx) return;

        const allocCpu = metrics.allocated_cpu || 0;
        const remCpu = metrics.remaining_cpu || 0;
        const allocRam = metrics.allocated_ram || 0;
        const remRam = metrics.remaining_ram || 0;

        this.instances.capacity = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['CPU Cores', 'RAM (GB)'],
                datasets: [
                    {
                        label: 'Allocated',
                        data: [allocCpu, allocRam],
                        backgroundColor: 'rgba(59, 130, 246, 0.8)',
                        borderColor: '#3b82f6',
                        borderWidth: 1.5,
                        borderRadius: 4,
                    },
                    {
                        label: 'Remaining',
                        data: [remCpu, remRam],
                        backgroundColor: 'rgba(100, 116, 139, 0.45)',
                        borderColor: '#64748b',
                        borderWidth: 1.5,
                        borderRadius: 4,
                    }
                ]
            },
            options: {
                ...this.getDarkThemeOptions('Resource Distribution', ''),
                scales: {
                    x: {
                        stacked: true,
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8' }
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8' }
                    }
                }
            }
        });
    },

    /**
     * Render Chart D: Allocation Outcomes (Successful vs Failed VMs Doughnut Chart)
     * @param {Object} metrics
     */
    renderOutcomesChart(metrics = {}) {
        this.destroyChart('outcomes');
        const ctx = document.getElementById('chart-outcomes');
        if (!ctx) return;

        const successful = metrics.successful_allocations || 0;
        const failed = metrics.failed_allocations || 0;
        const total = metrics.total_vms || 0;

        const hasData = total > 0;
        const dataValues = hasData ? [successful, failed] : [1];
        const bgColors = hasData
            ? ['rgba(16, 185, 129, 0.85)', 'rgba(244, 63, 94, 0.85)']
            : ['rgba(51, 65, 85, 0.6)'];
        const borderColors = hasData ? ['#10b981', '#f43f5e'] : ['#334155'];
        const labels = hasData ? ['Allocated VMs', 'Failed Allocations'] : ['No Workload'];

        this.instances.outcomes = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels,
                datasets: [
                    {
                        data: dataValues,
                        backgroundColor: bgColors,
                        borderColor: borderColors,
                        borderWidth: 2,
                        hoverOffset: 4,
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#cbd5e1',
                            font: { family: 'Inter', size: 11, weight: 500 },
                            boxWidth: 12,
                            boxHeight: 12,
                            padding: 10,
                        }
                    },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        borderColor: '#334155',
                        borderWidth: 1,
                        callbacks: {
                            label: function (context) {
                                if (!hasData) return 'No data';
                                const count = context.raw || 0;
                                const pct = total > 0 ? ((count / total) * 100).toFixed(1) : 0;
                                return ` ${context.label}: ${count} (${pct}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
};

window.ChartManager = ChartManager;
