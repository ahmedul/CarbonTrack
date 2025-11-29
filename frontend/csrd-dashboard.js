/**
 * CSRD Compliance Dashboard Component
 * Enterprise feature for EU CSRD compliance reporting
 */

const CSRDDashboard = {
    name: 'CSRDDashboard',
    template: `
        <div class="csrd-dashboard">
            <!-- Header -->
            <div class="dashboard-header">
                <h2><i class="fas fa-chart-bar"></i> CSRD Compliance Dashboard</h2>
                <p class="subtitle">EU Corporate Sustainability Reporting Directive (CSRD)</p>
                <button class="btn-primary" @click="showCreateModal = true">
                    <i class="fas fa-plus"></i> Create New Report
                </button>
            </div>

            <!-- Statistics Cards -->
            <div class="stats-cards">
                <div class="stat-card">
                    <div class="stat-icon blue">
                        <i class="fas fa-file-alt"></i>
                    </div>
                    <div class="stat-content">
                        <h3>{{ statistics.totalReports }}</h3>
                        <p>Total Reports</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon yellow">
                        <i class="fas fa-clock"></i>
                    </div>
                    <div class="stat-content">
                        <h3>{{ statistics.inProgress }}</h3>
                        <p>In Progress</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon green">
                        <i class="fas fa-check-circle"></i>
                    </div>
                    <div class="stat-content">
                        <h3>{{ statistics.submitted }}</h3>
                        <p>Submitted</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon purple">
                        <i class="fas fa-percentage"></i>
                    </div>
                    <div class="stat-content">
                        <h3>{{ statistics.avgCompleteness }}%</h3>
                        <p>Avg Completeness</p>
                    </div>
                </div>
            </div>

            <!-- Filters -->
            <div class="filters-section">
                <div class="filter-group">
                    <label>Year</label>
                    <select v-model="filters.year" @change="loadReports">
                        <option :value="null">All Years</option>
                        <option v-for="year in availableYears" :key="year" :value="year">
                            {{ year }}
                        </option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Status</label>
                    <select v-model="filters.status" @change="loadReports">
                        <option :value="null">All Status</option>
                        <option value="NOT_STARTED">Not Started</option>
                        <option value="IN_PROGRESS">In Progress</option>
                        <option value="REVIEW">Under Review</option>
                        <option value="COMPLETED">Completed</option>
                        <option value="SUBMITTED">Submitted</option>
                    </select>
                </div>
            </div>

            <!-- Reports List -->
            <div class="reports-list">
                <div v-if="loading" class="loading-state">
                    <i class="fas fa-spinner fa-spin"></i> Loading reports...
                </div>

                <div v-else-if="reports.length === 0" class="empty-state">
                    <i class="fas fa-folder-open"></i>
                    <h3>No Reports Found</h3>
                    <p>Create your first CSRD report to get started</p>
                    <button class="btn-primary" @click="showCreateModal = true">
                        Create Report
                    </button>
                </div>

                <div v-else class="reports-table">
                    <table>
                        <thead>
                            <tr>
                                <th>Report ID</th>
                                <th>Year</th>
                                <th>Company</th>
                                <th>Status</th>
                                <th>Completeness</th>
                                <th>Last Updated</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="report in reports" :key="report.report_id">
                                <td><code>{{ report.report_id }}</code></td>
                                <td>{{ report.reporting_year }}</td>
                                <td>{{ report.company_name }}</td>
                                <td>
                                    <span class="status-badge" :class="getStatusClass(report.status)">
                                        {{ formatStatus(report.status) }}
                                    </span>
                                </td>
                                <td>
                                    <div class="progress-bar">
                                        <div class="progress-fill" 
                                             :style="{width: report.completeness_score + '%'}"
                                             :class="getCompletenessClass(report.completeness_score)">
                                        </div>
                                        <span class="progress-text">{{ report.completeness_score }}%</span>
                                    </div>
                                </td>
                                <td>{{ formatDate(report.updated_at) }}</td>
                                <td>
                                    <button class="btn-icon" @click="viewReport(report.report_id)" title="View Details">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    <button class="btn-icon" @click="editReport(report.report_id)" title="Edit">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button class="btn-icon" @click="exportPDF(report.report_id)" title="Export PDF">
                                        <i class="fas fa-file-pdf"></i>
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Create Report Modal -->
            <div v-if="showCreateModal" class="modal-overlay" @click="showCreateModal = false">
                <div class="modal-content" @click.stop>
                    <div class="modal-header">
                        <h3>Create New CSRD Report</h3>
                        <button class="btn-close" @click="showCreateModal = false">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="modal-body">
                        <form @submit.prevent="createReport">
                            <div class="form-group">
                                <label>Company Name *</label>
                                <input v-model="newReport.company_name" type="text" required 
                                       placeholder="e.g., Acme Corporation GmbH">
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Reporting Year *</label>
                                    <input v-model.number="newReport.reporting_year" type="number" 
                                           required min="2024" max="2030" placeholder="2025">
                                </div>
                                <div class="form-group">
                                    <label>Reporting Period *</label>
                                    <select v-model="newReport.reporting_period" required>
                                        <option value="ANNUAL">Annual</option>
                                        <option value="Q1">Q1</option>
                                        <option value="Q2">Q2</option>
                                        <option value="Q3">Q3</option>
                                        <option value="Q4">Q4</option>
                                    </select>
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Country *</label>
                                    <select v-model="newReport.country" required>
                                        <option value="">Select Country</option>
                                        <option value="DE">Germany</option>
                                        <option value="FR">France</option>
                                        <option value="NL">Netherlands</option>
                                        <option value="BE">Belgium</option>
                                        <option value="AT">Austria</option>
                                        <option value="IT">Italy</option>
                                        <option value="ES">Spain</option>
                                        <option value="PL">Poland</option>
                                        <option value="SE">Sweden</option>
                                        <option value="DK">Denmark</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>Sector</label>
                                    <input v-model="newReport.sector" type="text" 
                                           placeholder="e.g., Technology">
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Employee Count *</label>
                                    <input v-model.number="newReport.employee_count" type="number" 
                                           required min="250" placeholder="250+">
                                </div>
                                <div class="form-group">
                                    <label>Annual Revenue (EUR) *</label>
                                    <input v-model.number="newReport.annual_revenue_eur" type="number" 
                                           required min="40000000" step="1000000" 
                                           placeholder="40,000,000">
                                </div>
                            </div>
                            <div class="form-actions">
                                <button type="button" class="btn-secondary" @click="showCreateModal = false">
                                    Cancel
                                </button>
                                <button type="submit" class="btn-primary" :disabled="creating">
                                    <i class="fas" :class="creating ? 'fa-spinner fa-spin' : 'fa-plus'"></i>
                                    {{ creating ? 'Creating...' : 'Create Report' }}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>

            <!-- Report Detail Modal -->
            <div v-if="selectedReport" class="modal-overlay" @click="selectedReport = null">
                <div class="modal-content modal-large" @click.stop>
                    <div class="modal-header">
                        <h3>{{ selectedReport.company_name }} - {{ selectedReport.reporting_year }}</h3>
                        <button class="btn-close" @click="selectedReport = null">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="modal-body">
                        <!-- Report details content -->
                        <div class="report-details">
                            <div class="detail-section">
                                <h4>Report Information</h4>
                                <div class="detail-grid">
                                    <div class="detail-item">
                                        <label>Report ID</label>
                                        <span><code>{{ selectedReport.report_id }}</code></span>
                                    </div>
                                    <div class="detail-item">
                                        <label>Status</label>
                                        <span class="status-badge" :class="getStatusClass(selectedReport.status)">
                                            {{ formatStatus(selectedReport.status) }}
                                        </span>
                                    </div>
                                    <div class="detail-item">
                                        <label>Completeness</label>
                                        <span>{{ selectedReport.completeness_score }}%</span>
                                    </div>
                                    <div class="detail-item">
                                        <label>Created</label>
                                        <span>{{ formatDate(selectedReport.created_at) }}</span>
                                    </div>
                                </div>
                            </div>

                            <div class="detail-section" v-if="selectedReport.emissions_scope">
                                <h4>Emissions Data (tCO2e)</h4>
                                <div class="emissions-chart">
                                    <div class="emission-item">
                                        <label>Scope 1</label>
                                        <span class="emission-value">
                                            {{ selectedReport.emissions_scope.scope_1 || 0 }}
                                        </span>
                                    </div>
                                    <div class="emission-item">
                                        <label>Scope 2</label>
                                        <span class="emission-value">
                                            {{ selectedReport.emissions_scope.scope_2 || 0 }}
                                        </span>
                                    </div>
                                    <div class="emission-item">
                                        <label>Scope 3</label>
                                        <span class="emission-value">
                                            {{ selectedReport.emissions_scope.scope_3 || 0 }}
                                        </span>
                                    </div>
                                    <div class="emission-item total">
                                        <label>Total</label>
                                        <span class="emission-value">
                                            {{ selectedReport.emissions_scope.total || 0 }}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <div class="detail-actions">
                                <button class="btn-primary" @click="editReport(selectedReport.report_id)">
                                    <i class="fas fa-edit"></i> Edit Report
                                </button>
                                <button class="btn-secondary" @click="exportPDF(selectedReport.report_id)">
                                    <i class="fas fa-file-pdf"></i> Export PDF
                                </button>
                                <button class="btn-secondary" @click="viewAuditTrail(selectedReport.report_id)">
                                    <i class="fas fa-history"></i> Audit Trail
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,
    data() {
        return {
            reports: [],
            selectedReport: null,
            loading: false,
            creating: false,
            showCreateModal: false,
            filters: {
                year: null,
                status: null
            },
            newReport: {
                company_name: '',
                reporting_year: new Date().getFullYear(),
                reporting_period: 'ANNUAL',
                country: '',
                sector: '',
                employee_count: null,
                annual_revenue_eur: null
            },
            statistics: {
                totalReports: 0,
                inProgress: 0,
                submitted: 0,
                avgCompleteness: 0
            },
            availableYears: [2024, 2025, 2026, 2027, 2028]
        };
    },
    mounted() {
        this.loadReports();
    },
    methods: {
        async loadReports() {
            this.loading = true;
            try {
                const params = new URLSearchParams();
                if (this.filters.year) params.append('year', this.filters.year);
                if (this.filters.status) params.append('status', this.filters.status);

                const response = await fetch(
                    `${this.apiBase}/api/v1/csrd/reports?${params.toString()}`,
                    {
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('token')}`
                        }
                    }
                );

                if (response.ok) {
                    const data = await response.json();
                    this.reports = data.reports || [];
                    this.calculateStatistics();
                } else if (response.status === 403) {
                    this.$emit('show-upgrade-prompt', 'CSRD features require Enterprise subscription');
                } else {
                    throw new Error('Failed to load reports');
                }
            } catch (error) {
                console.error('Error loading CSRD reports:', error);
                this.$emit('show-error', 'Failed to load CSRD reports');
            } finally {
                this.loading = false;
            }
        },

        async createReport() {
            this.creating = true;
            try {
                const response = await fetch(`${this.apiBase}/api/v1/csrd/reports`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`,
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: new URLSearchParams(this.newReport).toString()
                });

                if (response.ok) {
                    this.$emit('show-success', 'CSRD report created successfully');
                    this.showCreateModal = false;
                    this.resetNewReport();
                    await this.loadReports();
                } else {
                    throw new Error('Failed to create report');
                }
            } catch (error) {
                console.error('Error creating report:', error);
                this.$emit('show-error', 'Failed to create report');
            } finally {
                this.creating = false;
            }
        },

        async viewReport(reportId) {
            try {
                const response = await fetch(
                    `${this.apiBase}/api/v1/csrd/reports/${reportId}`,
                    {
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('token')}`
                        }
                    }
                );

                if (response.ok) {
                    this.selectedReport = await response.json();
                } else {
                    throw new Error('Failed to load report details');
                }
            } catch (error) {
                console.error('Error viewing report:', error);
                this.$emit('show-error', 'Failed to load report details');
            }
        },

        editReport(reportId) {
            // Navigate to edit page (implement edit component separately)
            this.$emit('navigate-to', `/csrd/edit/${reportId}`);
        },

        async exportPDF(reportId) {
            try {
                const response = await fetch(
                    `${this.apiBase}/api/v1/csrd/reports/${reportId}/export/pdf`,
                    {
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('token')}`
                        }
                    }
                );

                if (response.ok) {
                    const data = await response.json();
                    window.open(data.download_url, '_blank');
                    this.$emit('show-success', 'PDF export initiated');
                } else {
                    throw new Error('Failed to export PDF');
                }
            } catch (error) {
                console.error('Error exporting PDF:', error);
                this.$emit('show-error', 'Failed to export PDF');
            }
        },

        async viewAuditTrail(reportId) {
            // Implement audit trail viewer
            this.$emit('navigate-to', `/csrd/audit/${reportId}`);
        },

        calculateStatistics() {
            this.statistics.totalReports = this.reports.length;
            this.statistics.inProgress = this.reports.filter(
                r => r.status === 'IN_PROGRESS'
            ).length;
            this.statistics.submitted = this.reports.filter(
                r => r.status === 'SUBMITTED'
            ).length;
            
            if (this.reports.length > 0) {
                const totalCompleteness = this.reports.reduce(
                    (sum, r) => sum + (r.completeness_score || 0), 0
                );
                this.statistics.avgCompleteness = Math.round(
                    totalCompleteness / this.reports.length
                );
            } else {
                this.statistics.avgCompleteness = 0;
            }
        },

        resetNewReport() {
            this.newReport = {
                company_name: '',
                reporting_year: new Date().getFullYear(),
                reporting_period: 'ANNUAL',
                country: '',
                sector: '',
                employee_count: null,
                annual_revenue_eur: null
            };
        },

        formatStatus(status) {
            const statusMap = {
                'NOT_STARTED': 'Not Started',
                'IN_PROGRESS': 'In Progress',
                'REVIEW': 'Under Review',
                'COMPLETED': 'Completed',
                'SUBMITTED': 'Submitted'
            };
            return statusMap[status] || status;
        },

        getStatusClass(status) {
            const classMap = {
                'NOT_STARTED': 'status-grey',
                'IN_PROGRESS': 'status-yellow',
                'REVIEW': 'status-blue',
                'COMPLETED': 'status-green',
                'SUBMITTED': 'status-green'
            };
            return classMap[status] || 'status-grey';
        },

        getCompletenessClass(score) {
            if (score >= 95) return 'progress-excellent';
            if (score >= 75) return 'progress-good';
            if (score >= 50) return 'progress-fair';
            return 'progress-poor';
        },

        formatDate(dateString) {
            if (!dateString) return 'N/A';
            const date = new Date(dateString);
            return date.toLocaleDateString('en-GB', {
                day: '2-digit',
                month: 'short',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    },
    computed: {
        apiBase() {
            return window.API_BASE_URL || 'https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod';
        }
    }
};

// Export for use in main app
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CSRDDashboard;
}
