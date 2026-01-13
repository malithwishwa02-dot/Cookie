# GitHub Agent Task: Forensic Verification

The stealth check agent logic is located in `tests/verify_stealth.py`.

Due to repository permission restrictions, the automated GitHub Action workflow file is provided here for manual implementation.

## Workflow Definition

To enable the automated agent, create `.github/workflows/stealth_check.yml` in your repository with the following content:

```yaml
name: Oblivion Stealth Verification

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  verify-stealth:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        
    - name: Install Dependencies
      run: |
        pip install -r cookie_forge_suite/requirements.txt
        
    - name: Generate Test Profile
      run: |
        # Generate a quick profile for testing
        mkdir -p test_profile
        cd cookie_forge_suite
        python3 oblivion_core.py --profile ../test_profile --quick --age 120
        
    - name: Run Forensic Verification (Audit Mode)
      run: |
        python3 tests/verify_stealth.py --profile test_profile
        
    - name: Run Forensic Verification (Fix Mode)
      if: failure()
      run: |
        echo "Detection vectors found. Initiating auto-remediation..."
        python3 tests/verify_stealth.py --profile test_profile --fix
        
    - name: Validate Fixes
      if: failure()
      run: |
        python3 tests/verify_stealth.py --profile test_profile
```
