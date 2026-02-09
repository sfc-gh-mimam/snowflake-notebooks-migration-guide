# SPCS Deployment Friction Report

## Overview

This document summarizes friction points encountered while deploying a Streamlit app to Snowpark Container Services (SPCS). These findings are intended to inform product and documentation improvements.

**Deployment**: Snowflake Notebooks Migration Guide (Streamlit app)  
**Date**: February 2026  
**Account**: PM-PM_AWS_US_WEST_2  

---

## Friction Points Summary

| Issue | Type | Severity | Time Lost | Fix Complexity |
|-------|------|----------|-----------|----------------|
| Username mismatch with Okta SSO | Product | High | ~45 min | Low |
| Browser auth loop (5+ windows) | Product | High | ~30 min | Low |
| Docker platform architecture | Docs | Medium | ~15 min | Low |
| SPCS service spec syntax | Docs | Medium | ~10 min | Low |

---

## Detailed Findings

### 1. Snow CLI Authentication - Username Mismatch (HIGH PRIORITY)

#### Problem
When using `externalbrowser` authentication with Okta SSO, if the user has multiple Snowflake users in the same account, the authentication fails with a cryptic error.

**Scenario:**
- User has two accounts in PM org:
  - `MIMAM` - linked to Okta SSO (muzz.imam@snowflake.com)
  - `MUZZIMAM` - uses password/passkey, has ACCOUNTADMIN
- Config file had `user = "muzzimam"`
- Okta SSO redirected to `MIMAM`
- Result: Authentication mismatch

**Current Error Message:**
```
Invalid connection configuration. 250001 (08001): None: Failed to connect to 
DB: PM-PM_AWS_US_WEST_2.snowflakecomputing.com:443. The user you were trying 
to authenticate as differs from the user currently logged in at the IDP.
```

**Issues with current behavior:**
1. Error doesn't specify WHICH users mismatched (expected vs actual)
2. No guidance on how to fix
3. Error code `250001` is not searchable/documented

#### Recommended Fix

**Improved Error Message:**
```
Authentication failed: Username mismatch

  Config expects:  MUZZIMAM
  IDP returned:    MIMAM

To fix, update your ~/.snowflake/config.toml:
  user = "MIMAM"

Or authenticate with a different account if you intended to use MUZZIMAM.
```

**Implementation:** In the Snowflake Python connector or Snow CLI, when catching error code 390191 (IDP user mismatch), parse the response to extract both usernames and provide actionable guidance.

---

### 2. External Browser Authentication Loop (HIGH PRIORITY)

#### Problem
When authentication fails due to username mismatch, the browser opens 5+ times in rapid succession before finally failing. Each attempt triggers Duo/MFA, creating a terrible user experience.

**Observed Behavior:**
1. Browser window opens → Okta login → Duo push
2. Fails silently
3. Browser window opens again → Okta login → Duo push
4. Repeat 3-5 more times
5. Finally shows error

#### Recommended Fix

1. **Fail fast**: After first authentication attempt fails with user mismatch error, do not retry
2. **Add retry limit**: Maximum 1-2 retries for transient errors, 0 retries for identity mismatch
3. **Show error immediately**: Don't make user wait through multiple Duo pushes

**Pseudocode:**
```python
def authenticate_external_browser():
    for attempt in range(MAX_RETRIES):
        try:
            result = do_browser_auth()
            return result
        except UserMismatchError as e:
            # Don't retry - this is a config issue, not transient
            raise AuthenticationError(
                f"Username mismatch: config has '{e.expected}' but IDP returned '{e.actual}'"
            )
        except TransientError:
            if attempt < MAX_RETRIES - 1:
                continue
            raise
```

---

### 3. Docker Platform Architecture Requirement (MEDIUM)

#### Problem
Building Docker images on Mac M-series (ARM64) produces images that SPCS rejects. The error only appears at service creation time, after pushing the image.

**Error:**
```
397013 (0A000): SPCS only supports image for amd64 architecture. 
Please rebuild your image with '--platform linux/amd64' option
```

#### Recommended Fix

**Documentation Update:** Add prominent warning in SPCS quickstart guides:

```markdown
> ⚠️ **Important for Mac M-series users**
> 
> SPCS requires `linux/amd64` images. If building on Apple Silicon (M1/M2/M3):
> ```bash
> docker build --platform linux/amd64 -t myimage .
> ```
```

**Product Enhancement (optional):** `snow spcs image-repository list-images` could show architecture and warn if non-amd64 images are detected.

---

### 4. SPCS Service Spec Syntax (MEDIUM)

#### Problem
The service specification YAML syntax for `readinessProbe` differs from Kubernetes conventions, causing confusion.

**What didn't work (Kubernetes-style):**
```yaml
readinessProbe:
  httpGet:
    path: /_stcore/health
    port: 8501
```

**What works (SPCS-style):**
```yaml
readinessProbe:
  port: 8501
  path: /_stcore/health
```

#### Recommended Fix

**Documentation Update:** Add complete, working examples for common service specs including:
- Streamlit apps
- FastAPI services  
- Health check configurations
- Resource limits

---

## Impact Assessment

### Time Lost
- Total deployment time: ~3 hours
- Time lost to friction: ~1.5 hours (50%)
- Primary cause: Authentication issues (~75% of friction time)

### User Experience Impact
- Browser loop with Duo pushes: Frustrating, feels broken
- Cryptic error messages: Required searching docs/forums
- Platform mismatch: Wasted time pushing wrong image

---

## Recommendations Priority

### P0 - Quick Wins (High Impact, Low Effort)
1. **Improve auth error message** - Include expected vs actual username
2. **Stop browser retry loop** - Fail immediately on identity mismatch

### P1 - Documentation (Medium Impact, Low Effort)
3. **Add platform warning** - Prominent note about linux/amd64 requirement
4. **Add service spec examples** - Complete working YAML for common apps

### P2 - Nice to Have
5. **Pre-flight validation** - `snow spcs` could check image architecture before push
6. **Config validation** - Warn if externalbrowser auth might have user conflicts

---

## Appendix: Environment Details

- **Snow CLI Version**: 3.14.0
- **Docker Version**: 29.2.0
- **Platform**: macOS Darwin 25.2.0 (Apple Silicon)
- **Authentication**: Okta SSO with Duo MFA
- **Snowflake Account**: PM-PM_AWS_US_WEST_2
