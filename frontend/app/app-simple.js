// Simplified CarbonTrack Vue.js Application
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
            currentView: 'login',
            isAuthenticated: false,
            
            // Forms
            loginForm: {
                email: 'demo@carbontrack.dev',
                password: 'password123'
            },
            
            // User data
            userProfile: {
                email: '',
                full_name: 'Demo User'
            }
        };
    },
    
    mounted() {
        console.log('Vue app mounted successfully!');
    },
    
    methods: {
        login() {
            console.log('Login attempt:', this.loginForm);
            
            // Simple demo login
            if (this.loginForm.email && this.loginForm.password) {
                this.isAuthenticated = true;
                this.currentView = 'dashboard';
                this.userProfile.email = this.loginForm.email;
                console.log('Login successful');
            } else {
                alert('Please enter email and password');
            }
        },
        
        logout() {
            console.log('Logging out');
            this.isAuthenticated = false;
            this.currentView = 'login';
            this.loginForm = { email: '', password: '' };
        },
        
        showNotification(message, type) {
            console.log('[' + type + '] ' + message);
            alert(message);
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