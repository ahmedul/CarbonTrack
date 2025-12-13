# Landing Page Deployment Guide

## Quick Deploy

Deploy the landing page to production:

```bash
./deploy-landing.sh
```

## What Gets Deployed

✅ **Landing page** (`landing.html`)
  - Professional hero section
  - CSRD challenge explanation
  - Core features showcase
  - Transparent pricing tables
  - Product roadmap
  - Call-to-action sections

❌ **NOT Deployed** (staying on feature branch):
  - CSRD Compliance Module backend
  - CSRD frontend UI
  - Premium subscription features
  - Database tables for CSRD

## Deployment Options

The script will ask you:

```
Deploy landing page as homepage? (y/N)
```

### Option 1: Deploy as `/landing.html` (Recommended)
- Answer: **N** (default)
- Landing page accessible at: `https://carbontracksystem.com/landing.html`
- Current homepage unchanged
- App remains at: `https://app.carbontracksystem.com`

### Option 2: Deploy as root homepage
- Answer: **Y**
- Landing page becomes: `https://carbontracksystem.com/`
- Original `index.html` backed up as `index.html.backup`
- Can revert later if needed

## After Deployment

### 1. Test the Landing Page
Visit: https://carbontracksystem.com/landing.html

Check:
- [ ] All sections load correctly
- [ ] Pricing tables display properly
- [ ] CTA buttons link to app.carbontracksystem.com
- [ ] Mobile responsive design works
- [ ] CloudFront CDN serving correctly

### 2. Update Marketing Materials
Update links in:
- LinkedIn posts → Point to landing page
- Email campaigns → Use landing page URL
- Social media → Share landing page
- Product Hunt → Use landing page as destination

### 3. Analytics (Optional)
Add Google Analytics tracking:
```html
<!-- Add to landing.html <head> section -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

## CSRD Development Workflow

Landing page is live, but CSRD features stay on feature branch:

```bash
# Current branch
git branch
# Output: feature/csrd-compliance-module

# Continue CSRD development
cd backend/app
# Work on CSRD API, database, frontend

# Test locally
python -m pytest tests/test_csrd_*.py

# When ready to deploy CSRD:
# 1. Merge feature branch to main
# 2. Run full deployment script
# 3. Create DynamoDB tables
# 4. Deploy CSRD frontend
```

## Rollback

If you need to rollback the landing page:

```bash
# Restore original index.html (if you deployed as root)
aws s3 cp s3://carbontrack-production-frontend/index.html.backup \
    s3://carbontrack-production-frontend/index.html \
    --region eu-central-1

# Invalidate CloudFront
aws cloudfront create-invalidation \
    --distribution-id EUKA4HQFK6MC \
    --paths "/index.html"

# Or just remove landing.html
aws s3 rm s3://carbontrack-production-frontend/landing.html \
    --region eu-central-1
```

## Troubleshooting

### Issue: Script fails to find S3 bucket
**Solution:** Update `S3_BUCKET` variable in `deploy-landing.sh`:
```bash
S3_BUCKET="your-actual-bucket-name"
```

### Issue: CloudFront invalidation fails
**Solution:** Update `CLOUDFRONT_DISTRIBUTION_ID` in `deploy-landing.sh`:
```bash
CLOUDFRONT_DISTRIBUTION_ID="your-distribution-id"
```

Find your distribution ID:
```bash
aws cloudfront list-distributions --query 'DistributionList.Items[].Id' --output text
```

### Issue: Changes not visible
**Wait time:** CloudFront cache invalidation takes 5-10 minutes
**Check:** https://carbontracksystem.com/landing.html?nocache=1

### Issue: Mobile layout broken
**Cause:** CSS not loading from CDN
**Solution:** Check Tailwind CSS CDN link in `landing.html`:
```html
<script src="https://cdn.tailwindcss.com"></script>
```

## Manual Deployment (If Script Fails)

```bash
# Upload landing page
aws s3 cp landing.html s3://carbontrack-production-frontend/landing.html \
    --region eu-central-1 \
    --cache-control "public, max-age=300, must-revalidate" \
    --content-type "text/html"

# Invalidate CloudFront
aws cloudfront create-invalidation \
    --distribution-id EUKA4HQFK6MC \
    --paths "/landing.html" \
    --region us-east-1
```

## Next Steps After Landing Page Deploy

1. **Monitor traffic:**
   - Check CloudFront logs
   - Monitor S3 bucket requests
   - Track conversion rates (free trial signups)

2. **A/B test CTAs:**
   - "Start Free Trial" vs "Book Demo"
   - Pricing emphasis (Professional tier)
   - CSRD urgency messaging

3. **Continue CSRD development:**
   - Complete frontend integration
   - Write comprehensive tests
   - Test subscription verification
   - Prepare staging environment

4. **Plan CSRD launch:**
   - Set target date: January 15, 2025
   - Beta access for Professional subscribers
   - Email existing users about new feature
   - Update pricing page with CSRD details

## Support

Questions or issues?
- Email: ahmedulkabir55@gmail.com
- Check deployment logs in terminal output
- Review CloudFront distribution in AWS Console
