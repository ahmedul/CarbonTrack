// CarbonTrack Vue.js Application - Compatible Version
console.log('CarbonTrack app starting...');

if (typeof Vue === 'undefined') {
    console.error('Vue.js is not available!');
    document.body.innerHTML = '<h1 style="color: red; text-align: center; margin-top: 50px;">Vue.js failed to load from CDN. Please check your internet connection.</h1>';
} else {
    console.log('Vue.js loaded successfully');
}

const { createApp } = Vue;

const app = createApp({
    data() {
        return {
            currentView: 'dashboard',
            isAuthenticated: false,
            authToken: null,
            apiBase: 'http://localhost:8000/api/v1',
            
            // User data
            userProfile: {
                user_id: '',
                email: '',
                full_name: '',
                carbon_budget: 500
            },
            
            // Forms
            loginForm: {
                email: 'demo@carbontrack.dev',
                password: 'password123'
            },
            
            emissionForm: {
                category: '',
                activity: '',
                amount: '',
                unit: '',
                date: new Date().toISOString().split('T')[0],
                description: ''
            },
            
            // Data
            emissions: [],
            totalEmissions: 245.8,
            monthlyEmissions: 34.2,
            goalProgress: 68,
            chart: null,
            
            // Notifications
            notifications: [],
            
            // Loading states
            loading: false
        };
    },
    
    mounted() {
        console.log('Vue app mounted successfully!');
        // Check for stored authentication
        const token = localStorage.getItem('carbontrack_token');
        if (token) {
            this.authToken = token;
            this.isAuthenticated = true;
            this.loadUserData();
            this.loadEmissions();
        }
        this.initializeChart();
    },
    
    methods: {
        // Authentication methods
        login() {
            console.log('Login attempt for:', this.loginForm.email);
            
            if (this.loginForm.email === 'demo@carbontrack.dev' && this.loginForm.password === 'password123') {
                this.isAuthenticated = true;
                this.currentView = 'dashboard';
                this.userProfile = {
                    user_id: 'demo-user',
                    email: this.loginForm.email,
                    full_name: 'Demo User',
                    carbon_budget: 500
                };
                localStorage.setItem('carbontrack_token', 'demo-token-123');
                
                // Load initial sample data
                this.loadEmissions();
                
                this.showNotification('Login successful! Welcome to CarbonTrack.', 'success');
                this.initializeChart();
            } else {
                this.showNotification('Invalid credentials. Use demo@carbontrack.dev / password123', 'error');
            }
        },
        
        logout() {
            console.log('Logging out user');
            this.isAuthenticated = false;
            this.currentView = 'login';
            this.userProfile = { user_id: '', email: '', full_name: '', carbon_budget: 500 };
            localStorage.removeItem('carbontrack_token');
            this.loginForm = { email: '', password: '' };
            this.showNotification('You have been logged out successfully.', 'success');
        },
        
        // Data loading methods
        loadUserData() {
            console.log('Loading user profile data');
            // Simulate API call with demo data
            this.userProfile = {
                user_id: 'demo-user',
                email: 'demo@carbontrack.dev',
                full_name: 'Demo User',
                carbon_budget: 500
            };
        },
        
        loadEmissions() {
            console.log('Loading emissions data');
            // Simulate loading emissions with realistic demo data
            this.emissions = [
                {
                    id: '1',
                    category: 'transportation',
                    activity: 'Flight to London',
                    amount: 150.5,
                    unit: 'kg',
                    date: '2025-09-25',
                    description: 'Business trip to London'
                },
                {
                    id: '2',
                    category: 'transportation',
                    activity: 'Car commute',
                    amount: 25.4,
                    unit: 'kg',
                    date: '2025-09-24',
                    description: 'Daily commute to office'
                },
                {
                    id: '3',
                    category: 'energy',
                    activity: 'Home electricity',
                    amount: 45.2,
                    unit: 'kg',
                    date: '2025-09-23',
                    description: 'Monthly electricity bill'
                },
                {
                    id: '4',
                    category: 'food',
                    activity: 'Restaurant dining',
                    amount: 12.1,
                    unit: 'kg',
                    date: '2025-09-22',
                    description: 'Dinner at steakhouse'
                },
                {
                    id: '5',
                    category: 'transportation',
                    activity: 'Uber rides',
                    amount: 8.7,
                    unit: 'kg',
                    date: '2025-09-21',
                    description: 'City transportation'
                },
                {
                    id: '6',
                    category: 'energy',
                    activity: 'Office electricity',
                    amount: 23.8,
                    unit: 'kg',
                    date: '2025-09-20',
                    description: 'Workspace energy consumption'
                },
                {
                    id: '7',
                    category: 'food',
                    activity: 'Grocery shopping',
                    amount: 15.2,
                    unit: 'kg',
                    date: '2025-09-19',
                    description: 'Weekly groceries'
                },
                {
                    id: '8',
                    category: 'waste',
                    activity: 'Recycling credit',
                    amount: -2.1,
                    unit: 'kg',
                    date: '2025-09-18',
                    description: 'Paper and plastic recycling'
                }
            ];
            
            // Calculate totals
            this.totalEmissions = this.emissions.reduce(function(sum, emission) {
                return sum + emission.amount;
            }, 0);
            
            // Calculate this month's emissions (September 2025)
            this.monthlyEmissions = this.emissions.filter(function(emission) {
                return emission.date.startsWith('2025-09');
            }).reduce(function(sum, emission) {
                return sum + emission.amount;
            }, 0);
            
            // Update goal progress (assuming 300kg monthly target)
            this.goalProgress = Math.min(Math.round((this.monthlyEmissions / 300) * 100), 100);
        },
        
        // Emission management
        addEmission() {
            if (!this.emissionForm.category || !this.emissionForm.amount) {
                this.showNotification('Please fill in all required fields', 'error');
                return;
            }
            
            const newEmission = {
                id: Date.now().toString(),
                category: this.emissionForm.category,
                activity: this.emissionForm.activity || this.emissionForm.category,
                amount: parseFloat(this.emissionForm.amount),
                unit: 'kg',
                date: this.emissionForm.date,
                description: this.emissionForm.description
            };
            
            this.emissions.unshift(newEmission);
            this.totalEmissions += newEmission.amount;
            this.monthlyEmissions += newEmission.amount;
            
            // Reset form
            this.emissionForm = {
                category: '',
                activity: '',
                amount: '',
                unit: '',
                date: new Date().toISOString().split('T')[0],
                description: ''
            };
            
            this.showNotification('Carbon emission added successfully!', 'success');
            this.updateChart();
        },
        
        deleteEmission(emissionId) {
            const index = this.emissions.findIndex(function(e) { return e.id === emissionId; });
            if (index !== -1) {
                const emission = this.emissions[index];
                this.totalEmissions -= emission.amount;
                this.monthlyEmissions -= emission.amount;
                this.emissions.splice(index, 1);
                this.showNotification('Emission deleted successfully', 'success');
                this.updateChart();
            }
        },
        
        // Sample data creation
        createSampleData() {
            console.log('Creating additional sample data');
            const sampleEmissions = [
                { category: 'transportation', activity: 'Train to Manchester', amount: 35.8, date: '2025-09-17', description: 'Business meeting' },
                { category: 'energy', activity: 'Home heating', amount: 67.3, date: '2025-09-16', description: 'September heating bill' },
                { category: 'food', activity: 'Restaurant dining', amount: 8.5, date: '2025-09-15', description: 'Dinner with clients' },
                { category: 'transportation', activity: 'Taxi to airport', amount: 12.7, date: '2025-09-14', description: 'Airport transfer' },
                { category: 'energy', activity: 'Office electricity', amount: 23.8, date: '2025-09-13', description: 'Workspace consumption' },
                { category: 'food', activity: 'Coffee shop visit', amount: 2.3, date: '2025-09-12', description: 'Daily coffee' },
                { category: 'waste', activity: 'Recycling credit', amount: -1.5, date: '2025-09-11', description: 'Glass recycling' },
                { category: 'transportation', activity: 'Bus commute', amount: 4.2, date: '2025-09-10', description: 'Public transport' },
                { category: 'energy', activity: 'Phone charging', amount: 0.3, date: '2025-09-09', description: 'Daily device usage' },
                { category: 'food', activity: 'Lunch delivery', amount: 3.7, date: '2025-09-08', description: 'Food delivery service' }
            ];
            
            var totalAdded = 0;
            for (var i = 0; i < sampleEmissions.length; i++) {
                var emission = sampleEmissions[i];
                emission.id = Date.now().toString() + i;
                emission.unit = 'kg';
                this.emissions.unshift(emission);
                totalAdded += emission.amount;
            }
            
            // Recalculate totals
            this.totalEmissions = this.emissions.reduce(function(sum, emission) {
                return sum + emission.amount;
            }, 0);
            
            this.monthlyEmissions = this.emissions.filter(function(emission) {
                return emission.date.startsWith('2025-09');
            }).reduce(function(sum, emission) {
                return sum + emission.amount;
            }, 0);
            
            // Update goal progress
            this.goalProgress = Math.min(Math.round((this.monthlyEmissions / 300) * 100), 100);
            
            this.showNotification('Additional sample data created! ' + sampleEmissions.length + ' emissions added.', 'success');
            this.updateChart();
        },
        
        // Chart methods
        initializeChart() {
            if (typeof Chart === 'undefined') {
                console.warn('Chart.js not loaded, skipping chart initialization');
                return;
            }
            
            setTimeout(function() {
                const ctx = document.getElementById('emissionsChart');
                if (ctx && !this.chart) {
                    this.chart = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: ['Sep 18', 'Sep 19', 'Sep 20', 'Sep 21', 'Sep 22', 'Sep 23', 'Sep 24', 'Sep 25'],
                            datasets: [{
                                label: 'Daily CO₂ Emissions (kg)',
                                data: [23.5, 15.2, 45.6, 8.7, 12.1, 45.2, 25.4, 150.5],
                                borderColor: 'rgb(59, 130, 246)',
                                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                                borderWidth: 3,
                                fill: true,
                                tension: 0.4,
                                pointBackgroundColor: 'rgb(59, 130, 246)',
                                pointBorderColor: '#fff',
                                pointBorderWidth: 2,
                                pointRadius: 5
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    display: true,
                                    position: 'top',
                                    labels: {
                                        font: {
                                            size: 14
                                        },
                                        color: '#374151'
                                    }
                                },
                                tooltip: {
                                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                                    titleColor: '#fff',
                                    bodyColor: '#fff',
                                    borderColor: 'rgb(59, 130, 246)',
                                    borderWidth: 1
                                }
                            },
                            scales: {
                                x: {
                                    display: true,
                                    title: {
                                        display: true,
                                        text: 'Date',
                                        color: '#6b7280',
                                        font: {
                                            size: 12
                                        }
                                    },
                                    grid: {
                                        color: 'rgba(0, 0, 0, 0.05)'
                                    },
                                    ticks: {
                                        color: '#6b7280',
                                        font: {
                                            size: 11
                                        }
                                    }
                                },
                                y: {
                                    beginAtZero: true,
                                    display: true,
                                    title: {
                                        display: true,
                                        text: 'CO₂ Emissions (kg)',
                                        color: '#6b7280',
                                        font: {
                                            size: 12
                                        }
                                    },
                                    grid: {
                                        color: 'rgba(0, 0, 0, 0.05)'
                                    },
                                    ticks: {
                                        color: '#6b7280',
                                        font: {
                                            size: 11
                                        }
                                    }
                                }
                            },
                            elements: {
                                point: {
                                    hoverRadius: 8
                                }
                            }
                        }
                    });
                }
            }.bind(this), 100);
        },
        
        updateChart() {
            if (this.chart && this.emissions.length > 0) {
                // Get last 7 days of emissions data
                var chartData = [];
                var chartLabels = [];
                
                // Sort emissions by date and get recent ones
                var sortedEmissions = this.emissions.slice().sort(function(a, b) {
                    return new Date(a.date) - new Date(b.date);
                });
                
                var recentEmissions = sortedEmissions.slice(-8); // Last 8 entries
                
                for (var i = 0; i < recentEmissions.length; i++) {
                    var emission = recentEmissions[i];
                    var date = new Date(emission.date);
                    var label = (date.getMonth() + 1) + '/' + date.getDate();
                    chartLabels.push(label);
                    chartData.push(emission.amount);
                }
                
                // Update chart data
                this.chart.data.labels = chartLabels;
                this.chart.data.datasets[0].data = chartData;
                this.chart.update('active');
            }
        },
        
        // Navigation methods
        switchView(view) {
            this.currentView = view;
            console.log('Switched to view:', view);
        },
        
        // Notification system
        showNotification(message, type) {
            console.log('[' + type + '] ' + message);
            const notification = {
                id: Date.now(),
                message: message,
                type: type || 'info'
            };
            this.notifications.push(notification);
            
            // Auto-remove notification after 5 seconds
            setTimeout(function() {
                const index = this.notifications.findIndex(function(n) { return n.id === notification.id; });
                if (index !== -1) {
                    this.notifications.splice(index, 1);
                }
            }.bind(this), 5000);
        },
        
        removeNotification(notificationId) {
            const index = this.notifications.findIndex(function(n) { return n.id === notificationId; });
            if (index !== -1) {
                this.notifications.splice(index, 1);
            }
        },
        
        // Utility methods
        formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric' 
            });
        },
        
        getCategoryIcon(category) {
            const icons = {
                transportation: '🚗',
                energy: '⚡',
                food: '🍽️',
                waste: '♻️'
            };
            return icons[category] || '📊';
        },
        
        getCategoryColor(category) {
            const colors = {
                transportation: 'text-blue-600',
                energy: 'text-yellow-600',
                food: 'text-green-600',
                waste: 'text-purple-600'
            };
            return colors[category] || 'text-gray-600';
        },
        
        displayTotalEmissions() {
            return Math.round(this.totalEmissions * 100) / 100;
        },
        
        displayMonthlyEmissions() {
            return Math.round(this.monthlyEmissions * 100) / 100;
        }
    }
});

console.log('Vue app created, attempting to mount...');
try {
    app.mount('#app');
    console.log('CarbonTrack Vue app mounted successfully!');
} catch (error) {
    console.error('Error mounting Vue app:', error);
    document.body.innerHTML = '<h1 style="color: red; text-align: center; margin-top: 50px;">Failed to mount Vue app: ' + error.message + '</h1>';
}