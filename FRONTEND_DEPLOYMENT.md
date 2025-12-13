# CarbonTrack Frontend Structure

## 📁 File Structure

```
CarbonTrack/
├── frontend/
│   ├── index.html          ← LANDING PAGE (deployed to S3 root /)
│   └── app/
│       ├── index.html      ← APP PAGE (deployed to S3 /app/)
│       ├── app-full.js     ← Main app logic
│       ├── csrd-dashboard.js
│       ├── subscription-gate.js
│       └── assets/
```

## 🌐 URL Structure

- **https://carbontracksystem.com/** → Landing page with roadmap, pricing, features
- **https://carbontracksystem.com/app/** → Application (login, dashboard, etc.)

## 🚀 Deployment

### Quick Deploy
```bash
./deploy-frontend.sh
```

### Manual Deploy (if needed)

**⚠️ NEVER run `aws s3 sync frontend/ s3://...` - it will overwrite the landing page!**

Instead, use these commands:

```bash
# Deploy landing page to root
aws s3 cp frontend/index.html s3://carbontrack-frontend-production/index.html

# Deploy app files to /app/ subdirectory
aws s3 sync frontend/app/ s3://carbontrack-frontend-production/app/

# Invalidate CloudFront
aws cloudfront create-invalidation --distribution-id EUKA4HQFK6MC --paths "/" "/app/*"
```

## ⚠️ IMPORTANT RULES

1. **NEVER** sync `frontend/` directly to S3 root - it will overwrite the landing page
2. **ALWAYS** deploy `frontend/index.html` to S3 root separately
3. **ALWAYS** deploy `frontend/app/*` to S3 `/app/` subdirectory
4. Use the `deploy-frontend.sh` script to ensure correct structure

## 📝 Files to Remember

- `frontend/index.html` = Landing page (45KB with full content)
- `frontend/app/index.html` = App page (Vue.js application)

## 🔧 CloudFront Configuration

- Distribution ID: `EUKA4HQFK6MC`
- Domain: `carbontracksystem.com`
- S3 Bucket: `carbontrack-frontend-production`
- Default Root Object: `index.html`
