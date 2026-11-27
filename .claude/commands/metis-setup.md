---
description: Guide local METIS API credential setup and check whether the required keys are present
allowed-tools: Bash, Read
---

# METIS Setup

Read the setup section of `automation/metis/README.md`. Ask the user to enter missing
values directly in the repo-root `.env` in their editor. Never request credential values in
chat or print the contents of `.env`.

From the repository root, run `python3 scripts/metis_api.py credentials` to check for missing
keys. Use `py -X utf8` on Windows if `python3` is unavailable. Once all keys are present, verify
the login with `python3 scripts/metis_api.py request GET /auth/whoami` and report the account
name on success or the login status on failure.
