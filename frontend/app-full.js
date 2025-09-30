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
            apiBase: 'https://ahzh0n0k6c.execute-api.us-east-1.amazonaws.com/prod/api/v1',
            
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
            
            registerForm: {
                firstName: '',
                lastName: '',
                email: '',
                password: '',
                confirmPassword: '',
                organization: '',
                acceptTerms: false
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
            
            // Activity options for better user experience
            activityOptions: {
                transportation: [
                    { key: 'car_gasoline_medium', name: 'Medium Gasoline Car', unit: 'km', example: '25 km commute ≈ 4.8 kg CO₂' },
                    { key: 'car_gasoline_small', name: 'Small Gasoline Car', unit: 'km', example: '25 km commute ≈ 3.8 kg CO₂' },
                    { key: 'car_gasoline_large', name: 'Large Car/SUV', unit: 'km', example: '25 km commute ≈ 6.3 kg CO₂' },
                    { key: 'car_hybrid', name: 'Hybrid Vehicle', unit: 'km', example: '25 km commute ≈ 2.7 kg CO₂' },
                    { key: 'car_electric', name: 'Electric Vehicle', unit: 'km', example: '25 km commute ≈ 3.0 kg CO₂' },
                    { key: 'motorcycle', name: 'Motorcycle', unit: 'km', example: '25 km ride ≈ 2.6 kg CO₂' },
                    { key: 'bus_city', name: 'City Bus', unit: 'km', example: '25 km trip ≈ 2.2 kg CO₂' },
                    { key: 'train_local', name: 'Local Train', unit: 'km', example: '25 km trip ≈ 1.0 kg CO₂' },
                    { key: 'flight_domestic_short', name: 'Domestic Flight (<500km)', unit: 'km', example: '500 km flight ≈ 128 kg CO₂' },
                    { key: 'flight_international', name: 'International Flight', unit: 'km', example: '1000 km flight ≈ 150 kg CO₂' }
                ],
                energy: [
                    { key: 'electricity', name: 'Electricity Usage', unit: 'kWh', example: '100 kWh ≈ 40 kg CO₂' },
                    { key: 'natural_gas', name: 'Natural Gas', unit: 'therms', example: '10 therms ≈ 53 kg CO₂' },
                    { key: 'heating_oil', name: 'Heating Oil', unit: 'gallons', example: '10 gallons ≈ 95 kg CO₂' },
                    { key: 'propane', name: 'Propane', unit: 'gallons', example: '10 gallons ≈ 57 kg CO₂' }
                ],
                food: [
                    { key: 'beef', name: 'Beef', unit: 'kg', example: '1 kg ≈ 60 kg CO₂' },
                    { key: 'lamb', name: 'Lamb', unit: 'kg', example: '1 kg ≈ 39 kg CO₂' },
                    { key: 'pork', name: 'Pork', unit: 'kg', example: '1 kg ≈ 12 kg CO₂' },
                    { key: 'chicken', name: 'Chicken', unit: 'kg', example: '1 kg ≈ 10 kg CO₂' },
                    { key: 'fish_farmed', name: 'Farmed Fish', unit: 'kg', example: '1 kg ≈ 14 kg CO₂' },
                    { key: 'fish_wild', name: 'Wild Fish', unit: 'kg', example: '1 kg ≈ 3 kg CO₂' },
                    { key: 'cheese', name: 'Cheese', unit: 'kg', example: '1 kg ≈ 14 kg CO₂' },
                    { key: 'milk', name: 'Milk', unit: 'liters', example: '1 liter ≈ 3.2 kg CO₂' },
                    { key: 'eggs', name: 'Eggs', unit: 'kg', example: '1 kg ≈ 4.2 kg CO₂' },
                    { key: 'rice', name: 'Rice', unit: 'kg', example: '1 kg ≈ 4 kg CO₂' },
                    { key: 'vegetables_root', name: 'Root Vegetables', unit: 'kg', example: '1 kg ≈ 0.4 kg CO₂' },
                    { key: 'fruits_local', name: 'Local Fruits', unit: 'kg', example: '1 kg ≈ 1.1 kg CO₂' }
                ],
                waste: [
                    { key: 'landfill_mixed', name: 'Mixed Waste to Landfill', unit: 'kg', example: '10 kg ≈ 5.7 kg CO₂' },
                    { key: 'recycling_paper', name: 'Paper Recycling', unit: 'kg', example: '5 kg saves 4.5 kg CO₂' },
                    { key: 'recycling_plastic', name: 'Plastic Recycling', unit: 'kg', example: '2 kg saves 3.7 kg CO₂' },
                    { key: 'recycling_aluminum', name: 'Aluminum Recycling', unit: 'kg', example: '1 kg saves 8.9 kg CO₂' },
                    { key: 'composting_food', name: 'Food Composting', unit: 'kg', example: '5 kg saves 1.3 kg CO₂' }
                ]
            },
            
            // Notifications
            notifications: [],
            
            // Loading states
            loading: false,
            
            // Recommendations
            recommendations: [],
            selectedCategory: null,
            recommendationCategories: {
                transportation: { name: 'Transportation', description: 'Reduce emissions from travel', icon: '🚗' },
                energy: { name: 'Energy', description: 'Optimize energy usage', icon: '⚡' },
                food: { name: 'Food & Diet', description: 'Sustainable dietary choices', icon: '🥗' },
                waste: { name: 'Waste', description: 'Reduce, reuse, recycle', icon: '♻️' },
                lifestyle: { name: 'Lifestyle', description: 'Sustainable living', icon: '🌱' }
            },
            recommendationStats: {
                totalRecommendations: 0,
                potentialSavings: 0,
                quickWins: 0,
                highImpact: 0
            },
            
            // Gamification
            gamificationProfile: {
                total_points: 0,
                level: {
                    current_level: { name: 'Seedling', level: 1, icon: '🌱' },
                    next_level: null,
                    progress_to_next: 0
                },
                achievements_count: 0,
                goals_achieved: 0,
                streak: {
                    current_streak: 0,
                    longest_streak: 0,
                    streak_status: 'no_activities'
                }
            },
            recentAchievements: [],
            allAchievements: [],
            showAllAchievements: false,
            activeChallenges: [],
            leaderboards: [],
            selectedLeaderboardPeriod: 'weekly',
            gamificationStats: {
                achievements_earned: 0,
                total_activities: 0,
                carbon_saved_kg: 0,
                goals_achieved: 0
            },
            
            // Admin Panel Data
            adminTab: 'pending',
            adminStats: {
                totalUsers: 156,
                pendingRegistrations: 8,
                activeThisMonth: 42,
                totalCarbonTracked: 2847
            },
            pendingUsers: [
                {
                    id: 'pending_1',
                    firstName: 'Sarah',
                    lastName: 'Johnson',
                    email: 'sarah.johnson@example.com',
                    organization: 'Green Tech Inc.',
                    registeredAt: '2025-09-29T10:30:00Z'
                },
                {
                    id: 'pending_2',
                    firstName: 'Michael',
                    lastName: 'Chen',
                    email: 'michael.chen@university.edu',
                    organization: 'University Research Lab',
                    registeredAt: '2025-09-29T15:45:00Z'
                },
                {
                    id: 'pending_3',
                    firstName: 'Emma',
                    lastName: 'Davis',
                    email: 'emma.davis@startup.co',
                    organization: 'EcoSolutions Startup',
                    registeredAt: '2025-09-30T09:15:00Z'
                }
            ],
            allUsers: [
                {
                    id: 'user_1',
                    name: 'Demo User',
                    email: 'demo@carbontrack.dev',
                    status: 'active',
                    role: 'admin',
                    lastActive: '2025-09-30T12:00:00Z'
                },
                {
                    id: 'user_2',
                    name: 'Alex Thompson',
                    email: 'alex@greencompany.com',
                    status: 'active',
                    role: 'user',
                    lastActive: '2025-09-29T18:30:00Z'
                },
                {
                    id: 'user_3',
                    name: 'Lisa Rodriguez',
                    email: 'lisa@ecofirm.org',
                    status: 'inactive',
                    role: 'user',
                    lastActive: '2025-09-15T14:20:00Z'
                }
            ],
            userFilter: 'all',
            userSearch: '',
            systemSettings: {
                requireApproval: true,
                allowSelfRegistration: true
            }
        };
    },
    
    computed: {
        filteredRecommendations() {
            if (!this.selectedCategory) {
                return this.recommendations;
            }
            return this.recommendations.filter(rec => rec.category === this.selectedCategory);
        },
        
        filteredLeaderboards() {
            return this.leaderboards.filter(lb => 
                lb.period === this.selectedLeaderboardPeriod || 
                (this.selectedLeaderboardPeriod === 'all_time' && lb.period === 'all_time')
            );
        },
        
        isRegistrationValid() {
            return this.registerForm.firstName.trim() &&
                   this.registerForm.lastName.trim() &&
                   this.registerForm.email.trim() &&
                   this.registerForm.password.length >= 8 &&
                   this.registerForm.password === this.registerForm.confirmPassword &&
                   this.registerForm.acceptTerms;
        },
        
        filteredUsers() {
            let filtered = this.allUsers;
            
            // Apply status filter
            if (this.userFilter !== 'all') {
                if (this.userFilter === 'admins') {
                    filtered = filtered.filter(user => user.role === 'admin');
                } else {
                    filtered = filtered.filter(user => user.status === this.userFilter);
                }
            }
            
            // Apply search filter
            if (this.userSearch.trim()) {
                const search = this.userSearch.toLowerCase();
                filtered = filtered.filter(user => 
                    user.name.toLowerCase().includes(search) ||
                    user.email.toLowerCase().includes(search)
                );
            }
            
            return filtered;
        }
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
            this.loadRecommendations();
            this.loadRecommendationStats();
        }
        this.initializeChart();
    },
    
    methods: {
        // Activity selection helper
        selectActivity(option) {
            this.emissionForm.activity = option.key;
            this.emissionForm.unit = option.unit;
            console.log('Selected activity:', option.name, 'with unit:', option.unit);
        },
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
                    carbon_budget: 500,
                    role: 'admin'  // Make demo user an admin
                };
                localStorage.setItem('carbontrack_token', 'demo-token-123');
                
                // Load initial sample data
                this.loadEmissions();
                this.loadRecommendations();
                this.loadRecommendationStats();
                this.loadGamificationData();
                
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
                carbon_budget: 500,
                role: 'admin'
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
            console.log('Creating realistic sample data with accurate carbon calculations');
            const sampleEmissions = [
                // Transportation - using real activity names and accurate calculations
                { category: 'transportation', activity: 'car_gasoline_medium', amount: 25, unit: 'km', co2_equivalent: 4.8, date: '2025-09-20', description: 'Drive to downtown for meeting' },
                { category: 'transportation', activity: 'flight_domestic_short', amount: 320, unit: 'km', co2_equivalent: 81.6, date: '2025-09-18', description: 'Business trip to nearby city' },
                { category: 'transportation', activity: 'train_local', amount: 45, unit: 'km', co2_equivalent: 1.85, date: '2025-09-17', description: 'Train commute to office' },
                { category: 'transportation', activity: 'bus_city', amount: 12, unit: 'km', co2_equivalent: 1.07, date: '2025-09-16', description: 'Bus to shopping center' },
                
                // Energy - with realistic consumption patterns
                { category: 'energy', activity: 'electricity', amount: 450, unit: 'kWh', co2_equivalent: 180.45, date: '2025-09-15', description: 'Monthly home electricity bill' },
                { category: 'energy', activity: 'natural_gas', amount: 8, unit: 'therms', co2_equivalent: 42.4, date: '2025-09-14', description: 'Home heating and hot water' },
                
                // Food - with different impact levels
                { category: 'food', activity: 'beef', amount: 0.3, unit: 'kg', co2_equivalent: 18.0, date: '2025-09-13', description: 'Beef burger for lunch' },
                { category: 'food', activity: 'chicken', amount: 0.5, unit: 'kg', co2_equivalent: 4.95, date: '2025-09-12', description: 'Chicken dinner' },
                { category: 'food', activity: 'vegetables_root', amount: 2, unit: 'kg', co2_equivalent: 0.86, date: '2025-09-11', description: 'Weekly vegetable shopping' },
                { category: 'food', activity: 'milk', amount: 2, unit: 'liters', co2_equivalent: 6.4, date: '2025-09-10', description: 'Weekly milk purchase' },
                
                // Waste - showing both emissions and savings
                { category: 'waste', activity: 'recycling_aluminum', amount: 0.5, unit: 'kg', co2_equivalent: -4.47, date: '2025-09-09', description: 'Aluminum cans recycling' },
                { category: 'waste', activity: 'recycling_paper', amount: 3, unit: 'kg', co2_equivalent: -2.67, date: '2025-09-08', description: 'Weekly paper recycling' },
                { category: 'waste', activity: 'landfill_mixed', amount: 5, unit: 'kg', co2_equivalent: 2.85, date: '2025-09-07', description: 'General household waste' },
                { category: 'waste', activity: 'composting_food', amount: 2, unit: 'kg', co2_equivalent: -0.52, date: '2025-09-06', description: 'Food waste composting' }
            ];
            
            var totalAdded = 0;
            for (var i = 0; i < sampleEmissions.length; i++) {
                var emission = sampleEmissions[i];
                emission.id = Date.now().toString() + i;
                // Use the calculated co2_equivalent instead of raw amount
                this.emissions.unshift(emission);
                totalAdded += emission.co2_equivalent;
            }
            
            // Recalculate totals based on CO2 equivalent values
            this.totalEmissions = this.emissions.reduce(function(sum, emission) {
                return sum + (emission.co2_equivalent || emission.amount);
            }, 0);
            
            this.monthlyEmissions = this.emissions.filter(function(emission) {
                return emission.date.startsWith('2025-09');
            }).reduce(function(sum, emission) {
                return sum + (emission.co2_equivalent || emission.amount);
            }, 0);
            
            // Update goal progress (300kg CO2 monthly target)
            this.goalProgress = Math.min(Math.round((this.monthlyEmissions / 300) * 100), 100);
            
            this.showNotification('Realistic sample data created! ' + sampleEmissions.length + ' emissions added with scientific calculations.', 'success');
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
        },
        
        // Recommendations Methods
        async loadRecommendations() {
            if (!this.isAuthenticated) return;
            
            this.loading = true;
            try {
                const response = await axios.get(`${this.apiBase}/recommendations/`, {
                    headers: {
                        'Authorization': `Bearer ${this.authToken}`,
                        'Content-Type': 'application/json'
                    },
                    params: {
                        limit: 20
                    }
                });
                
                if (response.data.success) {
                    this.recommendations = response.data.data.recommendations;
                    this.updateRecommendationStats(response.data.data);
                } else {
                    console.error('Failed to load recommendations:', response.data);
                }
            } catch (error) {
                console.error('Error loading recommendations:', error);
                this.showNotification('Failed to load recommendations', 'error');
            } finally {
                this.loading = false;
            }
        },
        
        async loadRecommendationStats() {
            if (!this.isAuthenticated) return;
            
            try {
                const response = await axios.get(`${this.apiBase}/recommendations/stats`, {
                    headers: {
                        'Authorization': `Bearer ${this.authToken}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.data.success) {
                    const stats = response.data.data;
                    this.recommendationStats = {
                        totalRecommendations: stats.total_recommendations || 0,
                        potentialSavings: stats.potential_impact?.total_co2_savings_kg || 0,
                        quickWins: stats.potential_impact?.quick_wins || 0,
                        highImpact: stats.potential_impact?.high_impact_count || 0
                    };
                }
            } catch (error) {
                console.error('Error loading recommendation stats:', error);
            }
        },
        
        updateRecommendationStats(data) {
            this.recommendationStats = {
                totalRecommendations: data.count || 0,
                potentialSavings: data.total_potential_savings_kg || 0,
                quickWins: data.implementation_stats?.easy || 0,
                highImpact: this.recommendations.filter(rec => rec.co2_savings_kg > 50).length
            };
        },
        
        getCategoryIcon(category) {
            const icons = {
                transportation: '🚗',
                energy: '⚡',
                food: '🥗',
                waste: '♻️',
                lifestyle: '🌱'
            };
            return icons[category] || '📋';
        },
        
        getDifficultyColor(difficulty) {
            const colors = {
                'Easy': 'bg-green-100 text-green-800',
                'Medium': 'bg-yellow-100 text-yellow-800',
                'Hard': 'bg-red-100 text-red-800'
            };
            return colors[difficulty] || 'bg-gray-100 text-gray-800';
        },
        
        getCostColor(cost) {
            const colors = {
                'Free': 'bg-green-100 text-green-800',
                'Low Cost': 'bg-blue-100 text-blue-800',
                'Medium Cost': 'bg-yellow-100 text-yellow-800',
                'High Cost': 'bg-red-100 text-red-800'
            };
            return colors[cost] || 'bg-gray-100 text-gray-800';
        },
        
        // Gamification Methods
        async loadGamificationProfile() {
            if (!this.isAuthenticated) return;
            
            this.loading = true;
            try {
                const response = await axios.get(`${this.apiBase}/gamification/profile`, {
                    headers: {
                        'Authorization': `Bearer ${this.authToken}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.data.success) {
                    const data = response.data.data;
                    this.gamificationProfile = data.user_profile;
                    this.recentAchievements = data.recent_achievements;
                    this.activeChallenges = data.active_challenges;
                    this.gamificationStats = data.statistics;
                } else {
                    console.error('Failed to load gamification profile:', response.data);
                }
            } catch (error) {
                console.error('Error loading gamification profile:', error);
                this.showNotification('Failed to load achievements data', 'error');
            } finally {
                this.loading = false;
            }
        },
        
        async loadAchievements() {
            if (!this.isAuthenticated) return;
            
            try {
                const response = await axios.get(`${this.apiBase}/gamification/achievements`, {
                    headers: {
                        'Authorization': `Bearer ${this.authToken}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.data.success) {
                    const data = response.data.data;
                    this.allAchievements = [...data.earned_achievements, ...data.achievements_progress];
                }
            } catch (error) {
                console.error('Error loading achievements:', error);
            }
        },
        
        async loadLeaderboards() {
            if (!this.isAuthenticated) return;
            
            try {
                const response = await axios.get(`${this.apiBase}/gamification/leaderboards`, {
                    headers: {
                        'Authorization': `Bearer ${this.authToken}`,
                        'Content-Type': 'application/json'
                    },
                    params: {
                        limit: 10
                    }
                });
                
                if (response.data.success) {
                    this.leaderboards = response.data.data.leaderboards;
                }
            } catch (error) {
                console.error('Error loading leaderboards:', error);
            }
        },
        
        async completeChallenge(challengeId) {
            try {
                const response = await axios.post(`${this.apiBase}/gamification/challenges/${challengeId}/complete`, {}, {
                    headers: {
                        'Authorization': `Bearer ${this.authToken}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.data.success) {
                    const result = response.data.data.challenge_completion;
                    this.showNotification(
                        `🎉 Challenge completed! +${result.points_earned} points`, 
                        'success'
                    );
                    
                    // Reload gamification data
                    this.loadGamificationProfile();
                    
                    // Show new achievements if any
                    if (response.data.data.new_achievements.length > 0) {
                        setTimeout(() => {
                            response.data.data.new_achievements.forEach(achievement => {
                                this.showNotification(
                                    `🏆 Achievement Unlocked: ${achievement.name}!`,
                                    'success'
                                );
                            });
                        }, 1000);
                    }
                } else {
                    this.showNotification('Failed to complete challenge', 'error');
                }
            } catch (error) {
                console.error('Error completing challenge:', error);
                this.showNotification('Failed to complete challenge', 'error');
            }
        },
        
        getRankColor(rank) {
            if (rank === 1) return 'bg-yellow-500'; // Gold
            if (rank === 2) return 'bg-gray-400'; // Silver
            if (rank === 3) return 'bg-yellow-600'; // Bronze
            if (rank <= 10) return 'bg-blue-500'; // Top 10
            return 'bg-gray-500'; // Others
        },
        
        // Load gamification data when user logs in
        loadGamificationData() {
            this.loadGamificationProfile();
            this.loadAchievements();
            this.loadLeaderboards();
        },
        
        // Registration Methods
        async register() {
            console.log('Register method called');
            console.log('Registration form data:', this.registerForm);
            console.log('Is registration valid?', this.isRegistrationValid);
            
            if (!this.isRegistrationValid) {
                this.showNotification('Please fill in all required fields correctly', 'error');
                return;
            }
            
            this.loading = true;
            try {
                // Simulate API call for registration
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                // In real implementation, this would call the backend API
                console.log('Registration data:', this.registerForm);
                
                this.showNotification(
                    'Registration successful! Please wait for admin approval before logging in.',
                    'success'
                );
                
                // Reset form and redirect to login
                this.registerForm = {
                    firstName: '',
                    lastName: '',
                    email: '',
                    password: '',
                    confirmPassword: '',
                    organization: '',
                    acceptTerms: false
                };
                
                this.currentView = 'login';
                
            } catch (error) {
                console.error('Registration error:', error);
                this.showNotification('Registration failed. Please try again.', 'error');
            } finally {
                this.loading = false;
            }
        },
        
        // Admin Methods
        async approveUser(userId) {
            try {
                // Simulate API call
                await new Promise(resolve => setTimeout(resolve, 500));
                
                // Find and remove from pending
                const userIndex = this.pendingUsers.findIndex(user => user.id === userId);
                if (userIndex !== -1) {
                    const user = this.pendingUsers[userIndex];
                    
                    // Add to approved users
                    this.allUsers.push({
                        id: `approved_${Date.now()}`,
                        name: `${user.firstName} ${user.lastName}`,
                        email: user.email,
                        status: 'active',
                        role: 'user',
                        lastActive: new Date().toISOString()
                    });
                    
                    // Remove from pending
                    this.pendingUsers.splice(userIndex, 1);
                    
                    // Update stats
                    this.adminStats.pendingRegistrations--;
                    this.adminStats.totalUsers++;
                    
                    this.showNotification('User approved successfully!', 'success');
                }
            } catch (error) {
                console.error('Error approving user:', error);
                this.showNotification('Failed to approve user', 'error');
            }
        },
        
        async rejectUser(userId) {
            try {
                // Simulate API call
                await new Promise(resolve => setTimeout(resolve, 500));
                
                // Remove from pending
                const userIndex = this.pendingUsers.findIndex(user => user.id === userId);
                if (userIndex !== -1) {
                    this.pendingUsers.splice(userIndex, 1);
                    this.adminStats.pendingRegistrations--;
                    this.showNotification('User registration rejected', 'success');
                }
            } catch (error) {
                console.error('Error rejecting user:', error);
                this.showNotification('Failed to reject user', 'error');
            }
        },
        
        editUser(userId) {
            // Placeholder for user edit functionality
            this.showNotification('User edit functionality coming soon', 'info');
        },
        
        async toggleUserStatus(userId) {
            try {
                // Simulate API call
                await new Promise(resolve => setTimeout(resolve, 500));
                
                const user = this.allUsers.find(u => u.id === userId);
                if (user) {
                    user.status = user.status === 'active' ? 'inactive' : 'active';
                    this.showNotification(`User ${user.status === 'active' ? 'activated' : 'deactivated'} successfully`, 'success');
                }
            } catch (error) {
                console.error('Error toggling user status:', error);
                this.showNotification('Failed to update user status', 'error');
            }
        },
        
        async saveSettings() {
            try {
                // Simulate API call
                await new Promise(resolve => setTimeout(resolve, 500));
                
                console.log('Saving settings:', this.systemSettings);
                this.showNotification('Settings saved successfully!', 'success');
            } catch (error) {
                console.error('Error saving settings:', error);
                this.showNotification('Failed to save settings', 'error');
            }
        },
        
        formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
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