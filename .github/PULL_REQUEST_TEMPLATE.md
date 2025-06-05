# 🚨 PRODUCTION DEPLOYMENT CHECKLIST

**CRITICAL: This repository deploys to production EVA web app**

## Repository Verification
- [ ] I confirmed this is the correct repository (eva_web)
- [ ] I verified the remote URL: `git remote -v`
- [ ] I checked this is NOT for realtime app features
- [ ] I checked this is NOT for experimental features

## Change Verification
- [ ] This change is for the main EVA web application
- [ ] I tested the change locally with `python core/eva.py`
- [ ] The current version is working before this change
- [ ] This is a minimal, focused change
- [ ] I have a rollback plan if this breaks

## Deployment Safety
- [ ] I verified `railway.json` contains `python core/eva.py`
- [ ] I confirmed deployment target is evaweb-production.up.railway.app
- [ ] User has been notified of this deployment
- [ ] This change won't break existing functionality

## Emergency Contacts
If this deployment fails:
1. Immediately rollback: `git reset --hard [PREVIOUS_WORKING_COMMIT]`
2. Force push: `git push --force origin main`
3. Notify user of status

## What This Change Does
<!-- Describe in detail what this change accomplishes -->

## Testing Performed
<!-- Describe how you tested this change -->

## Rollback Plan
<!-- Describe how to revert if this breaks -->

---

**⚠️ REMEMBER: Every push affects live users. When in doubt, don't deploy.**