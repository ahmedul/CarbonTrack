// Vue.js Application for CarbonTrack
console.log('App.js starting...');

if (typeof Vue === 'undefined') {
    console.error('Vue.js is not available!');
    alert('Vue.js failed to load from CDN');
} else {
    console.log('Vue.js is available');
}

const { createApp } = Vue;

const app = createApp({
    data() {
        return {
            currentView: 'dashboard',
            isAuthenticated: false,
            authToken: null,
            apiBase: 'https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1',
            
            // Cognito Configuration
            cognitoConfig: {
                region: 'eu-central-1',
                userPoolId: 'eu-central-1_liszdknXy',
                clientId: '3rg58gvke8v6afmfng7o4fk0r1'
            },
            
            // User data
            userProfile: {
                user_id: '',
                email: '',
                full_name: '',
                carbon_budget: 500
            },
            
            // Forms
            loginForm: {
                email: '',
                password: ''
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
            totalEmissions: 0,
            monthlyEmissions: 0,
            goalProgress: 0,
            chart: null,
            
            // Demo data - matches what we added to DynamoDB
            demoEmissions: [
                {
                    id: "demo-1",
                    date: "2024-01-15",
                    category: "transportation",
                    activity: "car_gasoline_medium",
                    amount: 25.5,
                    unit: "km",
                    description: "Daily commute to office",
                    co2_equivalent: 4.896,
                    created_at: "2024-01-15T09:30:00Z"
                },
                {
                    id: "demo-2", 
                    date: "2024-01-14",
                    category: "energy",
                    activity: "electricity",
                    amount: 12.3,
                    unit: "kWh",
                    description: "Home electricity usage",
                    co2_equivalent: 4.932,
                    created_at: "2024-01-14T18:45:00Z"
                },
                {
                    id: "demo-3",
                    date: "2024-01-13", 
                    category: "food",
                    activity: "beef",
                    amount: 0.5,
                    unit: "kg",
                    description: "Lunch - beef burger",
                    co2_equivalent: 30.0,
                    created_at: "2024-01-13T12:00:00Z"
                }
            ]
        };
    },
    
    async mounted() {
        // Check for stored authentication
        const token = localStorage.getItem('carbontrack_token');
        const storedUser = localStorage.getItem('carbontrack_user');
        
        if (token) {
            this.authToken = token;
            this.isAuthenticated = true;
            
            // Restore user profile from localStorage
            if (storedUser) {
                try {
                    this.userProfile = JSON.parse(storedUser);
                    console.log('Restored user profile:', this.userProfile);
                } catch (e) {
                    console.error('Failed to parse stored user:', e);
                }
            }
            
            await this.loadUserData();
        } else {
            // Load demo data when not authenticated
            this.loadDemoData();
        }
    },
    
    methods: {
        async login() {
            try {
                console.log('Attempting login with:', this.loginForm.email);
                console.log('API Base:', this.apiBase);
                
                const response = await axios.post(`${this.apiBase}/auth/login`, {
                    email: this.loginForm.email,
                    password: this.loginForm.password
                });
                
                console.log('Login response:', response.data);
                
                this.authToken = response.data.access_token;
                this.isAuthenticated = true;
                localStorage.setItem('carbontrack_token', this.authToken);
                
                // Store user profile with role
                if (response.data.user) {
                    this.userProfile = response.data.user;
                    localStorage.setItem('carbontrack_user', JSON.stringify(response.data.user));
                }
                
                await this.loadUserData();
                this.currentView = 'dashboard';
                
                // Clear form
                this.loginForm = { email: '', password: '' };
                
                this.showNotification('Login successful!', 'success');
            } catch (error) {
                console.error('Login error:', error);
                console.error('Error response:', error.response && error.response.data);
                this.showNotification(`Login failed: ${(error.response && error.response.data && error.response.data.detail) || error.message}`, 'error');
            }
        },
        
        logout() {
            this.isAuthenticated = false;
            this.authToken = null;
            localStorage.removeItem('carbontrack_token');
            localStorage.removeItem('carbontrack_user');
            this.currentView = 'login';
            this.userProfile = { user_id: '', email: '', full_name: '', carbon_budget: 500 };
            this.emissions = [];
            this.showNotification('Logged out successfully', 'success');
        },
        
        async loadUserData() {
            try {
                await Promise.all([
                    this.loadUserProfile(),
                    this.loadEmissions()
                ]);
                this.calculateStats();
                this.$nextTick(() => {
                    this.renderChart();
                });
            } catch (error) {
                console.error('Error loading user data:', error);
            }
        },
        
        async loadUserProfile() {
            try {
                if (!this.authToken) {
                    console.log('No auth token available for profile');
                    return;
                }
                
                const response = await axios.get(`${this.apiBase}/users/profile`, {
                    headers: { Authorization: `Bearer ${this.authToken}` }
                });
                this.userProfile = response.data;
                console.log('Loaded user profile:', this.userProfile.email);
            } catch (error) {
                console.error('Error loading user profile:', error);
                if (error.response && error.response.status === 401) {
                    console.log('Authentication failed, logging out');
                    this.logout();
                }
            }
        },
        
        async loadEmissions() {
            try {
                if (!this.authToken) {
                    console.log('No auth token available');
                    return;
                }
                
                const response = await axios.get(`${this.apiBase}/carbon-emissions/`, {
                    headers: { Authorization: `Bearer ${this.authToken}` }
                });
                this.emissions = response.data || [];
                console.log('Loaded emissions:', this.emissions.length);
            } catch (error) {
                console.error('Error loading emissions:', error);
                if (error.response && error.response.status === 401) {
                    console.log('Authentication failed, logging out');
                    this.logout();
                } else {
                    this.emissions = [];
                }
            }
        },
        
        async addEmission() {
            try {
                console.log('Adding emission with data:', this.emissionForm);
                console.log('Auth token:', this.authToken ? 'Present' : 'Missing');
                
                // Validate required fields
                if (!this.emissionForm.category || !this.emissionForm.activity || 
                    !this.emissionForm.amount || !this.emissionForm.unit || !this.emissionForm.date) {
                    this.showNotification('Please fill in all required fields', 'error');
                    return;
                }
                
                // Handle demo mode when not authenticated
                if (!this.authToken) {
                    this.addDemoEmission();
                    return;
                }
                
                const response = await axios.post(`${this.apiBase}/carbon-emissions/`, {
                    date: this.emissionForm.date,
                    category: this.emissionForm.category,
                    activity: this.emissionForm.activity,
                    amount: parseFloat(this.emissionForm.amount),
                    unit: this.emissionForm.unit,
                    description: this.emissionForm.description || null
                }, {
                    headers: { 
                        'Authorization': `Bearer ${this.authToken}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                console.log('Emission created successfully:', response.data);
                
                // Add to local emissions array for immediate UI update
                this.emissions.unshift(response.data);
                this.calculateStats();
                this.renderChart();
                
                // Clear form
                this.emissionForm = {
                    category: '',
                    activity: '',
                    amount: '',
                    unit: '',
                    date: new Date().toISOString().split('T')[0],
                    description: ''
                };
                
                this.showNotification('Emission added successfully!', 'success');
                this.currentView = 'dashboard';
            } catch (error) {
                console.error('Error adding emission:', error);
                console.error('Error response:', error.response && error.response.data);
                
                if (error.response && error.response.status === 401) {
                    this.showNotification('Session expired. Please log in again.', 'error');
                    this.logout();
                } else if (error.response && error.response.status === 422) {
                    const details = error.response.data && error.response.data.detail;
                    if (Array.isArray(details)) {
                        const errorMsg = details.map(d => d.msg).join(', ');
                        this.showNotification(`Validation error: ${errorMsg}`, 'error');
                    } else {
                        this.showNotification('Please check your input data', 'error');
                    }
                } else {
                    this.showNotification(`Failed to add emission: ${(error.response && error.response.data && error.response.data.detail) || error.message}`, 'error');
                }
            }
        },
        
        async updateProfile() {
            try {
                if (!this.authToken) {
                    // Demo mode - just update locally
                    this.showNotification('Profile updated successfully! (Demo mode - login to save permanently)', 'success');
                    this.calculateStats(); // Recalculate with new budget
                    return;
                }
                
                await axios.put(`${this.apiBase}/users/profile`, this.userProfile, {
                    headers: { Authorization: `Bearer ${this.authToken}` }
                });
                this.showNotification('Profile updated successfully!', 'success');
                this.calculateStats(); // Recalculate with new budget
            } catch (error) {
                console.error('Error updating profile:', error);
                this.showNotification('Failed to update profile. Please try again.', 'error');
            }
        },
        
        calculateStats() {
            // Calculate total emissions
            this.totalEmissions = this.emissions.reduce((sum, emission) => {
                return sum + (emission.co2_equivalent || 0);
            }, 0);
            
            // Calculate monthly emissions (current month)
            const currentMonth = new Date().getMonth();
            const currentYear = new Date().getFullYear();
            
            this.monthlyEmissions = this.emissions
                .filter(emission => {
                    const emissionDate = new Date(emission.date);
                    return emissionDate.getMonth() === currentMonth && 
                           emissionDate.getFullYear() === currentYear;
                })
                .reduce((sum, emission) => sum + (emission.co2_equivalent || 0), 0);
            
            // Calculate goal progress
            if (this.userProfile.carbon_budget > 0) {
                this.goalProgress = Math.min(100, Math.round(
                    ((this.userProfile.carbon_budget - this.monthlyEmissions) / this.userProfile.carbon_budget) * 100
                ));
            }
        },
        
        renderChart() {
            // Use nextTick to ensure DOM is updated
            this.$nextTick(() => {
                const ctx = document.getElementById('emissionsChart');
                if (!ctx) {
                    console.log('Chart canvas not found, will retry...');
                    // Retry after a short delay if canvas not found
                    setTimeout(() => this.renderChart(), 100);
                    return;
                }
                
                // Destroy existing chart
                if (this.chart) {
                    this.chart.destroy();
                    this.chart = null;
                }
            
            // Group emissions by month
            const monthlyData = {};
            this.emissions.forEach(emission => {
                const date = new Date(emission.date);
                const monthKey = `${date.getFullYear()}-${date.getMonth() + 1}`;
                monthlyData[monthKey] = (monthlyData[monthKey] || 0) + (emission.co2_equivalent || 0);
            });
            
            // Prepare chart data
            const sortedMonths = Object.keys(monthlyData).sort();
            const labels = sortedMonths.map(month => {
                const [year, monthNum] = month.split('-');
                const date = new Date(year, monthNum - 1);
                return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
            });
            const data = sortedMonths.map(month => monthlyData[month]);
            
            this.chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'CO₂ Emissions (kg)',
                        data: data,
                        borderColor: '#3B82F6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#3B82F6',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                color: 'rgba(59, 130, 246, 0.1)',
                                borderColor: 'rgba(59, 130, 246, 0.2)'
                            },
                            ticks: {
                                color: '#6B7280',
                                font: {
                                    family: 'Inter',
                                    size: 12
                                }
                            }
                        },
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(59, 130, 246, 0.1)',
                                borderColor: 'rgba(59, 130, 246, 0.2)'
                            },
                            ticks: {
                                color: '#6B7280',
                                font: {
                                    family: 'Inter',
                                    size: 12
                                }
                            },
                            title: {
                                display: true,
                                text: 'CO₂ Emissions (kg)',
                                color: '#374151',
                                font: {
                                    family: 'Inter',
                                    size: 14,
                                    weight: '600'
                                }
                            }
                        }
                    }
                }
            });
            });
        },
        
        formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric' 
            });
        },
        
        showNotification(message, type = 'info') {
            // Simple notification system
            const notification = document.createElement('div');
            notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
                type === 'success' ? 'bg-green-500' : 
                type === 'error' ? 'bg-red-500' : 'bg-blue-500'
            } text-white`;
            notification.textContent = message;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.remove();
            }, 3000);
        },
        
        // Method to create sample data for demonstration
        async createSampleData() {
            if (!this.authToken) {
                this.showNotification('Please log in first', 'error');
                return;
            }
            
            const sampleEmissions = [
                // Recent entries (September 2025)
                { date: '2025-09-26', category: 'transportation', activity: 'Car commute to work', amount: 45, unit: 'km', description: 'Daily drive to office' },
                { date: '2025-09-25', category: 'energy', activity: 'Home electricity usage', amount: 12, unit: 'kWh', description: 'Air conditioning on hot day' },
                { date: '2025-09-24', category: 'food', activity: 'Restaurant dinner', amount: 2.5, unit: 'kg', description: 'Beef steak dinner with friends' },
                { date: '2025-09-23', category: 'transportation', activity: 'Flight to conference', amount: 850, unit: 'km', description: 'Business trip to Berlin' },
                { date: '2025-09-22', category: 'waste', activity: 'Household waste', amount: 3, unit: 'kg', description: 'Weekly garbage disposal' },
                
                // August 2025
                { date: '2025-08-28', category: 'transportation', activity: 'Weekend car trip', amount: 120, unit: 'km', description: 'Visit to countryside' },
                { date: '2025-08-25', category: 'energy', activity: 'Office electricity', amount: 8, unit: 'kWh', description: 'Extended work day' },
                { date: '2025-08-22', category: 'food', activity: 'Grocery shopping', amount: 1.8, unit: 'kg', description: 'Weekly organic groceries' },
                { date: '2025-08-20', category: 'transportation', activity: 'Public transport', amount: 25, unit: 'km', description: 'Bus and train commute' },
                { date: '2025-08-18', category: 'shopping', activity: 'Online purchases', amount: 5, unit: 'kg', description: 'Books and electronics delivery' },
                
                // July 2025
                { date: '2025-07-30', category: 'transportation', activity: 'Summer vacation flight', amount: 1200, unit: 'km', description: 'Holiday trip to Spain' },
                { date: '2025-07-25', category: 'energy', activity: 'Home cooling', amount: 18, unit: 'kWh', description: 'AC during heat wave' },
                { date: '2025-07-20', category: 'food', activity: 'BBQ party', amount: 4, unit: 'kg', description: 'Grilled meat for friends' },
                { date: '2025-07-15', category: 'transportation', activity: 'Daily commute', amount: 200, unit: 'km', description: 'Weekly commuting total' },
                { date: '2025-07-10', category: 'waste', activity: 'Recycling', amount: 2, unit: 'kg', description: 'Plastic and paper waste' },
                
                // June 2025  
                { date: '2025-06-28', category: 'transportation', activity: 'Car maintenance trip', amount: 35, unit: 'km', description: 'Drive to service center' },
                { date: '2025-06-22', category: 'energy', activity: 'Home office usage', amount: 10, unit: 'kWh', description: 'Working from home day' },
                { date: '2025-06-18', category: 'food', activity: 'Local restaurant', amount: 1.2, unit: 'kg', description: 'Vegetarian lunch' },
                { date: '2025-06-15', category: 'transportation', activity: 'Bike ride', amount: 15, unit: 'km', description: 'Cycling to meet friends' },
                { date: '2025-06-10', category: 'shopping', activity: 'Clothing purchase', amount: 3, unit: 'kg', description: 'New summer wardrobe' }
            ];
            
            let successCount = 0;
            this.showNotification('Creating sample data...', 'info');
            
            for (const emission of sampleEmissions) {
                try {
                    await new Promise(resolve => setTimeout(resolve, 100)); // Small delay to avoid rate limiting
                    
                    const response = await axios.post(`${this.apiBase}/carbon-emissions/`, {
                        date: emission.date,
                        category: emission.category,
                        activity: emission.activity,
                        amount: parseFloat(emission.amount),
                        unit: emission.unit,
                        description: emission.description
                    }, {
                        headers: { 
                            'Authorization': `Bearer ${this.authToken}`,
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    successCount++;
                    console.log(`Created emission ${successCount}:`, emission.activity);
                    
                } catch (error) {
                    console.error('Error creating sample emission:', error);
                    if (error.response && error.response.status === 401) {
                        this.showNotification('Session expired. Please log in again.', 'error');
                        this.logout();
                        return;
                    }
                }
            }
            
            this.showNotification(`Created ${successCount} sample emissions!`, 'success');
            
            // Reload data to show the new entries
            await this.loadEmissions();
            this.calculateStats();
            this.renderChart();
            this.currentView = 'dashboard';
        },
        
        loadDemoData() {
            // Load demo data for testing UI without authentication
            this.emissions = [...this.demoEmissions];
            this.userProfile.full_name = 'Demo User';
            this.userProfile.email = 'demo@carbontrack.dev';
            this.userProfile.carbon_budget = 500;
            this.calculateStats();
            this.renderChart();
            console.log('Loaded demo data:', this.emissions.length, 'emissions');
        },
        
        addDemoEmission() {
            // Calculate CO2 equivalent for demo (simplified calculation)
            let co2_equivalent = 0;
            const amount = parseFloat(this.emissionForm.amount);
            
            // Simple emission factors for demo
            const demoFactors = {
                'transportation': {
                    'car_gasoline_small': 0.151,
                    'car_gasoline_medium': 0.192,
                    'car_gasoline_large': 0.251,
                    'car_electric': 0.1203,
                    'bus_city': 0.089,
                    'flight_domestic_short': 0.255
                },
                'energy': {
                    'electricity': 0.401,
                    'natural_gas': 0.184,
                    'heating_oil': 2.54
                },
                'food': {
                    'beef': 60.0,
                    'chicken': 9.9,
                    'vegetables': 2.0
                }
            };
            
            if (demoFactors[this.emissionForm.category] && 
                demoFactors[this.emissionForm.category][this.emissionForm.activity]) {
                co2_equivalent = amount * demoFactors[this.emissionForm.category][this.emissionForm.activity];
            } else {
                co2_equivalent = amount * 2.0; // Default factor
            }
            
            // Create demo emission entry
            const newEmission = {
                id: `demo-${Date.now()}`,
                date: this.emissionForm.date,
                category: this.emissionForm.category,
                activity: this.emissionForm.activity,
                amount: amount,
                unit: this.emissionForm.unit,
                description: this.emissionForm.description || null,
                co2_equivalent: co2_equivalent,
                created_at: new Date().toISOString()
            };
            
            // Add to demo emissions array
            this.emissions.unshift(newEmission);
            this.calculateStats();
            this.renderChart();
            
            // Clear form
            this.emissionForm = {
                category: '',
                activity: '',
                amount: '',
                unit: '',
                date: new Date().toISOString().split('T')[0],
                description: ''
            };
            
            this.showNotification('Demo emission added successfully! (Login to save permanently)', 'success');
            this.currentView = 'dashboard';
        }
    },
    
    watch: {
        // Watch for view changes to re-render chart when returning to dashboard
        currentView(newView, oldView) {
            if (newView === 'dashboard' && oldView !== 'dashboard') {
                // Delay chart rendering to ensure DOM is ready
                this.$nextTick(() => {
                    setTimeout(() => {
                        this.renderChart();
                    }, 50);
                });
            }
        }
    },
    
    computed: {
        // Round numbers for display
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
    console.log('Vue app mounted successfully!');
} catch (error) {
    console.error('Error mounting Vue app:', error);
    alert('Failed to mount Vue app: ' + error.message);
}