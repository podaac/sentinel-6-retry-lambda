# Sentinel-6 Retry Lambda

This Lambda function filters a list of "granules" from an input event payload. It cross-references the `payload.granules` list against a `fail` list and returns only the granules that contain files that failed.

## Tech Stack
* **Language:** Python 3.13
* **Dependency Management:** Poetry 2.0 (PEP 621 compliant)
* **Environment Management:** pyenv
* **Testing:** pytest
* **Deployment:** GitHub Actions + Terraform

---

## Local Setup

### 1. Python Environment
This project requires Python 3.13. Use `pyenv` to manage versions:

```bash
# Install 3.13 if you don't have it
pyenv install 3.13.0

# Set it locally for this project
pyenv local 3.13.0
```

### 2. Install Dependencies
We use Poetry 2.0. To install the project and its development dependencies (like `pytest`):

```bash
# Tell poetry to use your pyenv version
poetry env use $(pyenv which python)

# Install all dependencies
poetry sync
```

---

## Testing
We use `pytest` for unit testing. The tests verify that the filtering logic correctly identifies failed granules and handles empty edge cases.

### Run Tests
```bash
poetry run pytest -v
```

### Expected Result
When you run the tests, you should see an output similar to this:

```text
============================= test session starts ==============================
platform darwin -- Python 3.13.0, pytest-8.x.x, pluggy-1.x.x
rootdir: /path/to/sentinel-6-retry-lambda
collected 2 items

tests/test_handler.py::test_filter_failed_granules_success PASSED        [ 50%]
tests/test_handler.py::test_filter_failed_granules_empty PASSED          [100%]

============================== 2 passed in 0.02s ===============================
```

---

## Building the Deployment Zip (Local)
While GitHub Actions automates this, you can build the `.zip` manually for testing or manual AWS console uploads.

> **Note:** AWS Lambda requires all dependencies to be at the root of the `.zip`.

```bash
# 1. Clean up old builds
rm -rf dist_bundle lambda_package.zip

# 2. Create bundle folder
mkdir dist_bundle

# 3. Export dependencies to requirements.txt
# (Ensure poetry-plugin-export is installed)
poetry export --without-hashes --format=requirements.txt > requirements.txt

# 4. Install dependencies into the bundle folder
pip install -r requirements.txt -t dist_bundle

# 5. Copy the package code (contents only) to the root
cp -r src/sentinel_6_retry_lambda/. dist_bundle/

# 6. Zip everything up
cd dist_bundle && zip -r ../lambda_package.zip .
```

---

## Deployment Logic
The flow of code from your machine to AWS is as follows:

1.  **Develop:** Write code and tests locally.
2.  **Tag:** Create a git tag (e.g., `v1.0.0-beta.1`).
3.  **CI/CD:** GitHub Actions runs tests and builds the `lambda_package.zip`.
4.  **Artifact:** The zip is uploaded to the GitHub Release.
5.  **Terraform:** Run `terraform apply` to update the Lambda function using the new zip.

---

## Configuration
The Lambda expects an event in the following format:

```json
{
  "fail": [
    { "package_name": "filename_1.zip" }
  ],
  "payload": {
    "granules": [
      {
        "files": [{ "name": "filename_1.zip" }],
        "id": "example-id"
      }
    ]
  }
}
```