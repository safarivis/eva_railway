# 🚨 REPOSITORY SAFETY GUIDE
## Preventing Production Deployment Disasters

**CRITICAL: This repository deploys directly to production EVA web app**

---

## ⚠️ **What Went Wrong (June 5, 2025)**

### The Mistake:
- Claude Code assistant confused repositories
- Pushed **realtime app changes** to **main EVA web repo**
- Caused production deployment to fail
- Mixed experimental features with stable production code

### The Impact:
- Production EVA web app went down
- User lost access to working application
- Required emergency rollback to previous working state
- Lost user trust and caused panic

---

## 🎯 **Repository Structure (REMEMBER THIS!)**

### **THIS REPOSITORY** (`eva_web`)
- **URL**: https://github.com/safarivis/eva_web.git
- **Purpose**: Main EVA web application
- **Deployment**: https://evaweb-production.up.railway.app
- **Command**: `python core/eva.py`
- **Status**: PRODUCTION - HANDLE WITH EXTREME CARE

### **SEPARATE REPOSITORIES** (DO NOT MIX!)
- **EVA Realtime**: Different repo for realtime features
- **EVA Experiments**: Different repo for new features
- **EVA Assistants**: Different repo for assistants API

---

## 🛡️ **Safety Protocols**

### **Before ANY Git Push:**

1. **STOP AND VERIFY**
   ```bash
   # Check which repository you're in
   git remote -v
   # Should show: origin https://github.com/safarivis/eva_web.git
   ```

2. **CONFIRM PURPOSE**
   - Is this change for the MAIN EVA web app?
   - Or is it for realtime features (wrong repo!)?
   - Or is it experimental (wrong repo!)?

3. **CHECK DEPLOYMENT TARGET**
   ```bash
   # Verify railway.json contents
   cat railway.json
   # Should show: "startCommand": "python core/eva.py"
   ```

4. **TEST LOCALLY FIRST**
   ```bash
   # ALWAYS test before pushing
   python core/eva.py --test
   ```

5. **VERIFY WORKING STATE**
   - Is the current version working?
   - Will this change break anything?
   - Do you have a rollback plan?

### **Push Checklist (MANDATORY)**
```
□ Verified repository URL (eva_web, not realtime)
□ Confirmed this is for main EVA web app
□ Tested changes locally
□ Current version is working
□ Change is minimal and safe
□ Rollback plan ready
□ User has been notified of deployment
```

---

## 🚫 **FORBIDDEN ACTIONS**

### **NEVER Push These to Main EVA Repo:**
- Realtime app features
- Experimental logging systems
- Assistants API changes
- Major architectural changes
- Untested features
- Multiple unrelated changes at once

### **NEVER Push Without:**
- Testing locally first
- Confirming repository
- User approval for risky changes
- Rollback plan

---

## 🔧 **Emergency Procedures**

### **If Production Breaks:**
1. **IMMEDIATE ROLLBACK**
   ```bash
   # Find last working commit
   git log --oneline
   
   # Rollback to working commit
   git reset --hard [WORKING_COMMIT_HASH]
   
   # Force push to restore
   git push --force origin main
   ```

2. **NOTIFY USER**
   - Explain what happened
   - Provide timeline for fix
   - Keep them updated

3. **INVESTIGATE**
   - What caused the failure?
   - How to prevent it again?
   - Update safety procedures

---

## 📋 **Repository Identification**

### **How to Know You're in the RIGHT Repo:**
```bash
# Check remote URL
git remote get-url origin
# Should be: https://github.com/safarivis/eva_web.git

# Check railway.json
cat railway.json
# Should have: "python core/eva.py"

# Check main files exist
ls core/eva.py
# Should exist for main EVA repo
```

### **How to Know You're in the WRONG Repo:**
- Remote URL mentions "realtime" or "experiments"
- railway.json mentions realtime_app
- No core/eva.py file
- Different file structure

---

## 🎯 **For AI Assistants (Claude Code)**

### **MANDATORY Pre-Push Verification:**
1. **Check repository identity**
   ```bash
   git remote -v
   pwd
   ls -la
   ```

2. **Verify deployment target**
   ```bash
   cat railway.json
   ```

3. **Confirm with user**
   - "I'm about to push to eva_web production repo"
   - "This will deploy to evaweb-production.up.railway.app"
   - "Are you sure this is correct?"

4. **NEVER assume repository context**
   - Always verify which repo you're working in
   - Don't mix features from different projects
   - When in doubt, ASK THE USER

---

## 📚 **Learning from This Mistake**

### **Root Causes:**
1. **Context confusion** - Mixed up repository purposes
2. **No verification** - Didn't check deployment target
3. **Feature mixing** - Combined unrelated changes
4. **No testing** - Pushed without local verification

### **Prevention:**
1. **Clear context** - Always verify repository first
2. **Mandatory checks** - Use safety checklist
3. **Separate concerns** - Keep features in correct repos
4. **Test everything** - Local verification before push

---

## 🚨 **REMEMBER: This is Production!**

Every push to this repository affects a live application that users depend on. Treat it with the respect and caution it deserves.

**When in doubt, DON'T PUSH. ASK FIRST.**

---

**Document Created**: June 5, 2025  
**Reason**: Emergency rollback required due to incorrect repository push  
**Status**: MANDATORY READING before any git operations