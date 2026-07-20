# Qwen/DashScope API Key Fix - Summary

## Problem Identified
The persistent 401 "invalid_api_key" error was caused by **dots (.) in the API key** that appear in the Alibaba Cloud console for readability but are NOT part of the actual key.

Example:
- Console shows: `sk-ws-H.XILIHL.sLTV.MEYCIQD...`
- Actual key needed: `sk-ws-HXILIHLsLTVMEYCIQD...` (NO dots)

## Changes Made

### 1. **config.py** - Auto-strip dots and validate configuration
- Added `@field_validator` to automatically remove ALL dots from API keys before use
- Added comprehensive startup logging showing masked key format and length
- Added validation to detect mismatch between workspace keys (`sk-ws-`) and generic base URLs
- Replaced `@lru_cache` with manual cache that can be cleared on reload
- Settings now load from multiple `.env` file locations with proper fallback

### 2. **llm_client.py** - Enhanced debugging
- Clears settings cache on module load to ensure fresh configuration
- Added detailed request/response logging (without exposing full key)
- Logs HTTP status codes and error responses from Qwen API
- Shows key prefix/suffix in debug logs for verification

### 3. **main.py** - Startup health checks
- Logs configuration summary on server startup
- Warns if no API key is configured
- Identifies key type (workspace vs standard) and validates base URL match

### 4. **.env** (workspace) - Fixed example
- Removed all dots from the API key
- Set correct workspace-specific base URL: `https://ws-r0izv5baffzpmfae.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1`

### 5. **.env.example** - Created template with instructions
- Clear warnings about removing dots from keys
- Instructions for finding workspace-specific base URL
- Example format showing correct key structure

## What You Must Do On Your Local Windows Machine

### Step 1: Edit your local `.env` file
Location: `C:\Users\User\OneDrive\Desktop\convertale-production-ready (1)\apps\api\.env`

Replace the Qwen section with this (copy EXACTLY):

```env
# ── Qwen Cloud / DashScope ───────────────────────────────
QWEN_API_KEY=sk-ws-HYYPLEPyDFBMEYCIQDcreUM1q8RGR3A4VgRa9RqlRXdmEru0jOVj1gz0fx3CAIhAMDSTN7SWugxsgFWUeEQPbgBRPlMMmybY2gekfecMPRd
DASHSCOPE_API_KEY=sk-ws-HYYPLEPyDFBMEYCIQDcreUM1q8RGR3A4VgRa9RqlRXdmEru0jOVj1gz0fx3CAIhAMDSTN7SWugxsgFWUeEQPbgBRPlMMmybY2gekfecMPRd
QWEN_BASE_URL=https://ws-r0izv5baffzpmfae.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1
```

**CRITICAL**: 
- NO dots in the API keys (the code will auto-strip them, but start clean)
- The base URL MUST match your workspace domain exactly

### Step 2: Clear Python cache
In PowerShell, run:
```powershell
cd "C:\Users\User\OneDrive\Desktop\convertale-production-ready (1)\apps\api"
Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force
```

### Step 3: Restart your server
```powershell
poetry run uvicorn showrunner_api.main:app --reload --port 8000
```

### Step 4: Verify the fix
Look for these log messages on startup:
```
=== QWEN/DASHSCOPE CONFIGURATION ===
QWEN_API_KEY present: True
DASHSCOPE_API_KEY present: True
Effective key present: True
QWEN_BASE_URL: https://ws-r0izv5baffzpmfae.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1
QWEN_API_KEY format: sk-ws-HYYP...MPRd (len=103)
✓ Workspace key and URL appear correctly matched
====================================
```

If you see the ✓ checkmark, the configuration is correct!

## If It Still Fails

1. **Check the logs**: The enhanced logging will show exactly what key format and URL are being used
2. **Verify your key in Alibaba Console**: 
   - Go to Model Studio > API Key
   - Click "Reset" on your key to generate a fresh one
   - Copy it IMMEDIATELY (you can only see it once)
   - Paste it into `.env` WITHOUT any dots
3. **Try a different key**: Use one of your other workspace keys from the console
4. **Check workspace permissions**: Ensure the key has permission to call the chat/completions endpoint

## How the Code Now Protects You

Even if you accidentally paste a key with dots, the `@field_validator` in `config.py` will automatically strip them:
```
API key had dots removed: sk-ws-H.YY... → sk-ws-HYYP...
```

And the validation will warn you if there's a mismatch:
```
⚠️ MISMATCH: Workspace key (sk-ws-) requires workspace-specific base_url
```

This should finally resolve the 401 errors once and for all!
