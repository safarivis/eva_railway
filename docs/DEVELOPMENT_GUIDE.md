# EVA Agent Development Guide

## 📁 **CRITICAL: File Management Rules**

### ⚠️ TEMPORARY FILES POLICY
**NEVER place temporary files in the project root!** Always use the temp folder structure:

```
/temp/
  ├── tests/         # Test files and debugging scripts  
  ├── backups/       # Temporary backups during development
  ├── docs/          # Draft documentation
  ├── logs/          # Debug logs and output files
  └── cleanup/       # Files to delete after completion
```

**✅ DO:**
- Create `/temp/` folder for ALL temporary files
- Use descriptive names: `temp/tests/debug-zep-integration-2024-06-02.py`
- Delete temp files when development task is complete
- Document temp file purpose in development notes

**❌ DON'T:**
- Create `.test.py`, `.debug.py`, `.tmp` files in project root
- Leave temporary files scattered throughout the project
- Create files without clear cleanup plan

**🧹 CLEANUP ROUTINE:**
```bash
# At end of each development session:
rm -rf temp/tests/        # Remove temp test files
rm -rf temp/backups/      # Remove temp backups
rm -rf temp/logs/         # Remove debug logs
rm -rf temp/cleanup/      # Remove debugging files
git status                # Ensure no temp files tracked
```

---

## Development Best Practices

### 🔧 Testing New Features
1. Create test files in `temp/tests/`
2. Use descriptive names with dates
3. Document what you're testing
4. Clean up after completion

### 🔒 Security Considerations
- Never commit API keys or sensitive data
- Use environment variables for configuration
- Keep voice recordings in secure directories
- Test with non-production data when possible

### 📝 Documentation
- Update relevant docs when adding features
- Document breaking changes
- Keep examples current
- Add troubleshooting sections

### 🚀 Deployment
- Test locally before deploying
- Use the deployment scripts in `/scripts/`
- Verify environment variables are set
- Check logs for errors after deployment

---

This guide explains how to work on EVA safely and maintain code quality.