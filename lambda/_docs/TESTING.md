# TESTING GUIDE

## **📌 Overview**

This document provides a comprehensive guide on the **testing strategy** for the Workout Data Processing Pipeline, covering **test cases, testing procedures, quality assurance, and bug reporting**.

---

## **🧪 Test Cases**

### **1️⃣ Unit Tests (Function-Level Testing)**

Unit tests validate individual functions and methods.

| **Test Name**                        | **Description**                                                | **File**                    |
| ------------------------------------ | -------------------------------------------------------------- | --------------------------- |
| `test_process_file_with_new_records` | Ensures new records are correctly identified.                  | `test_workout_processor.py` |
| `test_handler_success`               | Validates the Lambda function processes an S3 event correctly. | `test_workout_processor.py` |
| `test_handler_error`                 | Ensures errors are caught and handled gracefully.              | `test_workout_processor.py` |
| `test_version_existing_file`         | Tests versioning logic for file processing.                    | `test_storage.py`           |
| `test_read_write_file`               | Ensures files can be written and read properly in storage.     | `test_storage.py`           |
| `test_get_storage_handler_local`     | Tests the retrieval of the correct storage handler (local).    | `test_storage.py`           |
| `test_get_storage_handler_s3`        | Tests the retrieval of the correct storage handler (S3).       | `test_storage.py`           |

### **2️⃣ Integration Tests (Cross-Component Validation)**

Integration tests validate the interaction between components.

| **Test Name**                  | **Description**                                                   | **File**             |
| ------------------------------ | ----------------------------------------------------------------- | -------------------- |
| `test_full_workflow_new_file`  | Tests the complete workflow, from S3 upload to SNS notification.  | `test_end_to_end.py` |
| `test_workflow_no_new_records` | Ensures pipeline behaves correctly when no new records are found. | `test_end_to_end.py` |
| `test_workflow_invalid_file`   | Checks behavior when an invalid file format is uploaded.          | `test_end_to_end.py` |
| `test_sns_notification`        | Validates that SNS notifications are properly sent.               | `test_end_to_end.py` |

### **3️⃣ Mock-Based Testing**

Mocking is used to isolate dependencies like AWS services.

| **Mock Component**     | **Description**                                       | **File**                    |
| ---------------------- | ----------------------------------------------------- | --------------------------- |
| `MockS3Operations`     | Mocks S3 interactions for unit tests.                 | `mocks.py`                  |
| `ErrorS3Operations`    | Mocks failure scenarios in S3.                        | `mocks.py`                  |
| `mock_s3_client`       | Mocked S3 client used in tests.                       | `test_workout_processor.py` |
| `mock_storage_handler` | Mocked storage handler for verifying data operations. | `test_workout_processor.py` |

---

## **🔍 Testing Procedures**

### **1️⃣ Running Unit Tests**

To execute unit tests, run:

```bash
pytest -v tests/
```

### **2️⃣ Running Integration Tests**

Run full pipeline tests with:

```bash
pytest -v tests/test_end_to_end.py
```

### **3️⃣ Manual Lambda Invocation**

To manually trigger Lambda:

```bash
aws lambda invoke --function-name workout-processor --payload fileb://test_event.json response.json
cat response.json
```

### **4️⃣ End-to-End S3 Trigger Test**

1. Upload a test CSV file to S3:
   ```bash
   aws s3 cp test.csv s3://my-workout-data-bucket/
   ```
2. Monitor CloudWatch logs:
   ```bash
   aws logs tail /aws/lambda/workout-processor --follow
   ```
3. Verify SNS notification:
   ```bash
   aws sns list-subscriptions-by-topic --topic-arn arn:aws:sns:us-west-2:533267082184:workout-notifications
   ```

---

## **✅ Quality Assurance**

### **1️⃣ Code Review Standards**

- All PRs must pass **unit and integration tests** before merging.
- Code should follow **PEP8** and include **docstrings** for maintainability.
- Ensure **mock-based testing** is used where appropriate to isolate dependencies.

### **2️⃣ CI/CD Pipeline Integration**

- Automated tests run on every push via **GitHub Actions**.
- **Code coverage** is reported and should exceed **80%**.
- Failed tests block deployment until resolved.

### **3️⃣ Performance Benchmarking**

- **Lambda execution time** should remain under **5 seconds** for typical workloads.
- **Memory consumption** should be optimized to avoid unnecessary AWS costs.
- CloudWatch **alerts** trigger if processing latency exceeds expected thresholds.

---

## **🐞 Bug Reporting**

### **1️⃣ How to Report a Bug**

If you encounter a bug, please report it using the following format:

```plaintext
**Bug Title:** Lambda function fails on CSV upload

**Description:**
When a new CSV file is uploaded to S3, the Lambda function throws a "FileNotFoundError" despite the file being present.

**Steps to Reproduce:**
1. Upload a CSV file named `workout_data.csv` to the `my-workout-data-bucket`.
2. Check CloudWatch logs for errors.
3. See the traceback mentioning "FileNotFoundError".

**Expected Behavior:**
The function should process the CSV file successfully and send an SNS notification.

**Actual Behavior:**
The function fails with a "FileNotFoundError".

**Environment:**
- AWS Lambda runtime: Python 3.11
- Storage backend: S3
- Deployed via: Docker/ECS

**Logs & Screenshots:**
[Include any logs or screenshots here]

**Possible Solutions:**
[If applicable, suggest possible fixes or areas to investigate]
```

### **2️⃣ Submitting Bug Reports**

- Open a **GitHub issue** in the repository.
- Assign appropriate **labels** (e.g., `bug`, `high-priority`).
- Provide **detailed logs** to expedite debugging.

### **3️⃣ Debugging Checklist**

- ✅ Check **CloudWatch logs** for errors (`aws logs tail /aws/lambda/workout-processor --follow`)
- ✅ Verify **S3 event triggers** (`aws s3api get-bucket-notification-configuration --bucket my-workout-data-bucket`)
- ✅ Ensure **AWS permissions** (`aws iam list-policies`)
- ✅ Test Lambda manually (`aws lambda invoke --function-name workout-processor --payload fileb://test_event.json response.json`)

---

## **🚀 Next Steps & Enhancements**

### **Short-Term Improvements**

✅ **Increase Test Coverage** – Add more edge-case tests. ✅ **Automate Test Artifact Storage** – Store test results in AWS S3 for historical tracking. ✅ **Improve Mocking Accuracy** – Enhance AWS service mocks to simulate real-world behavior.

### **Long-Term Enhancements**

📌 **Load Testing** – Use AWS Lambda Power Tuning to optimize performance. 📌 **Security Testing** – Implement penetration testing against API endpoints. 📌 **Automated Debugging** – Integrate CloudWatch anomaly detection for faster issue resolution.

---

## **🎉 Conclusion**

This **Testing Guide** outlines best practices for ensuring **code quality, reliability, and performance** in the Workout Data Processing Pipeline. With continuous improvements, we aim to **enhance robustness, automate QA, and ensure seamless deployments**.

🚀 **Happy Testing!**

