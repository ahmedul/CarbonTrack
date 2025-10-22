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
            currentView: 'home',
            isAuthenticated: false,
            authToken: null,
            isDemo: false,
            // API base selection: allow runtime override via window.API_BASE_URL; fallback to localhost in dev, prod URL otherwise
            apiBase: (window.API_BASE_URL && typeof window.API_BASE_URL === 'string')
                ? window.API_BASE_URL
                : (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
                    ? 'http://localhost:8000'
                    : 'https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod'),
            
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
            totalEmissions: 0,
            monthlyEmissions: 0,
            goalProgress: 0,
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
                totalUsers: 0,
                pendingRegistrations: 0,
                activeThisMonth: 0,
                totalCarbonTracked: 0
            },
            pendingUsers: [],  // Will be loaded from API
            allUsers: [],  // Will be loaded from API
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
    
    async mounted() {
        console.log('Vue app mounted successfully!');
        // Check for stored authentication
        const token = localStorage.getItem('carbontrack_token');
        const storedUser = localStorage.getItem('carbontrack_user');
        
        if (token) {
            this.authToken = token;
            
            // Restore user profile from localStorage
            if (storedUser) {
                try {
                    this.userProfile = JSON.parse(storedUser);
                    console.log('Restored user profile:', this.userProfile);
                } catch (e) {
                    console.error('Failed to parse stored user:', e);
                }
            }
            
            // Treat demo tokens specially: keep session without backend validation
            if (this.isDemoToken(token)) {
                this.isDemo = true;
                this.isAuthenticated = true;
                this.currentView = 'dashboard';
                // Seed a basic demo profile if missing
                if (!this.userProfile.email) {
                    this.userProfile = {
                        user_id: 'demo-user',
                        email: 'demo@carbontrack.dev',
                        full_name: 'Demo User',
                        carbon_budget: 500,
                        role: 'user'
                    };
                }
                // Load UI data lazily
                this.loadEmissions();
                this.loadRecommendations();
                this.loadRecommendationStats();
                this.initializeChart();
            } else {
            // Validate the token with backend before loading data
            const valid = await this.validateSession();
            if (valid) {
                this.loadEmissions();
                this.loadRecommendations();
                this.loadRecommendationStats();
                // Load admin data if user is admin and token present
                if (this.userProfile.role === 'admin' && this.authToken) {
                    this.loadAdminData();
                }
            } else {
                // Invalid/expired token — clear state and show login
                this.logout();
            }
            }
        }
        this.initializeChart();
    },
    
    methods: {
        // Validate session by calling profile; clears bad tokens to avoid 401 spam
        async validateSession() {
            if (!this.authToken) return false;
            if (this.isDemoToken(this.authToken)) {
                // Skip backend validation for demo tokens
                this.isDemo = true;
                this.isAuthenticated = true;
                return true;
            }
            try {
                const resp = await axios.get(`${this.apiBase}/api/v1/auth/me`, {
                    headers: {
                        'Authorization': `Bearer ${this.authToken}`,
                        'Content-Type': 'application/json'
                    }
                });
                if (resp && resp.data) {
                    const p = resp.data.user || resp.data;
                    this.userProfile = {
                        user_id: p.user_id || p.userId || '',
                        email: p.email || '',
                        full_name: p.full_name || p.fullName || '',
                        carbon_budget: p.carbon_budget ?? 500,
                        role: p.role || 'user'
                    };
                    this.isAuthenticated = true;
                    return true;
                }
                return false;
            } catch (e) {
                const status = e?.response?.status;
                // Only log out on actual auth failures
                if (status === 401 || status === 403) {
                    console.warn('Auth invalid; clearing session.', status);
                    localStorage.removeItem('carbontrack_token');
                    this.authToken = null;
                    this.isAuthenticated = false;
                    return false;
                }
                // Network error or API down; keep session and continue with empty data
                console.warn('Profile check unreachable; keeping session.', status);
                this.isAuthenticated = true;
                return true;
            }
        },

        isDemoToken(token) {
            return typeof token === 'string' && token.startsWith('demo-');
        },
        // Activity selection helper
        selectActivity(option) {
            this.emissionForm.activity = option.key;
            this.emissionForm.unit = option.unit;
            console.log('Selected activity:', option.name, 'with unit:', option.unit);
        },
        
        // Navigation helper for logo click
        navigateToHome() {
            console.log('Logo clicked - navigating to home');
            if (this.isAuthenticated) {
                // If user is logged in, go to dashboard
                this.currentView = 'dashboard';
                console.log('Authenticated user - navigating to dashboard');
            } else {
                // If not logged in, go to welcome page (any view that's not login or register)
                this.currentView = 'home';
                console.log('Non-authenticated user - navigating to welcome page');
            }
        },
        // Authentication methods
        async login() {
            console.log('=== LOGIN ATTEMPT ===');
            console.log('Email:', this.loginForm.email);
            console.log('Password length:', this.loginForm.password.length);
            console.log('Is authenticated before login:', this.isAuthenticated);
            console.log('Current view:', this.currentView);
            
            this.loading = true;
            
            try {
                // First try API login
                const loginData = {
                    email: this.loginForm.email,
                    password: this.loginForm.password
                };
                
                const response = await axios.post(`${this.apiBase}/api/v1/auth/login`, loginData, {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.data && response.data.access_token) {
                    console.log('✅ Login successful via API');
                    
                    this.isAuthenticated = true;
                    this.currentView = 'dashboard';
                    this.authToken = response.data.access_token;
                    this.userProfile = {
                        user_id: response.data.user.user_id,
                        email: response.data.user.email,
                        full_name: response.data.user.full_name,
                        carbon_budget: response.data.user.carbon_budget || 500,
                        role: response.data.user.role || 'user'
                    };
                    localStorage.setItem('carbontrack_token', response.data.access_token);
                    localStorage.setItem('carbontrack_user', JSON.stringify(this.userProfile));
                    
                    // Load data from API
                    this.loadEmissions();
                    this.loadRecommendations();
                    this.loadRecommendationStats();
                    this.loadGamificationData();
                    
                    // Load admin data if user is admin
                    if (this.userProfile.role === 'admin') {
                        this.loadAdminData();
                    }
                    
                    this.showNotification('Login successful! Welcome to CarbonTrack.', 'success');
                    this.initializeChart();
                    return;
                }
            } catch (error) {
                console.log('📡 API login failed, trying demo accounts');
                console.error('API Error:', error);
            }
            
            // Fallback to demo accounts if API fails
            if (this.loginForm.email === 'demo@carbontrack.dev' && this.loginForm.password === 'password123') {
                this.isAuthenticated = true;
                this.currentView = 'dashboard';
                this.userProfile = {
                    user_id: 'demo-user',
                    email: this.loginForm.email,
                    full_name: 'Demo User',
                    carbon_budget: 500,
                    role: 'user'  // Regular user, not admin
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
                // Check approved users
                const approvedUser = this.allUsers.find(user => 
                    user.email === this.loginForm.email && 
                    user.status === 'active'
                );
                
                if (approvedUser && this.loginForm.password === 'password123') {
                    // Login approved user
                    this.isAuthenticated = true;
                    this.currentView = 'dashboard';
                    this.userProfile = {
                        user_id: approvedUser.id,
                        email: approvedUser.email,
                        full_name: approvedUser.name,
                        carbon_budget: 500,
                        role: approvedUser.role
                    };
                    localStorage.setItem('carbontrack_token', `user-token-${approvedUser.id}`);
                    
                    // Load initial sample data
                    this.loadEmissions();
                    this.loadRecommendations();
                    this.loadRecommendationStats();
                    this.loadGamificationData();
                    
                    this.showNotification(`Welcome back, ${approvedUser.name}!`, 'success');
                    this.initializeChart();
                } else {
                    console.log('❌ Login failed - invalid credentials');
                    console.log('Attempted email:', this.loginForm.email);
                    console.log('Password provided:', this.loginForm.password ? '(password provided)' : '(no password)');
                    this.showNotification('Invalid email or password. Please check your credentials and try again.', 'error');
                }
            }
            
            this.loading = false;
        },
        
        logout() {
            console.log('=== LOGOUT PROCESS ===');
            console.log('Before logout - isAuthenticated:', this.isAuthenticated);
            console.log('Before logout - currentView:', this.currentView);
            
            this.isAuthenticated = false;
            this.currentView = 'home';
            this.userProfile = { user_id: '', email: '', full_name: '', carbon_budget: 500, role: 'user' };
            localStorage.removeItem('carbontrack_token');
            localStorage.removeItem('carbontrack_user');
            
            // Reset login form
            this.loginForm = { email: '', password: '' };
            
            // Reset any loading states
            this.loading = false;
            
            console.log('After logout - isAuthenticated:', this.isAuthenticated);
            console.log('After logout - currentView:', this.currentView);
            console.log('After logout - loginForm:', this.loginForm);
            
            this.showNotification('You have been logged out successfully.', 'success');
        },

        // Debug method to reset login state
        resetLoginState() {
            console.log('=== RESETTING LOGIN STATE ===');
            this.isAuthenticated = false;
            this.currentView = 'login';
            this.loginForm = { email: '', password: '' };
            this.userProfile = { user_id: '', email: '', full_name: '', carbon_budget: 500, role: 'user' };
            this.loading = false;
            localStorage.removeItem('carbontrack_token');
            console.log('Login state reset complete');
        },

        // Data loading methods
        
        async loadEmissions() {
            console.log('Loading emissions data from API');
            this.loading = true;
            
            try {
                // Make API call to load user's emissions
                const response = await axios.get(`${this.apiBase}/api/v1/carbon-emissions/`, {
                    headers: {
                        'Authorization': `Bearer ${this.authToken}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.data.success) {
                    console.log('✅ Successfully loaded emissions from API');
                    this.emissions = response.data.data.emissions || [];
                    this.totalEmissions = response.data.data.total_emissions || 0;
                    this.monthlyEmissions = response.data.data.monthly_emissions || 0;
                    this.goalProgress = response.data.data.goal_progress || 0;
                } else {
                    console.log('❌ API call failed');
                    this.handleEmissionsFallback();
                }
            } catch (error) {
                console.error('Error loading emissions from API:', error);
                this.handleEmissionsFallback(error);
            } finally {
                this.loading = false;
            }
        },

        handleEmissionsFallback(error) {
            const isAuthError = error?.response?.status === 401;
            // Only show demo emissions for explicit demo/admin users
            if (this.userProfile.user_id === 'demo-user' || this.userProfile.user_id === 'admin-user') {
                console.log('Using demo emissions for demo/admin user');
                this.loadDemoEmissions();
                return;
            }
            // For unauthenticated or regular users, do not inject demo data
            if (isAuthError || !this.isAuthenticated || !this.authToken) {
                console.log('Unauthenticated or auth error; showing empty emissions.');
                this.emissions = [];
                this.totalEmissions = 0;
                this.monthlyEmissions = 0;
                this.goalProgress = 0;
                return;
            }
            // Non-auth related failures (network etc): keep safe empty fallback
            this.emissions = [];
            this.totalEmissions = 0;
            this.monthlyEmissions = 0;
            this.goalProgress = 0;
        },
        
        loadDemoEmissions() {
            console.log('Loading demo emissions data as fallback');
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
        async addEmission() {
            if (!this.emissionForm.category || !this.emissionForm.amount) {
                this.showNotification('Please fill in all required fields', 'error');
                return;
            }
            
            this.loading = true;
            
            try {
                const emissionData = {
                    category: this.emissionForm.category,
                    activity: this.emissionForm.activity || this.emissionForm.category,
                    amount: parseFloat(this.emissionForm.amount),
                    unit: this.emissionForm.unit || 'kg',
                    date: this.emissionForm.date,
                    description: this.emissionForm.description
                };
                
                // Make API call to save emission
                const response = await axios.post(`${this.apiBase}/api/v1/carbon-emissions/`, emissionData, {
                    headers: {
                        'Authorization': `Bearer ${this.authToken}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.data.success) {
                    console.log('✅ Successfully saved emission to API');
                    
                    // Add the emission with the ID returned from API
                    const newEmission = {
                        id: response.data.data.emission_id || Date.now().toString(),
                        ...emissionData
                    };
                    
                    this.emissions.unshift(newEmission);
                    this.totalEmissions += newEmission.amount;
                    this.monthlyEmissions += newEmission.amount;
                    
                    // Update goal progress
                    this.goalProgress = Math.min(Math.round((this.monthlyEmissions / 300) * 100), 100);
                    
                    this.showNotification('Carbon emission saved to database successfully!', 'success');
                } else {
                    console.log('❌ API save failed, adding locally only');
                    this.addEmissionLocally(emissionData);
                    this.showNotification('Emission added locally (API unavailable)', 'info');
                }
            } catch (error) {
                const status = error?.response?.status;
                const detail = error?.response?.data?.detail || error?.message || 'Unknown error';
                console.error('Error saving emission to API:', status, detail, error);
                if (status === 401 || status === 403) {
                    this.showNotification('Authorization failed while saving. Please log in again or use a valid session.', 'error');
                } else if (status) {
                    this.showNotification(`Save failed (${status}): ${detail}`, 'error');
                } else {
                    console.log('📡 API not available, adding locally (session preserved)');
                }
                
                const emissionData = {
                    category: this.emissionForm.category,
                    activity: this.emissionForm.activity || this.emissionForm.category,
                    amount: parseFloat(this.emissionForm.amount),
                    unit: this.emissionForm.unit || 'kg',
                    date: this.emissionForm.date,
                    description: this.emissionForm.description
                };
                
                this.addEmissionLocally(emissionData);
                if (!status) {
                    this.showNotification('Emission added locally (API unavailable)', 'info');
                }
            } finally {
                // Reset form
                this.emissionForm = {
                    category: '',
                    activity: '',
                    amount: '',
                    unit: '',
                    date: new Date().toISOString().split('T')[0],
                    description: ''
                };
                
                this.loading = false;
                this.updateChart();
            }
        },
        
        addEmissionLocally(emissionData) {
            const newEmission = {
                id: Date.now().toString(),
                ...emissionData
            };
            
            this.emissions.unshift(newEmission);
            this.totalEmissions += newEmission.amount;
            this.monthlyEmissions += newEmission.amount;
            
            // Update goal progress
            this.goalProgress = Math.min(Math.round((this.monthlyEmissions / 300) * 100), 100);
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
        prepareChartData() {
            // Group emissions by date and sum CO2
            const emissionsByDate = {};
            
            this.emissions.forEach(emission => {
                const date = emission.date;
                if (!emissionsByDate[date]) {
                    emissionsByDate[date] = 0;
                }
                emissionsByDate[date] += emission.co2_equivalent || emission.amount || 0;
            });
            
            // Sort dates and prepare labels and data
            const dates = Object.keys(emissionsByDate).sort();
            const labels = dates.map(date => {
                const d = new Date(date);
                return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            });
            const data = dates.map(date => Math.round(emissionsByDate[date] * 10) / 10);
            
            // If no data, return some default data
            if (labels.length === 0) {
                return {
                    labels: ['Sep 18', 'Sep 19', 'Sep 20', 'Sep 21', 'Sep 22', 'Sep 23', 'Sep 24', 'Sep 25'],
                    data: [23.5, 15.2, 45.6, 8.7, 12.1, 45.2, 25.4, 150.5]
                };
            }
            
            return { labels, data };
        },
        
        initializeChart() {
            if (typeof Chart === 'undefined') {
                console.warn('Chart.js not loaded, skipping chart initialization');
                return;
            }
            
            setTimeout(() => {
                const ctx = document.getElementById('emissionsChart');
                if (ctx && !this.chart) {
                    // Prepare chart data from emissions
                    const chartData = this.prepareChartData();
                    
                    this.chart = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: chartData.labels,
                            datasets: [{
                                label: 'Daily CO₂ Emissions (kg)',
                                data: chartData.data,
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
            }, 100);
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
                    // Use co2_equivalent if available, otherwise fall back to amount
                    chartData.push(emission.co2_equivalent || emission.amount);
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
            
            // Auto-remove notification - longer for success messages
            const timeout = type === 'success' ? 10000 : 5000;
            setTimeout(function() {
                this.removeNotification(notification.id);
            }.bind(this), timeout);
        },

        removeNotification(id) {
            const index = this.notifications.findIndex(function(n) { return n.id === id; });
            if (index !== -1) {
                this.notifications.splice(index, 1);
            }
        },

        clearAllNotifications() {
            this.notifications = [];
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
                // Use mock data for demo mode (no backend)
                if (this.userProfile.user_id === 'demo-user' || this.userProfile.user_id === 'admin-user') {
                    // Mock recommendations data
                    const mockRecommendations = [
                        {
                            id: 'rec_001',
                            title: 'Switch to Public Transportation',
                            description: 'Using public transport for your daily commute could reduce your carbon footprint by 65%',
                            category: 'transportation',
                            impact_level: 'high',
                            effort_level: 'medium',
                            potential_savings_kg: 45.2,
                            implementation_tips: ['Check local bus and train schedules', 'Consider monthly passes for savings', 'Combine with walking or cycling'],
                            estimated_cost_impact: 'save',
                            timeframe: 'immediate'
                        },
                        {
                            id: 'rec_002',
                            title: 'Reduce Meat Consumption',
                            description: 'Replacing 2 meat meals per week with plant-based alternatives can significantly lower food-related emissions',
                            category: 'food',
                            impact_level: 'high',
                            effort_level: 'easy',
                            potential_savings_kg: 28.7,
                            implementation_tips: ['Try Meatless Monday', 'Explore plant-based protein sources', 'Start with familiar vegetables'],
                            estimated_cost_impact: 'save',
                            timeframe: 'immediate'
                        },
                        {
                            id: 'rec_003',
                            title: 'Optimize Home Heating',
                            description: 'Lowering your thermostat by 2°C and improving insulation can reduce energy consumption',
                            category: 'energy',
                            impact_level: 'medium',
                            effort_level: 'easy',
                            potential_savings_kg: 18.5,
                            implementation_tips: ['Use programmable thermostat', 'Seal windows and doors', 'Add weather stripping'],
                            estimated_cost_impact: 'save',
                            timeframe: 'immediate'
                        },
                        {
                            id: 'rec_004',
                            title: 'Choose Renewable Energy',
                            description: 'Switching to a renewable energy provider can eliminate home energy emissions',
                            category: 'energy',
                            impact_level: 'very_high',
                            effort_level: 'medium',
                            potential_savings_kg: 95.3,
                            implementation_tips: ['Research local green energy providers', 'Compare pricing plans', 'Consider solar panel installation'],
                            estimated_cost_impact: 'neutral',
                            timeframe: '1-3_months'
                        },
                        {
                            id: 'rec_005',
                            title: 'Reduce Air Travel',
                            description: 'Consider video calls instead of business trips, or choose direct flights when traveling',
                            category: 'transportation',
                            impact_level: 'very_high',
                            effort_level: 'medium',
                            potential_savings_kg: 156.8,
                            implementation_tips: ['Use video conferencing tools', 'Plan combined trips', 'Choose direct flights'],
                            estimated_cost_impact: 'save',
                            timeframe: 'immediate'
                        }
                    ];
                    
                    this.recommendations = mockRecommendations;
                    
                    // Update recommendation stats
                    this.recommendationStats = {
                        totalRecommendations: mockRecommendations.length,
                        potentialSavings: mockRecommendations.reduce((sum, rec) => sum + rec.potential_savings_kg, 0),
                        quickWins: mockRecommendations.filter(rec => rec.effort_level === 'easy').length,
                        highImpact: mockRecommendations.filter(rec => rec.impact_level === 'high' || rec.impact_level === 'very_high').length
                    };
                    
                    console.log('✅ Loaded mock recommendations for demo user');
                    this.loading = false;
                    return;
                }
                
                // Original API call for real backend
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
                // Only show error for non-demo users
                if (this.userProfile.user_id !== 'demo-user' && this.userProfile.user_id !== 'admin-user') {
                    this.showNotification('Failed to load recommendations', 'error');
                } else {
                    console.log('API not available - using demo mode');
                }
            } finally {
                this.loading = false;
            }
        },
        
        async loadRecommendationStats() {
            if (!this.isAuthenticated) return;
            
            try {
                // Use mock data for demo users
                if (this.userProfile.user_id === 'demo-user' || this.userProfile.user_id === 'admin-user') {
                    // Stats are handled in loadRecommendations for demo users
                    return;
                }
                
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
                // Use mock data for demo users
                if (this.userProfile.user_id === 'demo-user' || this.userProfile.user_id === 'admin-user') {
                    // Mock gamification profile
                    this.gamificationProfile = {
                        level: {
                            current_level: {
                                level: 3,
                                name: 'Eco Enthusiast',
                                icon: '🌱',
                                min_points: 500,
                                max_points: 1000
                            },
                            progress_to_next: 65
                        },
                        total_points: 825,
                        streak: {
                            current_streak: 12,
                            longest_streak: 18,
                            streak_type: 'daily_logging'
                        }
                    };
                    
                    // Mock recent achievements
                    this.recentAchievements = [
                        {
                            id: 'first_steps',
                            title: 'First Steps',
                            description: 'Complete your profile and log first activity',
                            icon: '👣',
                            points: 50,
                            earned_at: '2025-09-28T10:00:00Z',
                            category: 'onboarding'
                        },
                        {
                            id: 'weekly_warrior',
                            title: 'Weekly Warrior',
                            description: 'Log activities for 7 consecutive days',
                            icon: '🏆',
                            points: 100,
                            earned_at: '2025-09-25T15:30:00Z',
                            category: 'consistency'
                        },
                        {
                            id: 'carbon_saver',
                            title: 'Carbon Saver',
                            description: 'Reduce emissions by 50kg CO2 in a month',
                            icon: '🌍',
                            points: 200,
                            earned_at: '2025-09-20T09:15:00Z',
                            category: 'impact'
                        }
                    ];
                    
                    // Mock gamification stats
                    this.gamificationStats = {
                        achievements_earned: 8,
                        total_activities: 45,
                        carbon_saved_kg: 127.5,
                        goals_achieved: 3
                    };
                    
                    console.log('✅ Loaded mock gamification data for demo user');
                    this.loading = false;
                    return;
                }
                
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
                // Only show error for non-demo users
                if (this.userProfile.user_id !== 'demo-user' && this.userProfile.user_id !== 'admin-user') {
                    this.showNotification('Failed to load achievements data', 'error');
                } else {
                    console.log('API not available - using demo mode');
                }
            } finally {
                this.loading = false;
            }
        },
        
        async loadAchievements() {
            if (!this.isAuthenticated) return;
            
            try {
                // Use mock data for demo users
                if (this.userProfile.user_id === 'demo-user' || this.userProfile.user_id === 'admin-user') {
                    // Mock achievements data
                    const earnedAchievements = [
                        {
                            id: 'first_steps',
                            title: 'First Steps',
                            description: 'Complete your profile and log first activity',
                            icon: '👣',
                            points: 50,
                            earned_at: '2025-09-28T10:00:00Z',
                            category: 'onboarding',
                            status: 'earned'
                        },
                        {
                            id: 'weekly_warrior',
                            title: 'Weekly Warrior',
                            description: 'Log activities for 7 consecutive days',
                            icon: '🏆',
                            points: 100,
                            earned_at: '2025-09-25T15:30:00Z',
                            category: 'consistency',
                            status: 'earned'
                        },
                        {
                            id: 'carbon_saver',
                            title: 'Carbon Saver',
                            description: 'Reduce emissions by 50kg CO2 in a month',
                            icon: '🌍',
                            points: 200,
                            earned_at: '2025-09-20T09:15:00Z',
                            category: 'impact',
                            status: 'earned'
                        }
                    ];
                    
                    const progressAchievements = [
                        {
                            id: 'daily_tracker',
                            title: 'Daily Tracker',
                            description: 'Log activities for 30 consecutive days',
                            icon: '📅',
                            points: 300,
                            category: 'consistency',
                            status: 'in_progress',
                            progress: 12,
                            target: 30
                        },
                        {
                            id: 'eco_champion',
                            title: 'Eco Champion',
                            description: 'Reduce emissions by 200kg CO2 total',
                            icon: '🌟',
                            points: 500,
                            category: 'impact',
                            status: 'in_progress',
                            progress: 127.5,
                            target: 200
                        },
                        {
                            id: 'transport_hero',
                            title: 'Transport Hero',
                            description: 'Use sustainable transport 20 times',
                            icon: '🚆',
                            points: 150,
                            category: 'transportation',
                            status: 'available',
                            progress: 0,
                            target: 20
                        }
                    ];
                    
                    this.allAchievements = [...earnedAchievements, ...progressAchievements];
                    console.log('✅ Loaded mock achievements for demo user');
                    return;
                }
                
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
                console.log('API not available - using demo mode');
            }
        },
        
        async loadLeaderboards() {
            if (!this.isAuthenticated) return;
            
            try {
                // Use mock data for demo users
                if (this.userProfile.user_id === 'demo-user' || this.userProfile.user_id === 'admin-user') {
                    // Mock leaderboard data
                    this.leaderboards = [
                        {
                            period: 'weekly',
                            entries: [
                                {
                                    rank: 1,
                                    user: { name: 'Sarah Chen', avatar_url: null },
                                    points: 450,
                                    co2_reduction: 23.5
                                },
                                {
                                    rank: 2,
                                    user: { name: 'Demo User', avatar_url: null },
                                    points: 350,
                                    co2_reduction: 18.2
                                },
                                {
                                    rank: 3,
                                    user: { name: 'Mike Johnson', avatar_url: null },
                                    points: 280,
                                    co2_reduction: 15.8
                                }
                            ]
                        },
                        {
                            period: 'monthly',
                            entries: [
                                {
                                    rank: 1,
                                    user: { name: 'Emma Wilson', avatar_url: null },
                                    points: 1250,
                                    co2_reduction: 67.3
                                },
                                {
                                    rank: 2,
                                    user: { name: 'Alex Rodriguez', avatar_url: null },
                                    points: 980,
                                    co2_reduction: 52.1
                                },
                                {
                                    rank: 3,
                                    user: { name: 'Demo User', avatar_url: null },
                                    points: 825,
                                    co2_reduction: 42.7
                                }
                            ]
                        }
                    ];
                    console.log('✅ Loaded mock leaderboards for demo user');
                    return;
                }
                
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
                console.log('API not available - using demo mode');
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
            console.log('Registration attempt for:', this.registerForm.email);
            
            if (!this.isRegistrationValid) {
                this.showNotification('Please fill in all required fields correctly', 'error');
                return;
            }
            
            this.loading = true;
            try {
                const registrationData = {
                    full_name: `${this.registerForm.firstName} ${this.registerForm.lastName}`.trim(),
                    email: this.registerForm.email,
                    password: this.registerForm.password,
                    carbon_budget: 500.0
                };
                
                // Make API call for registration
                const response = await axios.post(`${this.apiBase}/api/v1/auth/register`, registrationData, {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response && response.status >= 200 && response.status < 300) {
                    console.log('✅ Registration successful via API');
                    const msg = (response.data && (response.data.message || response.data.status))
                      ? `🎉 ${response.data.message || 'Registration successful.'}`
                      : '🎉 Registration Successful! Your account request has been submitted for admin approval. You will be notified once approved.';
                    this.showNotification(msg, 'success');
                    // Switch to login view after a short delay
                    setTimeout(() => {
                        this.currentView = 'login';
                        this.loginForm.email = this.registerForm.email;
                    }, 1500);
                } else {
                    console.log('❌ API registration returned unexpected response, using local simulation');
                    this.handleLocalRegistration();
                }
            } catch (error) {
                console.error('Error during API registration:', error);
                const status = error?.response?.status;
                if (status === 409) {
                    this.showNotification('An account with this email already exists. Please log in or use a different email.', 'error');
                    this.currentView = 'login';
                    this.loginForm.email = this.registerForm.email;
                } else if (status === 400) {
                    const detail = error?.response?.data?.detail || 'Invalid input. Please check the form.';
                    this.showNotification(detail, 'error');
                } else {
                    console.log('📡 API not available, using local simulation');
                    this.handleLocalRegistration();
                }
            } finally {
                // Reset form but stay on registration page to see success
                this.registerForm = {
                    firstName: '',
                    lastName: '',
                    email: '',
                    password: '',
                    confirmPassword: '',
                    organization: '',
                    acceptTerms: false
                };
                
                this.loading = false;
            }
        },
        
        handleLocalRegistration() {
            // Fallback local registration when API is not available
            const newUser = {
                id: `pending_${Date.now()}`,
                firstName: this.registerForm.firstName,
                lastName: this.registerForm.lastName,
                email: this.registerForm.email,
                organization: this.registerForm.organization || null,
                registeredAt: new Date().toISOString()
            };
            
            // Add to pending users list
            this.pendingUsers.push(newUser);
            
            // Update admin stats
            this.adminStats.pendingRegistrations++;
            
            console.log('✅ Local registration successful for:', newUser.email);
            console.log('User can login after admin approval with password: password123');
            
            this.showNotification(
                '🎉 Registration Successful! Your account request has been submitted for admin approval. You will be able to login once approved.',
                'success'
            );
        },
        
        // Admin Methods
        // Admin data loading methods
        async loadAdminData() {
            if (this.userProfile.role !== 'admin') return;
            
            await Promise.all([
                this.loadPendingUsers(),
                this.loadAllUsers(),
                this.loadAdminStats()
            ]);
        },
        
        async loadPendingUsers() {
            try {
                console.log('Loading pending users...');
                const response = await axios.get(`${this.apiBase}/api/admin/pending-users`, {
                    headers: {
                        'Authorization': `Bearer ${this.authToken}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                console.log('Pending users response:', response.data);
                
                if (response.data && response.data.success) {
                    this.pendingUsers = response.data.pending_users.map(user => ({
                        id: user.user_id,
                        user_id: user.user_id,
                        firstName: user.full_name.split(' ')[0] || '',
                        lastName: user.full_name.split(' ').slice(1).join(' ') || '',
                        full_name: user.full_name,
                        email: user.email,
                        registeredAt: user.created_at,
                        role: user.role
                    }));
                    console.log('✅ Loaded pending users:', this.pendingUsers.length);
                    console.log('Pending users data:', this.pendingUsers);
                } else {
                    console.error('Unexpected response format:', response.data);
                }
            } catch (error) {
                console.error('Error loading pending users:', error);
                console.error('Error details:', error.response?.data);
                this.showNotification('Failed to load pending users', 'error');
            }
        },
        
        async loadAllUsers() {
            try {
                console.log('Loading all users...');
                const response = await axios.get(`${this.apiBase}/api/admin/users`, {
                    headers: {
                        'Authorization': `Bearer ${this.authToken}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                console.log('All users response:', response.data);
                
                if (response.data && response.data.success) {
                    this.allUsers = response.data.users.map(user => ({
                        id: user.user_id,
                        user_id: user.user_id,
                        name: user.full_name,
                        email: user.email,
                        status: user.status,
                        role: user.role,
                        lastActive: user.last_active,
                        totalEmissions: user.total_emissions,
                        entriesCount: user.entries_count
                    }));
                    console.log('✅ Loaded all users:', this.allUsers.length);
                    console.log('Users data:', this.allUsers);
                } else {
                    console.error('Unexpected response format:', response.data);
                }
            } catch (error) {
                console.error('Error loading all users:', error);
                console.error('Error details:', error.response?.data);
                this.showNotification('Failed to load users', 'error');
            }
        },
        
        async loadAdminStats() {
            try {
                const response = await axios.get(`${this.apiBase}/api/admin/stats`, {
                    headers: {
                        'Authorization': `Bearer ${this.authToken}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.data.success) {
                    this.adminStats = {
                        totalUsers: response.data.stats.total_users,
                        pendingRegistrations: response.data.stats.pending_registrations,
                        activeThisMonth: response.data.stats.active_this_month,
                        totalCarbonTracked: response.data.stats.total_carbon_tracked
                    };
                    console.log('✅ Loaded admin stats:', this.adminStats);
                }
            } catch (error) {
                console.error('Error loading admin stats:', error);
            }
        },
        
        async approveUser(userId) {
            try {
                console.log('Approving user:', userId);
                const response = await axios.post(
                    `${this.apiBase}/api/admin/users/${userId}/approve`, 
                    {},
                    {
                        headers: {
                            'Authorization': `Bearer ${this.authToken}`,
                            'Content-Type': 'application/json'
                        }
                    }
                );
                
                console.log('Approve response:', response);
                console.log('Approve response data:', response.data);
                
                // Check if approval was successful (response.data.success or just a 200 status)
                if (response.status === 200 || (response.data && response.data.success)) {
                    this.showNotification('✅ User approved successfully!', 'success');
                    // Reload data
                    await this.loadAdminData();
                } else {
                    console.error('Unexpected response structure:', response);
                    this.showNotification('Unexpected response from server', 'error');
                }
            } catch (error) {
                console.error('Error approving user:', error);
                console.error('Error details:', error.response?.data);
                console.error('Error status:', error.response?.status);
                
                // Check if it actually succeeded despite the error
                if (error.response && error.response.status === 200) {
                    this.showNotification('✅ User approved successfully!', 'success');
                    await this.loadAdminData();
                } else {
                    this.showNotification('Failed to approve user: ' + (error.response?.data?.detail || error.message), 'error');
                }
            }
        },
        
        async rejectUser(userId) {
            try {
                const response = await axios.delete(
                    `${this.apiBase}/api/admin/users/${userId}`,
                    {
                        headers: {
                            'Authorization': `Bearer ${this.authToken}`,
                            'Content-Type': 'application/json'
                        }
                    }
                );
                
                console.log('Reject response:', response.data);
                
                // Check if deletion was successful (response.data.success or just a 200 status)
                if (response.status === 200 || response.data.success) {
                    this.showNotification('✅ User rejected and removed', 'success');
                    // Reload data
                    await this.loadAdminData();
                } else {
                    this.showNotification('Failed to reject user', 'error');
                }
            } catch (error) {
                console.error('Error rejecting user:', error);
                console.error('Error response:', error.response?.data);
                // Check if it's actually successful despite the error
                if (error.response && error.response.status === 200) {
                    this.showNotification('✅ User rejected and removed', 'success');
                    await this.loadAdminData();
                } else {
                    this.showNotification('Failed to reject user', 'error');
                }
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