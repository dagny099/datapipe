# DEVELOPMENT GUIDE

## **📌 Technical Architecture**

### **🔹 Overview**
This project is a **serverless data pipeline** that processes workout data using **AWS Lambda, S3, SNS, and ECS**. The system is designed to:
1. **Monitor an S3 bucket** for new workout CSV files.
2. **Trigger a Lambda function** to process and clean the data.
3. **Identify and store new workout records**.
4. **Send notifications via AWS SNS** upon successful processing.
5. **Use AWS ECS with Docker** to manage Lambda deployment.

### **🔹 Core Components & Services**
| **Component** | **Description** |
|--------------|----------------|
| **AWS Lambda** | Serverless compute function to process workout data. |
| **Amazon S3** | Storage bucket where workout CSV files are uploaded. |
| **Amazon SNS** | Sends notifications when new data is processed. |
| **Amazon ECS** | Container registry for storing the Dockerized Lambda function. |
| **IAM Roles & Policies** | Securely manages access between AWS services. |

### **🔹 Workflow**
1. **File Upload to S3**: A user uploads a workout data file (`.csv`).
2. **S3 Event Trigger**: The upload event triggers the Lambda function.
3. **Lambda Processing**:
   - Extracts and validates the file.
   - Cleans and identifies new records.
   - Sends an SNS notification upon completion.
4. **Notification & Logging**:
   - SNS sends a summary of the processed records.
   - Logs are stored in AWS CloudWatch for monitoring and debugging.

---

## **🛠 Development Workflow**

### **1️⃣ Setting Up the Environment**
#### **Prerequisites**
- Install **Docker**
- Install **AWS CLI** & configure credentials
- Install **Python 3.x** & dependencies

#### **Cloning the Repository**
```bash
git clone https://github.com/your-repo/workout-data-pipeline.git
cd workout-data-pipeline
```

#### **Setting Up AWS Credentials**
```bash
aws configure
```

### **2️⃣ Development Cycle**
| **Step** | **Command** | **Description** |
|---------|------------|----------------|
| **Make changes to Lambda code** | Edit `workout_processor.py` | Modify data processing logic. |
| **Build Docker image** | `docker buildx build --platform linux/amd64 -t workout-processor .` | Ensures compatibility with AWS Lambda. |
| **Tag latest image** | `docker tag <IMAGE_ID> 533267082184.dkr.ecr.us-west-2.amazonaws.com/workout-processor:latest` | Tags the Docker image for deployment. |
| **Push image to AWS ECR** | `docker push 533267082184.dkr.ecr.us-west-2.amazonaws.com/workout-processor:latest` | Uploads the container to AWS. |
| **Deploy to AWS Lambda** | `aws lambda update-function-code --function-name workout-processor --image-uri 533267082184.dkr.ecr.us-west-2.amazonaws.com/workout-processor:latest` | Deploys the new Lambda function. |
| **Trigger Lambda (manual test)** | `aws lambda invoke --function-name workout-processor --payload fileb://test_event.json response.json` | Verifies Lambda execution. |
| **Upload test file to S3** | `aws s3 cp test.csv s3://my-bucket/` | Tests end-to-end flow. |

---

## **✅ Testing Procedures**

### **1️⃣ Unit Testing**
**Run tests locally using pytest:**
```bash
pytest -v tests/
```

### **2️⃣ Manual Lambda Invocation**
Test the function independently before S3 integration:
```bash
aws lambda invoke --function-name workout-processor --payload fileb://test_event.json response.json
cat response.json
```

### **3️⃣ Full Pipeline Test**
1. Upload a test CSV file:
   ```bash
   aws s3 cp test.csv s3://my-bucket/
   ```
2. Check if Lambda is triggered:
   ```bash
   aws logs tail /aws/lambda/workout-processor --follow
   ```
3. Verify SNS notification:
   ```bash
   aws sns list-subscriptions-by-topic --topic-arn arn:aws:sns:us-west-2:533267082184:workout-notifications
   ```

---

## **🚀 Build & Deployment Process**

### **1️⃣ Building the Docker Image**
```bash
docker buildx build --platform linux/amd64 -t workout-processor .
```

### **2️⃣ Tagging & Pushing to AWS ECS**
```bash
docker tag <IMAGE_ID> 533267082184.dkr.ecr.us-west-2.amazonaws.com/workout-processor:latest
docker push 533267082184.dkr.ecr.us-west-2.amazonaws.com/workout-processor:latest
```

### **3️⃣ Updating AWS Lambda with the New Container**
```bash
aws lambda update-function-code --function-name workout-processor \
    --image-uri 533267082184.dkr.ecr.us-west-2.amazonaws.com/workout-processor:latest
```

### **4️⃣ Verifying Deployment**
```bash
aws lambda get-function --function-name workout-processor
```

---

## **🔍 Troubleshooting**

| **Issue** | **Fix** |
|-----------|--------|
| Lambda not triggered | Check S3 event config: `aws s3api get-bucket-notification-configuration --bucket my-bucket` |
| SNS error: "Topic does not exist" | Verify `aws sns list-topics` & ensure Lambda IAM role has `sns:Publish` permissions. |
| No logs appearing | Check Lambda logs: `aws logs tail /aws/lambda/workout-processor --follow` |
| Docker build issues on Mac | Use `docker buildx build --platform linux/amd64` |

---

## **🎯 Best Practices**

- **Use tagged versions for stability (`v1`, `v2` instead of `latest`).**
- **Set up CloudFormation or Terraform** for infrastructure automation.
- **Use CI/CD pipelines (GitHub Actions) to automate testing & deployment.**
- **Enable monitoring with CloudWatch to track Lambda execution metrics.**

---

## **🎉 Congratulations!**
You now have a fully operational **serverless data pipeline** with AWS Lambda, S3, SNS, and ECS. 🚀

Happy coding! 🎯

