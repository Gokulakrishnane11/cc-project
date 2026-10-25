/**
 * ApiClient - Handles all network interactions with the Flask REST API.
 * Uses relative paths and consistent JSON error normalization.
 */

const ApiClient = {
    /**
     * Check server health status.
     * @returns {Promise<{status: string, service: string, version: string}>}
     */
    async getHealth() {
        try {
            const response = await fetch('/api/health');
            return await this._handleResponse(response);
        } catch (error) {
            throw this._normalizeNetworkError(error);
        }
    },

    /**
     * Fetch list of available algorithms and descriptions.
     * @returns {Promise<{algorithms: Array<{id: string, name: string, description: string}>}>}
     */
    async getAlgorithms() {
        try {
            const response = await fetch('/api/algorithms');
            return await this._handleResponse(response);
        } catch (error) {
            throw this._normalizeNetworkError(error);
        }
    },

    /**
     * Run a single allocation simulation.
     * @param {string} algorithm - 'first_fit', 'best_fit', or 'round_robin'
     * @param {Array<Object>} hosts - Configured physical hosts
     * @param {Array<Object>} vms - Configured virtual machines workload
     * @returns {Promise<Object>} Simulation results
     */
    async runSimulate(algorithm, hosts, vms) {
        try {
            const response = await fetch('/api/simulate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ algorithm, hosts, vms }),
            });
            return await this._handleResponse(response);
        } catch (error) {
            throw this._normalizeNetworkError(error);
        }
    },

    /**
     * Run all three allocation algorithms and return comparison metrics.
     * @param {Array<Object>} hosts - Configured physical hosts
     * @param {Array<Object>} vms - Configured virtual machines workload
     * @returns {Promise<Object>} Side-by-side comparison results
     */
    async runCompare(hosts, vms) {
        try {
            const response = await fetch('/api/compare', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ hosts, vms }),
            });
            return await this._handleResponse(response);
        } catch (error) {
            throw this._normalizeNetworkError(error);
        }
    },

    /**
     * Helper to parse JSON response and extract structured error messages.
     * @private
     */
    async _handleResponse(response) {
        let data = null;
        try {
            data = await response.json();
        } catch (jsonErr) {
            if (!response.ok) {
                throw new Error(`Server returned HTTP ${response.status}: ${response.statusText}`);
            }
            return null;
        }

        if (!response.ok) {
            if (data && data.error && data.error.message) {
                const err = new Error(data.error.message);
                err.code = data.error.code || 'API_ERROR';
                err.status = response.status;
                throw err;
            }
            throw new Error(`HTTP Error ${response.status}: ${response.statusText}`);
        }

        return data;
    },

    /**
     * Convert low-level fetch failures into readable UI messages.
     * @private
     */
    _normalizeNetworkError(error) {
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            return new Error('Backend server is unreachable. Please ensure the Flask app is running at http://127.0.0.1:5000.');
        }
        return error;
    }
};

window.ApiClient = ApiClient;
