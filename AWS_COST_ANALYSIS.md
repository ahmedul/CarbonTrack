# CarbonTrack AWS Cost Analysis & Budget Management
## Monthly Budget: €50 Maximum

### 🏷️ AWS Free Tier Breakdown (First 12 months)

#### ✅ **Services That Stay FREE Within Limits**
| Service | Free Tier Limit | Usage Pattern | Expected Cost |
|---------|----------------|---------------|---------------|
| **DynamoDB** | 25 GB storage + 200M requests/month | Carbon data storage | €0 |
| **Lambda** | 1M requests + 400K GB-seconds/month | API processing | €0 |
| **S3** | 5 GB storage + 20K GET/2K PUT requests | Frontend hosting | €0 |
| **CloudFront** | 50 GB transfer + 2M requests/month | Global CDN | €0 |
| **API Gateway** | 1M requests/month | API routing | €0 |
| **Cognito** | 50,000 MAU (Monthly Active Users) | User authentication | €0 |

**Total Free Tier Value: €0/month for typical startup usage**

#### ⚠️ **Services That May Incur Costs**

##### **Lambda Beyond Free Tier**
- **Free**: 1,000,000 requests/month
- **After**: €0.0000002 per request
- **Memory cost**: €0.0000166667 per GB-second

**Cost Calculation:**
```
10M requests/month = €1.80
20M requests/month = €3.60
```

##### **API Gateway Beyond Free Tier**
- **Free**: 1,000,000 requests/month  
- **After**: €3.50 per million requests

##### **DynamoDB Beyond Free Tier**
- **Free**: 25 GB storage + 200M requests
- **Storage**: €0.25 per GB/month
- **Requests**: €0.25 per million reads, €1.25 per million writes

##### **S3 Storage Beyond Free Tier**
- **Free**: 5 GB
- **After**: €0.023 per GB/month

### 📊 **Projected Monthly Costs by User Scale**

#### **Scenario 1: MVP Phase (0-100 users)**
| Service | Usage | Cost |
|---------|-------|------|
| Lambda | 500K requests | €0 (Free Tier) |
| API Gateway | 500K requests | €0 (Free Tier) |
| DynamoDB | 10 GB, 50M requests | €0 (Free Tier) |
| S3 | 1 GB | €0 (Free Tier) |
| CloudFront | 10 GB transfer | €0 (Free Tier) |
| **Total** | | **€0/month** |

#### **Scenario 2: Growth Phase (100-1000 users)**  
| Service | Usage | Cost |
|---------|-------|------|
| Lambda | 5M requests | €0.80 |
| API Gateway | 5M requests | €14.00 |
| DynamoDB | 50 GB, 500M requests | €6.25 |
| S3 | 3 GB | €0.07 |
| CloudFront | 100 GB transfer | €8.50 |
| Route 53 | Domain hosting | €0.50 |
| **Total** | | **€30.12/month** |

#### **Scenario 3: Scale Phase (1000+ users)**
| Service | Usage | Cost |
|---------|-------|------|
| Lambda | 20M requests | €3.60 |
| API Gateway | 20M requests | €56.00 |
| DynamoDB | 200 GB, 2B requests | €43.75 |
| S3 | 10 GB | €0.23 |
| CloudFront | 500 GB transfer | €42.50 |
| **Total** | | **€146.08/month** |

### 🚨 **Cost Control Strategy**

#### **1. Immediate Cost Safeguards**
```yaml
# AWS Budgets Configuration
Monthly Budget: €50
Alert Thresholds:
  - 50% (€25): Warning email
  - 80% (€40): Critical email  
  - 100% (€50): Emergency email + Slack alert
  - 120% (€60): Auto-disable non-essential services
```

#### **2. Service-Specific Limits**
```yaml
Lambda:
  Max Monthly Cost: €15
  Request Limit: 25M/month
  Memory Limit: 512MB max
  Timeout: 30s max

API Gateway:
  Max Monthly Cost: €20  
  Request Limit: 6M/month
  Enable caching: true
  
DynamoDB:
  Max Monthly Cost: €10
  On-demand pricing: true
  Auto-scaling: disabled initially
```

#### **3. Cost Optimization Techniques**

##### **Lambda Optimizations**
```python
# Reduce memory usage
MEMORY_SIZE = 256  # Start small, increase if needed

# Optimize cold starts
import json
import os
# Load configs once, outside handler
DATABASE_URL = os.environ.get('DATABASE_URL')

def lambda_handler(event, context):
    # Keep handler lightweight
    pass
```

##### **API Gateway Optimizations**
```yaml
# Enable caching to reduce Lambda calls
CacheKeyParameters:
  - method.request.path.user_id
CacheTtlInSeconds: 300  # 5 minute cache
```

##### **DynamoDB Optimizations**
```python
# Batch operations to reduce request count
def batch_write_emissions(emissions_list):
    # Write up to 25 items in single request
    table.batch_writer():
        for emission in emissions_list:
            table.put_item(Item=emission)

# Use efficient query patterns
def get_user_emissions(user_id, start_date, end_date):
    # Single query instead of multiple gets
    return table.query(
        KeyConditionExpression=Key('user_id').eq(user_id) & 
                             Key('timestamp').between(start_date, end_date)
    )
```

### 🔧 **Cost Monitoring Implementation**

#### **1. CloudWatch Alarms**
```yaml
# High request count alarm
Lambda Invocations > 1M/hour: Alert
API Gateway Requests > 500K/hour: Alert
DynamoDB Read/Write > 10K/minute: Alert
```

#### **2. Daily Cost Reports**
```python
# Lambda function for daily cost check
def daily_cost_check():
    costs = get_daily_costs()
    if costs > daily_budget:
        send_alert(f"Daily costs: €{costs}")
        
    monthly_projection = costs * 30
    if monthly_projection > 50:
        send_critical_alert(f"Projected monthly: €{monthly_projection}")
```

#### **3. Usage Analytics Dashboard**
```yaml
Metrics to Track:
  - Requests per minute/hour/day
  - Lambda duration and memory usage
  - DynamoDB read/write capacity consumption
  - S3 storage growth
  - CloudFront bandwidth usage
  - Error rates (failures cost money too)
```

### 💡 **Emergency Cost Control Measures**

#### **If Approaching €50 Budget:**
1. **Enable API rate limiting**: Max 100 req/min per user
2. **Reduce Lambda memory**: 256MB → 128MB  
3. **Increase cache TTL**: 5min → 30min
4. **Disable non-essential features**: PDF processing, complex analytics

#### **If Budget Exceeded:**
```bash
# Emergency cost control script
./emergency-cost-control.sh
  - Disable API Gateway endpoints
  - Pause DynamoDB auto-scaling
  - Set S3 lifecycle policies
  - Enable CloudFront compression
```

### 📈 **Revenue vs Cost Planning**

#### **Break-even Analysis**
```
Target: €50 monthly costs = €600 yearly
Required Revenue: €1200 yearly (2x cost)
Monthly Revenue Target: €100

Pricing Strategy:
- Free Tier: 0-100 emissions/month (€0)
- Basic Tier: 101-1000 emissions/month (€9.99)
- Pro Tier: Unlimited + Analytics (€29.99)

Break-even: 10 Basic users OR 4 Pro users
```

### 🛡️ **Monitoring & Alerts Setup**

#### **Email Alerts Configuration**
```bash
# Set up cost monitoring
aws budgets create-budget --account-id YOUR_ACCOUNT_ID \
  --budget file://budget-config.json \
  --notifications-with-subscribers file://notifications.json
```

#### **Slack Integration** (Optional)
```python
# Webhook for critical cost alerts
def send_slack_alert(message):
    webhook_url = os.environ['SLACK_WEBHOOK']
    requests.post(webhook_url, json={"text": f"🚨 CarbonTrack Cost Alert: {message}"})
```

This comprehensive cost management ensures you'll never exceed your €50 budget while maximizing the free tier benefits!