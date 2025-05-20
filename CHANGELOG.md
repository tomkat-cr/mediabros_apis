# CHANGELOG

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/) and [Keep a Changelog](http://keepachangelog.com/).



## Unreleased
---

### New

### Changes

### Fixes

### Breaks


## 1.1.0 (2025-05-20)
---

### New
Add monitor-exchange-rates to Pipfile
Add bcv-exchange-rates to Pipfile (replaces Vercel API)
Add cop-exchange-rates to Pipfile (replaces Vercel API)
Add CHANGELOG and Makefile
Add usage instructions to README.md

### Changes
Update Python version to 3.11

### Fixes
Update dependencies to latest versions to fix Snyk alerts.


## 1.0.0 (2025-05-14)
---

### Changes
Update OpenAO model and API call (2023-02-04)


## 0.1.8 (2023-03-29)
---

### Fixes
Chalice stages config renamed from dev to api
Pipenv run instead of shell to avoid need of Ctrl-D to exit
Pipfile updated


## 0.1.7 (2023-02-04)
---

### New
Support to deploy as a AWS Lambda function


## 0.1.6 (2023-02-02)
---

### New
Fly.io deployment


## 0.1.5 (2023-02-01)
---

### Fixes
Endpoints removed were restored
Print replaced by log_debug


## 0.1.4 (2023-01-31)
---

### Fixes
Builds/src with a single file instead of *.py
Remove endpoint without debug to have 12 func
Remove /query_params to have 12 funcs
Remove /pget to have 12 funcs on vercel
Remove /users/me to have 12 funcs on vercel


## 0.1.3 (2023-01-30)
---

### New
JWT token auth for /ai /codex

### Fixes
Credentials print removed


## 0.1.2 (2023-01-25)
---

### New
Add /codex endpoint
Add /crypto/symbol/currency endpoint
Add /ai POST endpoint
Add /ai validation

### Fixes
/ai response with no debug in plain text
CLI processing
README newlines


## 0.1.0 (2023-01-24)
---

### New
Add all endpoints, including /ai to call OpenAI