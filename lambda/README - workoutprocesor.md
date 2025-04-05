# AWS Lambda Workout Data Pipeline - README

## **🚀 Overview**

This project implements a modern **serverless data pipeline** using **AWS Lambda, S3, SNS, and ECS** to automate the processing of workout data. The pipeline:

1. **Monitors an S3 bucket** for new workout CSV files.
2. **Processes the new records** to clean and identify unique workout data.
3. **Publishes a notification via AWS SNS** when processing is complete.
4. **Uses AWS ECS with a Dockerized Lambda function** for streamlined deployment.

---

## **⚙️ Architectural Design**

### **🔹 AWS Services Used**

- **AWS Lambda**: Runs the serverless function that processes workout data.
- **Amazon S3**: Triggers Lambda upon file upload.
- **Amazon SNS**: Sends notifications after processing.
- **Amazon ECS (Elastic Container Service)**: Hosts the containerized Lambda function.
- **IAM Roles & Policies**: Manage permissions for Lambda, S3, and SNS.

### **🔹 Workflow Overview**

1. **User uploads a CSV file to the S3 bucket.**
2. **S3 triggers the Lambda function**, passing the event with the file details.
3. **Lambda processes the workout data**, identifying new records.
4. **A notification is sent to SNS** to indicate processing completion.
5. **Processed records can be stored, analyzed, or integrated into downstream systems.**

---

## **📂 Project Structure**

```bash
/workout-data-pipeline/
│── Dockerfile                      # Container definition for Lambda
│── workout_processor.py            # Main Lambda processing logic
│── storage.py                       # Handles data retrieval from S3
│── test_event.json                  # Sample event payload for local testing
│── requirements.txt                  # Python dependencies
│── deploy.sh                        # Deployment script for updating Lambda
│── README.md                        # Project documentation
```

---

## **🔨 Setup & Deployment Guide**

### **1️⃣ Initial AWS Infrastructure Setup**

Before deploying, ensure you have:

- An **S3 bucket** with a notification trigger for `s3:ObjectCreated:*` events.
- An **SNS topic** (`workout-notifications`) for processing notifications.
- An **IAM role for Lambda** with permissions to access S3, SNS, and CloudWatch.

Run the following to verify SNS:

```bash
aws sns list-topics
aws sns get-topic-attributes --topic-arn arn:aws:sns:us-west-2:533267082184:workout-notifications
```

---

### **2️⃣ Build & Deploy Lambda Using Docker**

#### **Step 1: Build the Docker Image**

Use `docker buildx` (needed for Apple Silicon M1/M2 chips):

```bash
docker buildx build --platform linux/amd64 -t workout-processor .
```

#### **Step 2: Tag & Push to AWS ECS**

Identify the latest image:

```bash
docker images
```

Tag the correct image:

```bash
docker tag <IMAGE_ID> 533267082184.dkr.ecr.us-west-2.amazonaws.com/workout-processor:latest
```

Push to AWS ECR:

```bash
docker push 533267082184.dkr.ecr.us-west-2.amazonaws.com/workout-processor:latest
```

#### **Step 3: Deploy to AWS Lambda**

Update the Lambda function with the new container:

```bash
aws lambda update-function-code --function-name workout-processor \
    --image-uri 533267082184.dkr.ecr.us-west-2.amazonaws.com/workout-processor:latest
```

Verify deployment:

```bash
aws lambda get-function --function-name workout-processor
```

---

### **3️⃣ Testing & Debugging**

#### **Manual Invocation**

Invoke Lambda with a test event:

```bash
aws lambda invoke --function-name workout-processor --payload fileb://test_event.json response.json
```

Check the output:

```bash
cat response.json
```

#### **Upload a CSV to S3 to Trigger Lambda**

Manually upload a test CSV:

```bash
aws s3 cp test.csv s3://my-bucket/
```

#### **Check CloudWatch Logs for Errors**

```bash
aws logs describe-log-groups
aws logs tail /aws/lambda/workout-processor --follow
```

---

## **🛠 Troubleshooting & Debugging Checklist**

| **Issue**                         | **Fix**                                                                                                 |
| --------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Lambda not triggered              | Check S3 event configuration using `aws s3api get-bucket-notification-configuration --bucket my-bucket` |
| SNS error: "Topic does not exist" | Verify `aws sns list-topics` and ensure Lambda's IAM role has `sns:Publish` permissions                 |
| No logs appearing in CloudWatch   | Check `aws lambda get-function --function-name workout-processor` and verify logging is enabled         |
| Docker build failing on Mac       | Use `docker buildx build --platform linux/amd64` to ensure compatibility with AWS                       |

---

## **📌 Notes & Best Practices**

1. **Use versioned tags (`v1`, `v2`) instead of `:latest` for production stability.**
2. **Ensure environment variables are set for S3, SNS, and other dependencies.**
3. **Always test Lambda manually (`aws lambda invoke`) before deploying to production.**

---

## **🎉 Congratulations!**

You have successfully deployed a **serverless data pipeline** for workout data processing using **AWS Lambda, S3, SNS, and ECS**. 🚀

For future improvements, consider:
✅ Adding **DynamoDB or S3 storage** for processed records
✅ Implementing **CloudFormation or Terraform** for infrastructure automation
✅ Extending **CI/CD automation** using GitHub Actions

Happy coding! 🎯

