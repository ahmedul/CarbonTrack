# 🌐 Custom Domain Setup Guide for CarbonTrack

**Your Current Setup:**
- ✅ CloudFront Distribution: `d2z2og1o0b9esb.cloudfront.net`
- ✅ Distribution ID: `EUKA4HQFK6MC`
- ✅ HTTPS enabled with automatic redirect
- ✅ Compression enabled

**Goal:** Set up `app.carbontrack.com` or `carbontrack.com`

---

## 📋 Prerequisites

You need to own a domain name. Options:

1. **Buy through AWS Route53** - Easiest integration (~$12/year for .com)
2. **Use existing domain** - From Namecheap, GoDaddy, etc.
3. **Use free subdomain** - Freenom, afraid.org (for testing)

---

## 🎯 Option 1: AWS Route53 (Recommended)

### **Step 1: Buy Domain in AWS Console**

1. Go to **Route53 Console**: https://console.aws.amazon.com/route53/
2. Click **"Registered domains"** in left sidebar
3. Click **"Register domain"** button
4. Search for: `carbontrack.com` (or your preferred name)
5. If available, click **"Add to cart"** → **"Continue"**
6. Fill in contact details
7. Enable **"Auto-renew"**
8. **Cost**: ~$12-13/year for .com
9. **Wait**: Domain registration takes ~10-15 minutes

### **Step 2: Request SSL Certificate**

1. Go to **Certificate Manager**: https://console.aws.amazon.com/acm/home?region=us-east-1
   - ⚠️ **IMPORTANT**: Must be in **us-east-1** region for CloudFront!
2. Click **"Request certificate"**
3. Select **"Request a public certificate"**
4. Add domain names:
   - `carbontrack.com`
   - `*.carbontrack.com` (wildcard for subdomains)
5. Click **"Next"**
6. Select **"DNS validation"** (easier)
7. Click **"Request"**
8. Click **"Create records in Route53"** button (auto-validates)
9. Wait ~5-10 minutes for validation

### **Step 3: Add Domain to CloudFront**

1. Go to **CloudFront Console**: https://console.aws.amazon.com/cloudfront/v3/home
2. Click on distribution **EUKA4HQFK6MC**
3. Click **"Edit"** in Settings section
4. Under **"Alternate domain names (CNAMEs)"**:
   - Click **"Add item"**
   - Enter: `app.carbontrack.com`
   - (Or just `carbontrack.com` if you want root domain)
5. Under **"Custom SSL certificate"**:
   - Click dropdown
   - Select your certificate (should appear after validation)
6. Click **"Save changes"**
7. Wait ~5-10 minutes for deployment

### **Step 4: Create DNS Record in Route53**

1. Go to **Route53 Console** → **"Hosted zones"**
2. Click on your domain: `carbontrack.com`
3. Click **"Create record"**
4. For subdomain (`app.carbontrack.com`):
   - **Record name**: `app`
   - **Record type**: `A`
   - **Alias**: ✅ Toggle ON
   - **Route traffic to**: "Alias to CloudFront distribution"
   - **Distribution**: `d2z2og1o0b9esb.cloudfront.net`
   - Click **"Create records"**

5. For root domain (`carbontrack.com`):
   - **Record name**: (leave empty)
   - **Record type**: `A`
   - **Alias**: ✅ Toggle ON
   - **Route traffic to**: "Alias to CloudFront distribution"
   - **Distribution**: `d2z2og1o0b9esb.cloudfront.net`
   - Click **"Create records"**

### **Step 5: Test**

Wait 5-10 minutes, then test:
```bash
# Check DNS propagation
dig app.carbontrack.com
nslookup app.carbontrack.com

# Test in browser
https://app.carbontrack.com
```

---

## 🎯 Option 2: External Domain (Namecheap, GoDaddy, etc.)

If you already own a domain elsewhere:

### **Step 1: Request SSL Certificate in AWS**

1. Go to **Certificate Manager** (us-east-1): https://console.aws.amazon.com/acm/home?region=us-east-1
2. Click **"Request certificate"**
3. Add domains: `yourdomain.com` and `*.yourdomain.com`
4. Select **"DNS validation"**
5. Click **"Request"**
6. **Copy the CNAME record** (you'll add this to your domain registrar)

### **Step 2: Add Validation Record to Your Domain Registrar**

**For Namecheap:**
1. Login → Dashboard → Manage domain
2. **Advanced DNS** tab
3. Click **"Add New Record"**
4. **Type**: CNAME
5. **Host**: (from AWS Certificate Manager, e.g., `_abc123.yourdomain.com`)
6. **Value**: (from AWS, e.g., `_xyz789.acm-validations.aws`)
7. **TTL**: Automatic
8. Click **"Save"**

**For GoDaddy:**
1. Login → My Products → DNS
2. Click **"Add"**
3. **Type**: CNAME
4. **Name**: (from AWS)
5. **Value**: (from AWS)
6. **TTL**: 600
7. Click **"Save"**

**For Cloudflare:**
1. Login → Select domain → DNS
2. Click **"Add record"**
3. **Type**: CNAME
4. **Name**: (from AWS)
5. **Target**: (from AWS)
6. **Proxy status**: DNS only (gray cloud)
7. Click **"Save"**

Wait ~10-30 minutes for validation.

### **Step 3: Add Domain to CloudFront**

(Same as Option 1, Step 3)

### **Step 4: Point Domain to CloudFront**

Add these DNS records in your domain registrar:

**For subdomain (app.yourdomain.com):**
- **Type**: CNAME
- **Host**: `app`
- **Value**: `d2z2og1o0b9esb.cloudfront.net`
- **TTL**: 300 or Automatic

**For root domain (yourdomain.com):**
- **Type**: ALIAS (if supported) or A record
- **Host**: `@` or leave empty
- **Value**: `d2z2og1o0b9esb.cloudfront.net`
- **TTL**: 300

⚠️ **Note**: Some registrars don't support ALIAS records for root domains. In that case:
- Use `www.yourdomain.com` instead
- Or migrate DNS to Route53 (free, keeps domain at registrar)

### **Step 5: Test**

```bash
# Check DNS
dig app.yourdomain.com

# Test in browser
https://app.yourdomain.com
```

---

## 🎯 Option 3: Free Subdomain (Testing Only)

For testing without buying a domain:

### **Services:**
- **afraid.org** - Free DNS service
- **duckdns.org** - Free dynamic DNS
- **noip.com** - Free hostname

**Example with DuckDNS:**

1. Go to: https://www.duckdns.org/
2. Sign in with social account
3. Create subdomain: `carbontrack.duckdns.org`
4. Point to CloudFront:
   - Click domain → Update IP
   - Enter CloudFront IP (get via: `ping d2z2og1o0b9esb.cloudfront.net`)

⚠️ **Limitation**: Free services don't support SSL certificates easily.

---

## 📊 Cost Breakdown

| Item | Monthly Cost | Annual Cost |
|------|-------------|-------------|
| **Domain (.com)** | ~$1 | ~$12-13 |
| **Route53 Hosted Zone** | $0.50 | $6 |
| **SSL Certificate** | FREE | FREE |
| **CloudFront** | ~$1-5 | ~$12-60 |
| **S3 Storage** | <$0.50 | <$6 |
| **Total** | ~$2-7 | ~$24-84 |

---

## 🚀 Quick Command Reference

### **Check if domain is available:**
```bash
aws route53domains check-domain-availability --domain-name carbontrack.com
```

### **Register domain via CLI:**
```bash
aws route53domains register-domain \
  --domain-name carbontrack.com \
  --duration-in-years 1 \
  --auto-renew \
  --admin-contact file://contact.json \
  --registrant-contact file://contact.json \
  --tech-contact file://contact.json
```

### **Create SSL certificate:**
```bash
aws acm request-certificate \
  --domain-name carbontrack.com \
  --subject-alternative-names "*.carbontrack.com" \
  --validation-method DNS \
  --region us-east-1
```

### **Get certificate ARN:**
```bash
aws acm list-certificates --region us-east-1
```

### **Check DNS propagation:**
```bash
dig app.carbontrack.com
nslookup app.carbontrack.com
host app.carbontrack.com
```

### **Test HTTPS:**
```bash
curl -I https://app.carbontrack.com
```

---

## 🎯 Current Status (No Custom Domain)

Your app is live at:

**Primary URL:** https://d2z2og1o0b9esb.cloudfront.net

This works perfectly! A custom domain is optional but provides:
- ✅ Professional appearance
- ✅ Brand recognition
- ✅ Easier to remember
- ✅ Better for marketing

---

## 🔍 Troubleshooting

### **"Certificate not appearing in CloudFront dropdown"**
- ✅ Check you're in **us-east-1** region
- ✅ Certificate status must be "Issued"
- ✅ Wait 5-10 minutes after validation

### **"DNS not resolving"**
- ✅ Wait 5-15 minutes for propagation
- ✅ Try: `dig app.yourdomain.com @8.8.8.8`
- ✅ Check CloudFront alternate domain names match DNS

### **"Invalid SSL certificate error"**
- ✅ Certificate must include exact domain name
- ✅ CloudFront alternate names must match certificate
- ✅ DNS must point to CloudFront correctly

### **"Still seeing CloudFront domain"**
- ✅ Clear browser cache (Ctrl+Shift+R)
- ✅ Try incognito mode
- ✅ Check DNS: `nslookup app.yourdomain.com`

---

## 📞 Next Steps

1. **Decide on domain name**: 
   - Option A: Buy `carbontrack.com` via Route53 (~$12/year)
   - Option B: Use existing domain
   - Option C: Keep CloudFront URL for now

2. **If buying domain**: Follow "Option 1" above
3. **If using existing**: Follow "Option 2" above
4. **If keeping CloudFront URL**: You're done! ✅

---

## 💡 Recommended Domain Names

Available to check:
- `carbontrack.app` - Modern, tech-focused
- `carbontrack.io` - Startup-friendly
- `carbontrack.com` - Classic, professional
- `mycarbon.app` - User-focused
- `trackcarbon.app` - Action-oriented

Check availability:
```bash
aws route53domains check-domain-availability --domain-name carbontrack.com
aws route53domains check-domain-availability --domain-name carbontrack.app
aws route53domains check-domain-availability --domain-name carbontrack.io
```

---

**Need help with any step? Let me know!** 🚀
