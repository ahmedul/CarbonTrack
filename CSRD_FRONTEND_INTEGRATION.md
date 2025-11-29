# CSRD Frontend Integration Guide

## Overview
This guide explains how to integrate the CSRD Compliance Dashboard and Subscription Gate into the main CarbonTrack application.

## New Components

### 1. Subscription Gate (`frontend/subscription-gate.js`)
- **Purpose**: Premium feature paywall with pricing cards
- **Features**:
  - 3 pricing tiers (Professional $49, Business $149, Enterprise $499)
  - Blockchain benefits highlighted in Enterprise tier
  - Responsive design with gradient cards
  - Loading and error states
  - API integration for subscription management

### 2. CSRD Dashboard (`frontend/csrd-dashboard.js`)
- **Purpose**: CSRD compliance reporting interface
- **Features**:
  - Subscription check on mount
  - Automatic paywall display for free users
  - Statistics cards, filters, report listing
  - Create/edit report modals
  - Export to PDF functionality

## Integration Steps

### Step 1: Add Files to HTML
Update your main `index.html` to include the new components:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Existing head content -->
    
    <!-- CSRD Styles -->
    <link rel="stylesheet" href="frontend/csrd-dashboard.css">
    <link rel="stylesheet" href="frontend/subscription-gate.css">
</head>
<body>
    <div id="app">
        <!-- Your existing app content -->
    </div>
    
    <!-- Existing scripts -->
    <script src="https://cdn.jsdelivr.net/npm/vue@3.3.4/dist/vue.global.prod.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    
    <!-- CSRD Components -->
    <script src="frontend/subscription-gate.js"></script>
    <script src="frontend/csrd-dashboard.js"></script>
    <script src="frontend/app.js"></script>
</body>
</html>
```

### Step 2: Register Components in Vue App
Update your main Vue app (`frontend/app.js`):

```javascript
const app = Vue.createApp({
    components: {
        CSRDDashboard: window.CSRDDashboard || CSRDDashboard,
        SubscriptionGate: window.SubscriptionGate
    },
    data() {
        return {
            currentView: 'dashboard',
            // ... other data
        };
    },
    // ... rest of your app
});

app.mount('#app');
```

### Step 3: Add Navigation Menu Item
Add CSRD link to your navigation:

```html
<nav class="sidebar">
    <ul>
        <li><a href="#" @click="currentView = 'dashboard'">Dashboard</a></li>
        <li><a href="#" @click="currentView = 'tracking'">Carbon Tracking</a></li>
        <li><a href="#" @click="currentView = 'csrd'">
            <i class="fas fa-chart-bar"></i> CSRD Compliance
            <span class="premium-badge">PRO</span>
        </a></li>
        <!-- ... other menu items -->
    </ul>
</nav>
```

### Step 4: Add Route Handler
Handle CSRD view in your app:

```javascript
computed: {
    currentComponent() {
        switch (this.currentView) {
            case 'dashboard': return 'Dashboard';
            case 'tracking': return 'CarbonTracking';
            case 'csrd': return 'CSRDDashboard';
            default: return 'Dashboard';
        }
    }
}
```

## Subscription Flow

### How It Works

1. **User navigates to CSRD dashboard**
   - Component calls `checkSubscription()` on mount
   - API: `GET /api/v1/subscriptions/check-feature/csrd`

2. **Free tier user (no access)**
   - Response: `{"has_access": false, "current_tier": "FREE", "required_tier": "PROFESSIONAL"}`
   - Dashboard displays subscription gate overlay
   - Shows 3 pricing cards with features

3. **User clicks upgrade**
   - Professional/Business: Calls `POST /api/v1/subscriptions/upgrade`
   - Enterprise: Opens contact form (mailto:sales@carbontrack.com)

4. **After upgrade**
   - Page reloads
   - Subscription check passes
   - Dashboard loads reports

### API Endpoints Used

```javascript
// Check feature access
GET /api/v1/subscriptions/check-feature/csrd
Headers: Authorization: Bearer <token>
Response: {"has_access": true/false, "current_tier": "...", "required_tier": "..."}

// Get current subscription
GET /api/v1/subscriptions/me
Headers: Authorization: Bearer <token>
Response: {"tier": "FREE", "expires_at": null, "features": {...}}

// Get pricing plans
GET /api/v1/subscriptions/plans
Headers: Authorization: Bearer <token>
Response: {"plans": [{tier, price, features}...]}

// Upgrade subscription
POST /api/v1/subscriptions/upgrade
Headers: Authorization: Bearer <token>
Body: {"tier": "PROFESSIONAL", "payment_method_id": null}
Response: {"message": "Subscription upgraded", "new_tier": "PROFESSIONAL"}
```

## Styling Customization

### Subscription Gate Colors
Edit `frontend/subscription-gate.css`:

```css
/* Professional tier - Blue */
.card-header.professional {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

/* Business tier - Green */
.card-header.business {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

/* Enterprise tier - Purple */
.card-header.enterprise {
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
}
```

### Premium Badge
Add premium badges to menu items:

```css
.premium-badge {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    color: white;
    font-size: 10px;
    padding: 2px 8px;
    border-radius: 12px;
    margin-left: 8px;
    font-weight: 700;
}
```

## Testing

### Test Subscription Gate

1. **As Free User**:
```javascript
// In browser console
localStorage.setItem('token', '<your-test-token>');
// Navigate to CSRD dashboard
// Should see subscription gate
```

2. **Mock API Response** (for testing):
```javascript
// Mock free user
fetch('https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/subscriptions/check-feature/csrd', {
    headers: {'Authorization': 'Bearer <token>'}
})
// Should return: {"has_access": false, "current_tier": "FREE"}
```

3. **Test Upgrade Flow**:
```javascript
// Upgrade to Professional
fetch('https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/subscriptions/upgrade', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer <token>',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({tier: 'PROFESSIONAL', payment_method_id: null})
})
```

## Troubleshooting

### Gate Not Showing
- Check browser console for errors
- Verify `subscription-gate.js` is loaded: `console.log(window.SubscriptionGate)`
- Check API response: Network tab → `/check-feature/csrd`

### Component Not Rendering
- Ensure Vue 3 is loaded before components
- Check component registration: `app._context.components`
- Verify template syntax in browser console

### API Errors
- 401 Unauthorized: Token expired or invalid
- 402 Payment Required: Free tier attempting access (expected)
- 500 Server Error: Check Lambda logs in CloudWatch

### CORS Issues
If accessing from different domain:
```javascript
// In backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Next Steps

### 1. Stripe Integration
Add payment processing:
```javascript
// In subscription-gate.js upgradeTo() method
const stripe = Stripe('pk_live_...');
const {paymentMethod} = await stripe.createPaymentMethod({
    type: 'card',
    card: cardElement
});

await axios.post('/api/v1/subscriptions/upgrade', {
    tier: 'PROFESSIONAL',
    payment_method_id: paymentMethod.id
});
```

### 2. Blockchain Verification UI
Add blockchain badge to submitted reports:
```html
<div v-if="report.blockchain_verified" class="blockchain-badge">
    <i class="fas fa-shield-alt"></i>
    <span>Blockchain Verified</span>
    <a :href="report.blockchain_explorer_url" target="_blank">
        View on Explorer
    </a>
</div>
```

### 3. Email Notifications
Notify users on subscription changes:
- Upgrade confirmation
- Payment receipt
- Feature unlock notification
- Expiration warnings

### 4. Analytics Tracking
Track conversion funnel:
```javascript
// Google Analytics events
gtag('event', 'view_subscription_gate', {tier: 'FREE'});
gtag('event', 'click_upgrade', {target_tier: 'PROFESSIONAL'});
gtag('event', 'subscription_upgraded', {tier: 'PROFESSIONAL', value: 49});
```

## Support

For issues or questions:
- Backend API: Check `backend/app/api/v1/subscriptions.py`
- Database: Review `backend/app/db/subscription_db.py`
- Frontend: Inspect browser console and Network tab
- Logs: CloudWatch Logs → `/aws/lambda/carbontrack-api-prod`

## Pricing Strategy

Current pricing (as of 2025):
- **FREE**: $0 - Basic carbon tracking only
- **PROFESSIONAL**: $49/month - CSRD access, single entity
- **BUSINESS**: $149/month - Multi-entity (5), API access
- **ENTERPRISE**: $499/month - Unlimited, blockchain, white-label

**Market positioning**: 88-98% cheaper than competitors (Workiva $30K, Datamaran $50K)

**Unique selling points**:
1. 🔐 Only platform with blockchain-verified CSRD reports
2. ⚡ 50% faster audits with instant verification
3. 💰 Saves €20K-50K in annual audit fees
4. 🛡️ Regulatory protection (€1M EU fine insurance)
5. 🏆 ESG credibility badge for investors
