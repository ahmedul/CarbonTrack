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
            apiBase: 'https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1',
            
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
        console.log('=== Vue app mounting ===');
        console.log('API Base URL:', this.apiBase);
        
        // Check for stored authentication (sync - don't use await in mounted)
        const token = localStorage.getItem('carbontrack_token');
        console.log('Token in localStorage:', token ? 'Yes (length: ' + token.length + ')' : 'No');
        
        if (token) {
            console.log('Found stored token, attempting to restore session...');
            this.authToken = token;
            this.isAuthenticated = true;
            
            // Load user data first, then load other data
            this.loadUserData().then(() => {
                console.log('User data loaded, profile:', this.userProfile);
                
                // Only load other data if still authenticated (token wasn't expired)
                if (this.isAuthenticated && this.userProfile.user_id) {
                    console.log('Loading emissions and other data...');
                    this.loadEmissions();
                    this.loadRecommendations();
                    this.loadRecommendationStats();
                } else {
                    console.log('Not authenticated or no user_id after loadUserData');
                }
            }).catch(error => {
                console.error('Error loading user data:', error);
                // Continue anyway - error is handled in loadUserData
            });
        } else {
            console.log('No token found, showing welcome screen');
            this.currentView = 'welcome';
        }
        
        // Always try to initialize chart (it has its own error handling)
        setTimeout(() => {
            try {
                this.initializeChart();
            } catch (chartError) {
                console.error('Chart initialization error (non-fatal):', chartError);
            }
        }, 500);
        
        console.log('=== Vue app mounted successfully ===');
    },
    
    methods: {
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
                
                const response = await axios.post(`${this.apiBase}/auth/login`, loginData, {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                // Check if we got an access_token (new API format)
                if (response.data.access_token) {
                    console.log('✅ Login successful via API');
                    this.authToken = response.data.access_token;
                    localStorage.setItem('carbontrack_token', response.data.access_token);
                    
                    // Fetch user profile
                    const profileResponse = await axios.get(`${this.apiBase}/auth/me`, {
                        headers: {
                            'Authorization': `Bearer ${this.authToken}`
                        }
                    });
                    
                    if (profileResponse.data.user) {
                        this.userProfile = {
                            user_id: profileResponse.data.user.user_id,
                            email: profileResponse.data.user.email || this.loginForm.email,
                            full_name: profileResponse.data.user.full_name || 'User',
                            carbon_budget: profileResponse.data.user.carbon_budget || 2000,
                            role: profileResponse.data.user.role || 'user'
                        };
                        
                        this.isAuthenticated = true;
                        this.currentView = 'dashboard';
                        
                        // Load data from API
                        this.loadEmissions();
                        this.loadRecommendations();
                        this.loadRecommendationStats();
                        this.loadGamificationData();
                        
                        this.showNotification('Login successful! Welcome to CarbonTrack.', 'success');
                        this.initializeChart();
                        this.loading = false;
                        return;
                    }
                }
                
                // Check old API format for backwards compatibility
                if (response.data.success) {
                    console.log('✅ Login successful via API (old format)');
                    const userData = response.data.data;
                    
                    this.isAuthenticated = true;
                    this.currentView = 'dashboard';
                    this.authToken = userData.token;
                    this.userProfile = {
                        user_id: userData.user_id,
                        email: userData.email,
                        full_name: userData.full_name,
                        carbon_budget: userData.carbon_budget || 500,
                        role: userData.role || 'user'
                    };
                    localStorage.setItem('carbontrack_token', userData.token);
                    
                    // Load data from API
                    this.loadEmissions();
                    this.loadRecommendations();
                    this.loadRecommendationStats();
                    this.loadGamificationData();
                    
                    this.showNotification('Login successful! Welcome to CarbonTrack.', 'success');
                    this.initializeChart();
                    this.loading = false;
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
            } else if (this.loginForm.email === 'ahmedulkabir55@gmail.com' && this.loginForm.password === '*king*55') {
                // Admin user login
                console.log('✅ Admin credentials matched!');
                this.isAuthenticated = true;
                this.currentView = 'dashboard';
                this.userProfile = {
                    user_id: 'admin-user',
                    email: this.loginForm.email,
                    full_name: 'Ahmed Ul Kabir',
                    carbon_budget: 500,
                    role: 'admin'  // Full admin access
                };
                localStorage.setItem('carbontrack_token', 'admin-token-123');
                
                // Load initial sample data
                this.loadEmissions();
                this.loadRecommendations();
                this.loadRecommendationStats();
                this.loadGamificationData();
                
                this.showNotification('Welcome back, Admin! You have full access to all features.', 'success');
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
        async loadUserData() {
            console.log('Loading user profile data');
            
            if (!this.authToken) {
                console.log('No auth token, skipping profile load');
                return;
            }
            
            try {
                console.log('Fetching user profile from API...');
                const response = await axios.get(`${this.apiBase}/auth/me`, {
                    headers: {
                        'Authorization': `Bearer ${this.authToken}`
                    }
                });
                
                console.log('API /me response:', response.data);
                
                if (response.data.user) {
                    console.log('✅ User profile loaded:', response.data.user);
                    this.userProfile = {
                        user_id: response.data.user.user_id,
                        email: response.data.user.email,
                        full_name: response.data.user.full_name || 'User',
                        carbon_budget: response.data.user.carbon_budget || 2000,
                        role: response.data.user.role || 'user'
                    };
                } else {
                    console.error('Invalid response format from /me endpoint');
                    throw new Error('Invalid response format');
                }
            } catch (error) {
                console.error('Failed to load user profile:', error);
                console.error('Error details:', error.response?.data || error.message);
                
                // Token is invalid or expired - force logout
                console.log('🔴 Token invalid/expired, forcing logout');
                localStorage.removeItem('carbontrack_token');
                this.authToken = null;
                this.isAuthenticated = false;
                this.currentView = 'welcome';
                this.showNotification('Session expired. Please login again.', 'error');
            }
        },
        
        async loadEmissions() {
            console.log('=== LOAD EMISSIONS START ===');
            console.log('Auth token:', this.authToken ? 'Present (length: ' + this.authToken.length + ')' : 'MISSING');
            console.log('User ID:', this.userProfile?.user_id);
            console.log('API Base:', this.apiBase);
            
            this.loading = true;
            
            try {
                // Make API call to load user's emissions
                const url = `${this.apiBase}/carbon-emissions`;
                console.log('Fetching emissions from:', url);
                
                const response = await axios.get(url, {
                    headers: {
                        'Authorization': `Bearer ${this.authToken}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                console.log('✅ API Response received');
                console.log('Response status:', response.status);
                console.log('Response data type:', Array.isArray(response.data) ? 'Array' : typeof response.data);
                console.log('Response data length:', Array.isArray(response.data) ? response.data.length : 'N/A');
                console.log('Raw API response:', response.data);
                
                // Check if we got emissions array (backend returns array directly)
                if (response.data && Array.isArray(response.data)) {
                    console.log('✅ Successfully loaded', response.data.length, 'emissions from API');
                    
                    // Map backend format to frontend format
                    // Backend now returns entries sorted by created_at (newest first)
                    this.emissions = response.data.map(emission => ({
                        id: emission.id,
                        category: emission.entry_type,
                        activity: emission.category || emission.entry_type,
                        amount: emission.co2_equivalent || emission.amount,
                        unit: emission.unit,
                        date: emission.date.split('T')[0],
                        created_at: emission.created_at || emission.id,  // Use created_at timestamp for sorting
                        description: emission.description || '',
                        co2_equivalent: emission.co2_equivalent
                    }));
                    
                    console.log('Mapped emissions:', this.emissions);
                    
                    // Calculate totals from actual data
                    this.totalEmissions = this.emissions.reduce((sum, e) => sum + parseFloat(e.amount || 0), 0);
                    
                    // Calculate monthly emissions (current month)
                    const currentMonth = new Date().toISOString().slice(0, 7);
                    this.monthlyEmissions = this.emissions
                        .filter(e => e.date.startsWith(currentMonth))
                        .reduce((sum, e) => sum + parseFloat(e.amount || 0), 0);
                    
                    this.goalProgress = Math.min(Math.round((this.monthlyEmissions / 300) * 100), 100);
                    
                    console.log('✅ Totals calculated:');
                    console.log('  - Total emissions:', this.totalEmissions, 'kg');
                    console.log('  - Monthly emissions:', this.monthlyEmissions, 'kg');
                    console.log('  - Goal progress:', this.goalProgress, '%');
                    console.log('=== LOAD EMISSIONS SUCCESS ===');
                    
                } else {
                    // Empty array or unexpected format - don't load demo data, just start fresh
                    console.log('⚠️ No emissions found or unexpected format');
                    this.emissions = [];
                    this.totalEmissions = 0;
                    this.monthlyEmissions = 0;
                    this.goalProgress = 0;
                    console.log('=== LOAD EMISSIONS COMPLETE (EMPTY) ===');
                }
            } catch (error) {
                console.error('❌ Error loading emissions from API:', error);
                console.error('Error response:', error.response?.data);
                console.error('Error status:', error.response?.status);
                
                // On error, start fresh - NEVER load demo data for authenticated users
                if (this.authToken) {
                    console.log('⚠️ API error for authenticated user - starting with empty data (NOT DEMO)');
                    this.emissions = [];
                    this.totalEmissions = 0;
                    this.monthlyEmissions = 0;
                    this.goalProgress = 0;
                } else {
                    console.log('📡 No auth token - using demo data for demo users');
                    this.loadDemoEmissions();
                }
                console.log('=== LOAD EMISSIONS FAILED ===');
            } finally {
                this.loading = false;
            }
        },
        
        loadDemoEmissions() {
            console.log('Loading demo emissions data as fallback');
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
        async addEmission() {
            if (!this.emissionForm.category || !this.emissionForm.amount) {
                this.showNotification('Please fill in all required fields', 'error');
                return;
            }
            
            // Check if user is authenticated
            if (!this.authToken) {
                this.showNotification('Please log in first', 'error');
                this.currentView = 'login';
                return;
            }
            
            try {
                // Prepare emission data for API
                const emissionData = {
                    entry_type: this.emissionForm.category,
                    category: this.emissionForm.activity || this.emissionForm.category,
                    amount: parseFloat(this.emissionForm.amount),
                    unit: this.emissionForm.unit || 'kg',
                    date: this.emissionForm.date + 'T12:00:00',  // Add time to date
                    description: this.emissionForm.description || ''
                };
                
                console.log('Sending emission data to API:', emissionData);
                console.log('Auth token present:', !!this.authToken);
                console.log('Auth token length:', this.authToken?.length);
                
                // Save to API
                const response = await axios.post(
                    `${this.apiBase}/carbon-emissions`,
                    emissionData,
                    {
                        headers: {
                            'Authorization': `Bearer ${this.authToken}`,
                            'Content-Type': 'application/json'
                        }
                    }
                );
                
                console.log('API response:', response.data);
                
                // Add to local list with API response data
                const newEmission = {
                    id: response.data.id,
                    category: response.data.entry_type,
                    activity: response.data.category || response.data.entry_type,
                    amount: response.data.co2_equivalent || response.data.amount,
                    unit: response.data.unit,
                    date: response.data.date.split('T')[0],
                    description: response.data.description || '',
                    co2_equivalent: response.data.co2_equivalent
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
                
                this.showNotification(`Carbon emission added successfully! CO2: ${newEmission.amount.toFixed(2)} kg`, 'success');
                this.updateChart();
                
            } catch (error) {
                console.error('Error saving emission:', error);
                console.error('Error details:', error.response?.data || error.message);
                const errorMsg = error.response?.data?.detail || 'Failed to save emission. Please try again.';
                this.showNotification(errorMsg, 'error');
            }
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
            
            const self = this;
            setTimeout(() => {
                const ctx = document.getElementById('emissionsChart');
                if (ctx && !self.chart) {
                    self.chart = new Chart(ctx, {
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
            }, 100);
        },
        
        updateChart() {
            try {
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
            } catch (error) {
                console.log('Chart update skipped:', error.message);
                // Chart not initialized yet, that's okay
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
            setTimeout(() => {
                this.removeNotification(notification.id);
            }, timeout);
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
                // Use mock data for all users until API endpoints are implemented
                // TODO: Replace with real API calls when /recommendations endpoint is ready
                if (true) {
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
                            description: 'Lowering thermostat by 2°C and improving insulation can reduce heating emissions by 30%',
                            category: 'energy',
                            impact_level: 'medium',
                            effort_level: 'medium',
                            potential_savings_kg: 35.8,
                            implementation_tips: ['Seal windows and doors', 'Use programmable thermostat', 'Wear warmer clothes indoors'],
                            estimated_cost_impact: 'save',
                            timeframe: 'short_term'
                        },
                        {
                            id: 'rec_004',
                            title: 'LED Light Conversion',
                            description: 'Replace remaining incandescent bulbs with LED alternatives for immediate energy savings',
                            category: 'energy',
                            impact_level: 'low',
                            effort_level: 'easy',
                            potential_savings_kg: 12.4,
                            implementation_tips: ['Start with most-used rooms', 'Check for utility rebates', 'Choose warm white for comfort'],
                            estimated_cost_impact: 'save',
                            timeframe: 'immediate'
                        },
                        {
                            id: 'rec_005',
                            title: 'Work From Home Strategy',
                            description: 'Negotiate remote work 2-3 days per week to reduce commuting emissions',
                            category: 'transportation',
                            impact_level: 'high',
                            effort_level: 'medium',
                            potential_savings_kg: 52.1,
                            implementation_tips: ['Propose trial period', 'Show productivity metrics', 'Set up efficient home office'],
                            estimated_cost_impact: 'save',
                            timeframe: 'short_term'
                        }
                    ];
                    
                    this.recommendations = mockRecommendations;
                    
                    // Mock stats for demo
                    this.updateRecommendationStats({
                        weekly_recommendations: mockRecommendations.slice(0, 3),
                        stats: {
                            total_recommendations: mockRecommendations.length,
                            implemented_count: 2,
                            potential_monthly_savings: 174.2,
                            categories: {
                                transportation: 2,
                                energy: 2,
                                food: 1
                            }
                        }
                    });
                    return;
                }

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
                }
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
                // Use mock data for all users until API endpoints are implemented
                // TODO: Replace with real API calls when /gamification endpoint is ready
                if (true) {
                    // Mock gamification profile data
                    this.gamificationProfile = {
                        user_id: this.userProfile.user_id,
                        total_points: 1250,
                        level: 8,
                        level_name: 'Eco Warrior',
                        next_level_threshold: 1500,
                        achievements_unlocked: 12,
                        carbon_saved_total_kg: 187.5,
                        streak_days: 23,
                        rank: 15
                    };
                    
                    this.recentAchievements = [
                        {
                            id: 'ach_001',
                            name: 'First Steps',
                            description: 'Logged your first carbon entry',
                            icon: '🌱',
                            points: 50,
                            unlocked_date: '2025-09-28T10:30:00Z'
                        },
                        {
                            id: 'ach_002',  
                            name: 'Week Warrior',
                            description: 'Tracked emissions for 7 consecutive days',
                            icon: '📅',
                            points: 100,
                            unlocked_date: '2025-09-25T14:20:00Z'
                        }
                    ];
                    
                    this.activeChallenges = [
                        {
                            id: 'ch_001',
                            name: 'Carbon Diet Challenge',
                            description: 'Reduce food-related emissions by 20% this month',
                            progress: 65,
                            target: 100,
                            reward_points: 200,
                            end_date: '2025-10-31T23:59:59Z'
                        }
                    ];
                    
                    this.gamificationStats = {
                        weekly_points: 180,
                        monthly_points: 720,
                        achievements_this_month: 3,
                        challenges_completed: 2
                    };
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
                }
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
            console.log('Registration attempt for:', this.registerForm.email);
            
            if (!this.isRegistrationValid) {
                this.showNotification('Please fill in all required fields correctly', 'error');
                return;
            }
            
            this.loading = true;
            try {
                // Simulate API call for registration
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                // Add user to pending registrations list
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
                
                console.log('✅ Registration successful for:', newUser.email);
                
                this.showNotification(
                    '🎉 Registration Successful! Your account request has been submitted for admin approval. You will be able to login once approved.',
                    'success'
                );
                
                // Also log success details
                console.log('✅ REGISTRATION SUCCESSFUL!');
                console.log('User can login after admin approval with:');
                console.log('Email:', newUser.email);
                console.log('Password: password123 (default)');
                
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
                
                console.log('=== REGISTRATION COMPLETE ===');
                console.log('User should now appear in pending list');
                console.log('Current pending users:', this.pendingUsers);
                console.log('Admin stats:', this.adminStats);
                
                // Stay on registration page to see success message
                // this.currentView = 'login';
                
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
                    
                    // Add to approved users with login credentials
                    const approvedUser = {
                        id: `approved_${Date.now()}`,
                        name: `${user.firstName} ${user.lastName}`,
                        email: user.email,
                        status: 'active',
                        role: 'user',
                        lastActive: new Date().toISOString(),
                        // Store original registration info for reference
                        firstName: user.firstName,
                        lastName: user.lastName,
                        registeredAt: user.registeredAt
                    };
                    
                    this.allUsers.push(approvedUser);
                    
                    console.log('✅ User approved:', user.email, '- can now login with password: password123');
                    
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

// Global error handler to prevent errors from breaking the entire app
app.config.errorHandler = (err, instance, info) => {
    console.error('Vue Error Caught:', err);
    console.error('Component:', instance);
    console.error('Error Info:', info);
    // Log but don't break the app - prevent white screen on errors
    return false;
};

console.log('Vue app created, attempting to mount...');
try {
    app.mount('#app');
    console.log('CarbonTrack Vue app mounted successfully!');
} catch (error) {
    console.error('Error mounting Vue app:', error);
    document.body.innerHTML = '<h1 style="color: red; text-align: center; margin-top: 50px;">Failed to mount Vue app: ' + error.message + '</h1>';
}