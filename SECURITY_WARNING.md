# 🚨 SECURITY NOTICE - IMMEDIATE ACTION REQUIRED

**Date**: December 12, 2025  
**Status**: ⚠️ **CRITICAL - Secrets Exposed in Git History**

---

## Issue Discovered

The following files containing **real production secrets** were accidentally committed to git history:

1. ❌ `backend/aws-cognito-config.txt` - Contains Cognito Client Secret
2. ❌ `DEPLOYMENT_SECRETS.md` - Contains partial AWS credentials

**Commit**: e4489332e2c23e66653633f0c682225cb47aa810 (Sept 27, 2025)

---

## ✅ Immediate Actions Taken

### 1. Secured Repository
- ✅ Added secrets to `.gitignore`
- ✅ Removed files from git tracking (`git rm --cached`)
- ✅ Created template files for configuration

### 2. Files Now in `.gitignore`
```
backend/aws-cognito-config.txt
DEPLOYMENT_SECRETS.md
**/secrets.json
**/*secret*.txt
**/*credentials*.txt
.env*
```

---

## 🔴 REQUIRED: Rotate Compromised Credentials

### AWS Cognito Client Secret (CRITICAL)

**Exposed Secret**: `192sju21i9d0k9jhfn6g68cco7ib2vnu047583kbkos8f9c6bd8h`

**Steps to Rotate**:

1. **Go to AWS Console** → Cognito → User Pools
2. Navigate to: `eu-central-1_liszdknXy` → App clients → `3rg58gvke8v6afmfng7o4fk0r1`
3. Click **"Regenerate app client secret"**
4. **Copy the NEW secret immediately** (it won't be shown again)
5. Update in these locations:
   - Lambda environment variable: `COGNITO_CLIENT_SECRET`
   - Local `backend/aws-cognito-config.txt` (NOT in git)
   - Any CI/CD secrets in GitHub

**Command to update Lambda**:
```bash
aws lambda update-function-configuration \
  --function-name carbontrack-api \
  --environment "Variables={COGNITO_CLIENT_SECRET=<NEW_SECRET>,COGNITO_CLIENT_ID=3rg58gvke8v6afmfng7o4fk0r1,COGNITO_USER_POOL_ID=eu-central-1_liszdknXy,COGNITO_REGION=eu-central-1,DYNAMODB_REGION=eu-central-1}" \
  --region eu-central-1
```

### AWS Access Keys (if exposed)

If you find any AWS access keys in `DEPLOYMENT_SECRETS.md`:
1. AWS Console → IAM → Users → Security credentials
2. **Deactivate old keys**
3. **Create new access keys**
4. Update in GitHub Secrets and local environment

---

## 🛡️ Prevention Measures

### 1. Use Environment Variables Only
```bash
# In Lambda (AWS Console or CLI)
COGNITO_CLIENT_SECRET=<value>
AWS_ACCESS_KEY_ID=<value>  # Only if needed
AWS_SECRET_ACCESS_KEY=<value>  # Only if needed
```

### 2. Never Commit These File Types
- ❌ `.env` files
- ❌ `*secret*.txt`
- ❌ `*credentials*.txt`
- ❌ `aws-cognito-config.txt`
- ❌ Any file with actual API keys, passwords, tokens

### 3. Use Template Files Instead
- ✅ `aws-cognito-config.txt.template` (committed)
- ✅ `.env.example` (committed)
- ✅ `DEPLOYMENT_SECRETS.md.template` (if needed)

### 4. GitHub Secrets for CI/CD
Store secrets in: **Settings → Secrets and variables → Actions**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `COGNITO_CLIENT_SECRET`

---

## 📝 Git History Cleanup (Optional but Recommended)

⚠️ **Warning**: This rewrites git history and requires force-push

### Option 1: BFG Repo-Cleaner (Recommended)
```bash
# Install BFG
brew install bfg  # macOS
# or download from: https://rtyley.github.io/bfg-repo-cleaner/

# Create backup first!
cd ..
git clone --mirror CarbonTrack CarbonTrack-backup.git

# Remove sensitive files from history
cd CarbonTrack
bfg --delete-files aws-cognito-config.txt
bfg --delete-files DEPLOYMENT_SECRETS.md

git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force
```

### Option 2: git filter-branch (Manual)
```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch backend/aws-cognito-config.txt DEPLOYMENT_SECRETS.md" \
  --prune-empty --tag-name-filter cat -- --all

git push origin --force --all
git push origin --force --tags
```

**Note**: After force-push, all collaborators need to re-clone:
```bash
git clone https://github.com/ahmedul/CarbonTrack.git
```

---

## ✅ Verification Checklist

- [ ] Cognito Client Secret rotated in AWS
- [ ] Lambda environment variable updated with new secret
- [ ] Old secret deactivated/deleted
- [ ] `.gitignore` updated (already done ✅)
- [ ] Sensitive files removed from git (`git rm --cached`) (already done ✅)
- [ ] Git history cleaned (optional but recommended)
- [ ] All team members notified to re-clone repo
- [ ] GitHub repository secrets updated (if applicable)

---

## 🔍 How to Check for Secrets Going Forward

Run this before each commit:
```bash
./security-check.sh
```

Or add a pre-commit hook:
```bash
# .git/hooks/pre-commit
#!/bin/bash
if grep -r "AKIA\|aws_secret" --include="*.py" --include="*.js" --exclude-dir=".git" .; then
    echo "⚠️  WARNING: Potential AWS secrets detected!"
    echo "Please review before committing."
    exit 1
fi
```

---

## 📞 Support

If you need help with secret rotation:
1. AWS Documentation: https://docs.aws.amazon.com/cognito/latest/developerguide/
2. Check `backend/aws-cognito-config.txt.template` for configuration guide
3. Review `.gitignore` to ensure no secrets committed

**Last Updated**: December 12, 2025
