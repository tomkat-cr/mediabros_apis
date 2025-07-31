# CHANGELOG

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/) and [Keep a Changelog](http://keepachangelog.com/).



## Unreleased
---

### New

### Changes

### Fixes

### Breaks


## 1.1.1 (2025-07-31)
---

### Changes
- Enhance README with detailed setup instructions and API documentation in both English and Spanish.
- ".gitignore" to include IDE configurations.
- Modify .nvmrc for Node.js version 20
- Update Python version 3.13


## 1.1.0 (2025-07-28)
---

### New
- Add the /usdveb_monitor endpoint to return the USD/VEB rate from the MonitorDolarVenezuela Exchange API.
- Add the /usdveb_full endpoint to return both the official BCV and the MonitorDolarVenezuela USD/VEB exchange rates.
- Add the BANK_PERCENT_INCREASE_OFFICIAL and BANK_PERCENT_INCREASE_GOOGLE envvars to configure the bank percent increase for transfers in the USD/COP exchange rates.
- Add monitor-exchange-rates to Pipfile
- Add bcv-exchange-rates to Pipfile (replaces Vercel API)
- Add cop-exchange-rates to Pipfile (replaces Vercel API)
- Add CHANGELOG and Makefile
- Add usage instructions to README.md
- Add STS deployment method.
- Add integration tests.
- Add CHALICE_DEPLOYMENT envvar. Chalice deployment must be enabled with the assignment CHALICE_DEPLOYMENT="1". STS deployment is the default method.
- For the Chalice deployment, the external github repos "bcv", "cop" and "monitor" exchange-rates are not installed with pipenv install, but copied to the "vendor" directory because Chalice deploy won't recognice its versions.
- Add CHROMEDRIVER_INCLUDE envvar. Chrome and Chromedriver download must be enabled by the assignment CHROMEDRIVER_INCLUDE="1".
- Add CHROME_PATH and CHROMEDRIVER_PATH envvar to config.json to address the "Selenium error: Message: Unable to obtain driver for chrome"
- Add beautifulsoup4, cloudscraper, selenium because tthe "vendor" directory change for external github repos.
- Add "update_packages_only" to Makefile to build from the external github repos and download the chrome driver to vendor directory.
- Add documentation files based on the Memory Bank template [GS-208].

### Changes
- Rename the /usdvef endpoint to /usdveb. "/usdvef" is deprecated and removed.
- The /usdveb endpoint only returns the official BCV USD/Bs rate. No alternative/parallel exchange rate is provided.
- Update Python version to 3.13
- Replace deprecated "passlib" with "werkzeug" for password encryption.

### Fixes
- Update dependencies to latest versions to fix Snyk alerts.
- Replace eventual Github PAT in Pipfile and requirements.txt.
- "make deploy_prod" by creating the missing ".chalice/policy-prod.json" file.
- Proper error handling to veb_monitor().
- Fix: convert debug param to string before comparison in endpoint handlers

### Breaks
- The /usdveb command does not include the DolarToday data and API call because it was deprecated.
- Remove passlib dependency.


## 1.0.0 (2025-05-14)
---

### Changes
- Update OpenAI model and API call (2023-02-04)


## 0.1.8 (2023-03-29)
---

### Fixes
- Chalice stages config renamed from dev to api
- Pipenv run instead of shell to avoid need of Ctrl-D to exit
- Pipfile updated


## 0.1.7 (2023-02-04)
---

### New
- Support to deploy as a AWS Lambda function


## 0.1.6 (2023-02-02)
---

### New
- Fly.io deployment


## 0.1.5 (2023-02-01)
---

### Fixes
- Endpoints removed were restored
- Print replaced by log_debug


## 0.1.4 (2023-01-31)
---

### Fixes
- Builds/src with a single file instead of *.py
- Remove endpoint without debug to have 12 func
- Remove /query_params to have 12 funcs
- Remove /pget to have 12 funcs on vercel
- Remove /users/me to have 12 funcs on vercel


## 0.1.3 (2023-01-30)
---

### New
- JWT token auth for /ai /codex

### Fixes
- Credentials print removed


## 0.1.2 (2023-01-25)
---

### New
- Add /codex endpoint
- Add /crypto/symbol/currency endpoint
- Add /ai POST endpoint
- Add /ai validation

### Fixes
- /ai response with no debug in plain text
- CLI processing
- README newlines


## 0.1.0 (2023-01-24)
---

### New
- Add all endpoints, including /ai to call OpenAI