# 🚨 PRODUCTION REPOSITORY - HANDLE WITH EXTREME CARE

## ⚠️ CRITICAL WARNING ⚠️

**THIS REPOSITORY DEPLOYS DIRECTLY TO PRODUCTION EVA WEB APPLICATION**

- **Live URL**: https://evaweb-production.up.railway.app
- **Users**: Real users depend on this application
- **Impact**: Every push affects production immediately

---

## 🛡️ SAFETY MEASURES IMPLEMENTED

### 1. **Mandatory Safety Check Script**
```bash
# ALWAYS use this before pushing:
./pre-push-safety-check.sh
```

### 2. **Repository Verification**
- `.git-safety-config` - Repository identification
- Automatic verification of deployment target
- Protection against wrong repository pushes

### 3. **Documentation**
- `docs/REPOSITORY_SAFETY_GUIDE.md` - Complete safety procedures
- Pull request template with mandatory checklist
- Emergency rollback procedures

### 4. **Git Hooks** (Recommended)
```bash
# Set up pre-push hook
ln -s ../../pre-push-safety-check.sh .git/hooks/pre-push
```

---

## 🚫 FOR AI ASSISTANTS (Claude Code)

### **MANDATORY VERIFICATION BEFORE ANY GIT OPERATION:**

1. **Check repository identity:**
   ```bash
   git remote -v
   # Must show: eva_web repository
   ```

2. **Verify deployment config:**
   ```bash
   cat railway.json
   # Must show: "python core/eva.py"
   ```

3. **Confirm with user:**
   - "I'm about to modify the PRODUCTION eva_web repository"
   - "This will affect evaweb-production.up.railway.app"
   - "Are you absolutely sure this is correct?"

### **NEVER ASSUME - ALWAYS VERIFY**

---

## 📋 EMERGENCY PROCEDURES

### If Production Breaks:
```bash
# 1. Immediate rollback
git reset --hard [LAST_WORKING_COMMIT]
git push --force origin main

# 2. Check Railway deployment
# 3. Notify user immediately
```

### Last Known Working Commit:
- **Commit**: `92c7902`
- **Date**: June 5, 2025
- **Description**: Fix mobile audio autoplay restrictions

---

## 🔍 QUICK REPOSITORY IDENTIFICATION

### ✅ **THIS IS THE RIGHT REPO IF:**
- Remote URL contains "eva_web"
- `railway.json` has `python core/eva.py`
- `core/eva.py` file exists
- No `realtime_app/` directory

### ❌ **THIS IS THE WRONG REPO IF:**
- Remote URL contains "realtime" or "experiments"
- `railway.json` mentions realtime_app
- Missing `core/eva.py`
- Has experimental features

---

**🚨 WHEN IN DOUBT, DON'T PUSH. ASK THE USER FIRST. 🚨**

---

*Created after emergency rollback on June 5, 2025*  
*Reason: Incorrect repository push caused production outage*