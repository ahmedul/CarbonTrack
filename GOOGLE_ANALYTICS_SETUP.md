# Google Analytics 4 Setup Guide

## Overview
Google Analytics 4 (GA4) has been added to CarbonTrack to track user behavior, page views, and engagement metrics.

## Setup Required

### 1. Create Google Analytics 4 Property

1. Go to https://analytics.google.com/
2. Click "Admin" (gear icon in bottom left)
3. Click "Create Property"
4. Enter property details:
   - **Property name**: CarbonTrack
   - **Reporting time zone**: Your timezone
   - **Currency**: USD (or your preference)
5. Click "Next" and complete business information
6. Create a **Web** data stream:
   - **Website URL**: https://carbontracksystem.com
   - **Stream name**: CarbonTrack Production
7. Copy your **Measurement ID** (format: G-XXXXXXXXXX)

### 2. Update Frontend Configuration

Replace the placeholder in `frontend/index.html`:

```html
<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-XXXXXXXXXX', {  <!-- Replace with your Measurement ID -->
        'send_page_view': true,
        'cookie_flags': 'SameSite=None;Secure'
    });
</script>
```

### 3. Verify Installation

1. Deploy the updated frontend
2. Visit https://carbontracksystem.com
3. In Google Analytics:
   - Go to **Reports** > **Realtime**
   - You should see your own visit within 30 seconds

## Tracked Events

GA4 automatically tracks:

- **Page views**: Every page navigation
- **Scrolls**: 90% scroll depth
- **Outbound clicks**: External links
- **Site search**: Search queries (if implemented)
- **Video engagement**: Play, pause, complete
- **File downloads**: PDF, CSV downloads

## Custom Events (Future Enhancement)

You can add custom event tracking for specific user actions:

```javascript
// Track button clicks
gtag('event', 'add_activity', {
    'event_category': 'engagement',
    'event_label': 'transportation',
    'value': 1
});

// Track feature usage
gtag('event', 'view_recommendations', {
    'event_category': 'feature_usage',
    'recommendations_count': 10
});

// Track conversions
gtag('event', 'complete_goal', {
    'event_category': 'conversion',
    'goal_name': 'reduce_emissions_20_percent'
});
```

## Key Metrics to Monitor

### Engagement Metrics
- **Users**: Total unique visitors
- **Sessions**: Total visits to site
- **Engaged sessions**: Sessions lasting >10s or >2 page views
- **Engagement rate**: % of engaged sessions
- **Average engagement time**: Time spent on site

### Behavior Metrics
- **Views**: Total page views
- **Views per session**: Pages viewed per visit
- **Event count**: Total tracked events
- **Conversions**: Goal completions

### User Acquisition
- **New users**: First-time visitors
- **Source/Medium**: Where users come from
- **Campaign performance**: Marketing campaign effectiveness

### Retention
- **User retention**: % of users who return
- **Cohort analysis**: User behavior over time
- **Lifetime value**: Value of user over time

## Reports to Create

### 1. Feature Usage Dashboard
Track which features users engage with most:
- Dashboard views
- Activity additions
- Recommendations viewed
- Gamification engagement

### 2. User Journey Analysis
Understand how users navigate:
- Entry pages
- Exit pages
- Path analysis
- Drop-off points

### 3. Beta Testing Metrics
Monitor beta user behavior:
- Daily active users (DAU)
- Weekly active users (WAU)
- Feature adoption rate
- Time to first activity

### 4. Conversion Funnel
Track user progression:
1. Landing page visit
2. Registration
3. First activity added
4. 7-day retention
5. Goal completion

## Privacy & Compliance

### GDPR Compliance
GA4 includes built-in data controls:
- **IP anonymization**: Enabled by default
- **Data retention**: Set to 14 months
- **User deletion**: Request user data deletion
- **Cookie consent**: Implement cookie banner

### Cookie Banner (Required for EU users)

Add to frontend:

```html
<div id="cookie-banner" class="cookie-banner">
    <p>We use cookies to analyze site usage and improve your experience.</p>
    <button onclick="acceptCookies()">Accept</button>
    <button onclick="rejectCookies()">Reject</button>
</div>

<script>
function acceptCookies() {
    document.getElementById('cookie-banner').style.display = 'none';
    localStorage.setItem('cookies-accepted', 'true');
    // Enable GA4
    gtag('consent', 'update', {
        'analytics_storage': 'granted'
    });
}

function rejectCookies() {
    document.getElementById('cookie-banner').style.display = 'none';
    localStorage.setItem('cookies-accepted', 'false');
    // Disable GA4
    gtag('consent', 'update', {
        'analytics_storage': 'denied'
    });
}

// Check cookie consent on page load
if (!localStorage.getItem('cookies-accepted')) {
    document.getElementById('cookie-banner').style.display = 'block';
}
</script>
```

## Data Studio Integration

Create visual reports:

1. Go to https://datastudio.google.com/
2. Click "Create" > "Report"
3. Select GA4 as data source
4. Choose "CarbonTrack" property
5. Add widgets:
   - Users over time (line chart)
   - Top pages (table)
   - User acquisition (pie chart)
   - Events (bar chart)

## Optimization Tips

### 1. Set Up Goals/Conversions
Define key actions as conversions:
- User registration
- First activity added
- 5 activities completed
- Recommendation followed
- 30-day retention

### 2. Enable Enhanced Measurement
In GA4 stream settings, enable:
- ✅ Scrolls
- ✅ Outbound clicks
- ✅ Site search
- ✅ Video engagement
- ✅ File downloads

### 3. Link to Google Ads (Optional)
If running ads:
1. Admin > Property > Google Ads Links
2. Link your Google Ads account
3. Track ad performance and ROI

### 4. Set Up Alerts
Get notified of unusual activity:
1. Admin > Property > Custom Insights
2. Create alerts for:
   - Traffic drops >20%
   - Error rate increases
   - Conversion drops

## Testing

### Local Testing
```bash
# GA4 won't track localhost by default
# To test locally, temporarily change config:
gtag('config', 'G-XXXXXXXXXX', {
    'send_page_view': true,
    'debug_mode': true  // Enables debug mode
});

# Then view events in browser console
```

### Debug View
1. Install "Google Analytics Debugger" Chrome extension
2. Enable extension
3. Visit your site
4. Check browser console for GA4 events

### Real-time Testing
1. Visit https://carbontracksystem.com
2. Open GA4 > Reports > Realtime
3. Perform actions (add activity, view pages)
4. Verify events appear in real-time report

## Cost

Google Analytics 4 is **free** for up to:
- 10 million events per month
- 25 million events per day
- 50 custom dimensions
- 50 custom metrics

For most SaaS applications, the free tier is sufficient.

## Next Steps

1. **Week 1**: Monitor basic metrics (users, sessions, page views)
2. **Week 2**: Analyze user behavior and drop-off points
3. **Week 3**: Set up conversion goals and funnels
4. **Week 4**: Create custom dashboards and reports
5. **Month 2**: Implement A/B testing and optimization

## Resources

- [GA4 Documentation](https://support.google.com/analytics/answer/10089681)
- [GA4 Setup Guide](https://support.google.com/analytics/answer/9304153)
- [Event Reference](https://support.google.com/analytics/answer/9267735)
- [GA4 vs UA Differences](https://support.google.com/analytics/answer/9964640)
