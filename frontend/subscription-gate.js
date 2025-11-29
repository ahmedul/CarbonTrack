/**
 * Subscription Gate Component
 * Premium feature paywall with pricing cards
 */

const SubscriptionGate = {
    name: 'SubscriptionGate',
    template: `
        <div class="subscription-gate-overlay" v-if="showGate">
            <div class="subscription-gate">
                <button class="close-btn" @click="closeGate">
                    <i class="fas fa-times"></i>
                </button>
                
                <!-- Header -->
                <div class="gate-header">
                    <div class="lock-icon">
                        <i class="fas fa-lock"></i>
                    </div>
                    <h2>Upgrade to Access CSRD Compliance</h2>
                    <p>Choose a plan that fits your organization's sustainability reporting needs</p>
                </div>

                <!-- Loading State -->
                <div v-if="loading" class="loading-state">
                    <i class="fas fa-spinner fa-spin"></i>
                    <p>Loading subscription plans...</p>
                </div>

                <!-- Error State -->
                <div v-if="error" class="error-state">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>{{ error }}</p>
                    <button @click="loadPlans" class="btn-retry">Try Again</button>
                </div>

                <!-- Pricing Cards -->
                <div v-if="!loading && !error" class="pricing-cards">
                    <!-- Professional Plan -->
                    <div class="pricing-card" :class="{'current-plan': currentTier === 'PROFESSIONAL'}">
                        <div class="card-header professional">
                            <h3>Professional</h3>
                            <div class="price">
                                <span class="currency">$</span>
                                <span class="amount">49</span>
                                <span class="period">/month</span>
                            </div>
                            <p class="target">Small businesses (10-50 employees)</p>
                        </div>
                        <div class="card-body">
                            <ul class="features">
                                <li><i class="fas fa-check"></i> Basic CSRD reporting (single entity)</li>
                                <li><i class="fas fa-check"></i> Scope 1, 2, 3 emissions tracking</li>
                                <li><i class="fas fa-check"></i> Pre-filled CSRD templates</li>
                                <li><i class="fas fa-check"></i> Export to PDF</li>
                                <li><i class="fas fa-check"></i> Email support</li>
                                <li><i class="fas fa-check"></i> Up to 3 team members</li>
                            </ul>
                            <button 
                                class="btn-upgrade" 
                                @click="upgradeTo('PROFESSIONAL')"
                                :disabled="currentTier === 'PROFESSIONAL' || upgrading"
                            >
                                <span v-if="currentTier === 'PROFESSIONAL'">Current Plan</span>
                                <span v-else-if="upgrading === 'PROFESSIONAL'">
                                    <i class="fas fa-spinner fa-spin"></i> Upgrading...
                                </span>
                                <span v-else>Get Started</span>
                            </button>
                        </div>
                    </div>

                    <!-- Business Plan -->
                    <div class="pricing-card popular" :class="{'current-plan': currentTier === 'BUSINESS'}">
                        <div class="popular-badge">Most Popular</div>
                        <div class="card-header business">
                            <h3>Business</h3>
                            <div class="price">
                                <span class="currency">$</span>
                                <span class="amount">149</span>
                                <span class="period">/month</span>
                            </div>
                            <p class="target">Medium businesses (50-500 employees)</p>
                        </div>
                        <div class="card-body">
                            <ul class="features">
                                <li><i class="fas fa-check"></i> <strong>Everything in Professional, PLUS:</strong></li>
                                <li><i class="fas fa-check"></i> Multi-entity reporting (up to 5 entities)</li>
                                <li><i class="fas fa-check"></i> API access for integrations</li>
                                <li><i class="fas fa-check"></i> Custom report templates</li>
                                <li><i class="fas fa-check"></i> Priority email support</li>
                                <li><i class="fas fa-check"></i> Up to 10 team members</li>
                                <li><i class="fas fa-check"></i> Data validation & audit trails</li>
                            </ul>
                            <button 
                                class="btn-upgrade primary" 
                                @click="upgradeTo('BUSINESS')"
                                :disabled="currentTier === 'BUSINESS' || upgrading"
                            >
                                <span v-if="currentTier === 'BUSINESS'">Current Plan</span>
                                <span v-else-if="upgrading === 'BUSINESS'">
                                    <i class="fas fa-spinner fa-spin"></i> Upgrading...
                                </span>
                                <span v-else>Upgrade Now</span>
                            </button>
                        </div>
                    </div>

                    <!-- Enterprise Plan -->
                    <div class="pricing-card" :class="{'current-plan': currentTier === 'ENTERPRISE'}">
                        <div class="card-header enterprise">
                            <h3>Enterprise</h3>
                            <div class="price">
                                <span class="currency">$</span>
                                <span class="amount">499</span>
                                <span class="period">/month</span>
                            </div>
                            <p class="target">Large corporations (500+ employees)</p>
                        </div>
                        <div class="card-body">
                            <ul class="features">
                                <li><i class="fas fa-check"></i> <strong>Everything in Business, PLUS:</strong></li>
                                <li><i class="fas fa-check blockchain"></i> <strong>🔐 Blockchain-verified reports</strong></li>
                                <li><i class="fas fa-check"></i> Unlimited entities & subsidiaries</li>
                                <li><i class="fas fa-check"></i> White-label branding</li>
                                <li><i class="fas fa-check"></i> SSO (Single Sign-On)</li>
                                <li><i class="fas fa-check"></i> Custom integrations (SAP, Oracle, ERP)</li>
                                <li><i class="fas fa-check"></i> Dedicated account manager</li>
                                <li><i class="fas fa-check"></i> 24/7 priority support</li>
                                <li><i class="fas fa-check"></i> Unlimited team members</li>
                            </ul>
                            
                            <!-- Blockchain Badge -->
                            <div class="blockchain-badge">
                                <i class="fas fa-shield-alt"></i>
                                <div>
                                    <strong>Blockchain Verified</strong>
                                    <p>Tamper-proof reports with cryptographic sealing</p>
                                </div>
                            </div>
                            
                            <button 
                                class="btn-upgrade" 
                                @click="upgradeTo('ENTERPRISE')"
                                :disabled="currentTier === 'ENTERPRISE' || upgrading"
                            >
                                <span v-if="currentTier === 'ENTERPRISE'">Current Plan</span>
                                <span v-else-if="upgrading === 'ENTERPRISE'">
                                    <i class="fas fa-spinner fa-spin"></i> Upgrading...
                                </span>
                                <span v-else>Contact Sales</span>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Comparison Footer -->
                <div v-if="!loading && !error" class="comparison-footer">
                    <div class="comparison-item">
                        <i class="fas fa-shield-check"></i>
                        <p><strong>88-98% cheaper</strong> than competitors</p>
                    </div>
                    <div class="comparison-item">
                        <i class="fas fa-clock"></i>
                        <p><strong>Save 50+ hours</strong> per CSRD report</p>
                    </div>
                    <div class="comparison-item">
                        <i class="fas fa-gavel"></i>
                        <p><strong>€1M fine protection</strong> with compliance automation</p>
                    </div>
                    <div class="comparison-item">
                        <i class="fas fa-award"></i>
                        <p><strong>First blockchain CSRD</strong> platform on the market</p>
                    </div>
                </div>

                <!-- Money Back Guarantee -->
                <div v-if="!loading && !error" class="guarantee">
                    <i class="fas fa-hand-holding-usd"></i>
                    <p>30-day money-back guarantee • No credit card required for trial • Cancel anytime</p>
                </div>
            </div>
        </div>
    `,
    props: {
        show: {
            type: Boolean,
            default: false
        },
        requiredTier: {
            type: String,
            default: 'PROFESSIONAL'
        }
    },
    data() {
        return {
            showGate: this.show,
            loading: false,
            error: null,
            plans: [],
            currentTier: 'FREE',
            upgrading: null
        };
    },
    watch: {
        show(newVal) {
            this.showGate = newVal;
            if (newVal) {
                this.loadPlans();
            }
        }
    },
    mounted() {
        if (this.show) {
            this.loadPlans();
        }
    },
    methods: {
        async loadPlans() {
            this.loading = true;
            this.error = null;
            
            try {
                // Get current subscription
                const subResponse = await axios.get(`${API_BASE_URL}/api/v1/subscriptions/me`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });
                this.currentTier = subResponse.data.tier;
                
                // Get available plans
                const plansResponse = await axios.get(`${API_BASE_URL}/api/v1/subscriptions/plans`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });
                this.plans = plansResponse.data.plans;
                
            } catch (err) {
                console.error('Failed to load subscription plans:', err);
                this.error = err.response?.data?.detail || 'Failed to load plans. Please try again.';
            } finally {
                this.loading = false;
            }
        },
        
        async upgradeTo(tier) {
            if (this.upgrading || this.currentTier === tier) {
                return;
            }
            
            this.upgrading = tier;
            
            try {
                // For Enterprise, open contact form
                if (tier === 'ENTERPRISE') {
                    window.open('mailto:sales@carbontrack.com?subject=Enterprise Plan Inquiry', '_blank');
                    this.upgrading = null;
                    return;
                }
                
                // For other tiers, call upgrade API
                const response = await axios.post(
                    `${API_BASE_URL}/api/v1/subscriptions/upgrade`,
                    {
                        tier: tier,
                        payment_method_id: null // TODO: Integrate Stripe
                    },
                    {
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('token')}`
                        }
                    }
                );
                
                // Success - show message and close gate
                alert(`Successfully upgraded to ${tier}! Redirecting to dashboard...`);
                this.currentTier = tier;
                this.closeGate();
                
                // Refresh the page to update access
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
                
            } catch (err) {
                console.error('Upgrade failed:', err);
                const errorMsg = err.response?.data?.detail || 'Upgrade failed. Please try again.';
                alert(errorMsg);
            } finally {
                this.upgrading = null;
            }
        },
        
        closeGate() {
            this.showGate = false;
            this.$emit('close');
        }
    }
};

// Make component globally available
if (typeof window !== 'undefined') {
    window.SubscriptionGate = SubscriptionGate;
}
