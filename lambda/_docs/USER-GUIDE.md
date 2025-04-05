# USER GUIDE

## **📌 Overview**

This guide provides step-by-step instructions for setting up, using, and troubleshooting the **Workout Data Processing Pipeline**. The system is designed to process workout data automatically using **AWS Lambda, S3, SNS, and ECS**.

---

## **🛠 Installation Guide**

### **1️⃣ Prerequisites**

Before getting started, ensure you have the following:

- **AWS CLI** installed and configured (`aws configure`)
- **Docker** installed for containerized Lambda deployment
- **Python 3.x** installed
- **Git** installed

### **2️⃣ Cloning the Repository**

```bash
git clone https://github.com/your-repo/workout-data-pipeline.git
cd workout-data-pipeline
```

### **3️⃣ Setting Up AWS Resources**

#### **Create an S3 Bucket for Workout Data**

```bash
aws s3 mb s3://my-workout-data-bucket
```

#### **Create an SNS Topic for Notifications**

```bash
aws sns create-topic --name workout-notifications
```

#### **Configure Lambda Execution Role**

Ensure your Lambda function has:

- `s3:GetObject` permission for reading from S3
- `sns:Publish` permission for sending notifications
- `logs:CreateLogStream` for CloudWatch logging

#### **Deploy Initial Lambda Function**

```bash
docker buildx build --platform linux/amd64 -t workout-processor .
docker tag <IMAGE_ID> 533267082184.dkr.ecr.us-west-2.amazonaws.com/workout-processor:latest
docker push 533267082184.dkr.ecr.us-west-2.amazonaws.com/workout-processor:latest
aws lambda update-function-code --function-name workout-processor --image-uri 533267082184.dkr.ecr.us-west-2.amazonaws.com/workout-processor:latest
```

---

## **🚀 Feature Tutorials**

### **1️⃣ Uploading a Workout CSV File**

To process a new workout dataset, upload a CSV file to the S3 bucket:

```bash
aws s3 cp sample_workout.csv s3://my-workout-data-bucket/
```

This triggers the Lambda function, which:

- Extracts workout records from the CSV
- Cleans and identifies new records
- Sends a notification to SNS

### **2️⃣ Checking Processing Status**

#### **Manually Invoke Lambda**

```bash
aws lambda invoke --function-name workout-processor --payload fileb://test_event.json response.json
```

#### **Check SNS Notifications**

```bash
aws sns list-subscriptions-by-topic --topic-arn arn:aws:sns:us-west-2:533267082184:workout-notifications
```

#### **Monitor CloudWatch Logs**

```bash
aws logs tail /aws/lambda/workout-processor --follow
```

---

## **🛠 Troubleshooting**

| **Issue**                         | **Possible Fix**                                                                                                             |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Lambda not triggered              | Check S3 event notification configuration: `aws s3api get-bucket-notification-configuration --bucket my-workout-data-bucket` |
| SNS error: "Topic does not exist" | Verify SNS topic existence: `aws sns list-topics`                                                                            |
| No logs in CloudWatch             | Ensure logging is enabled: `aws logs describe-log-groups`                                                                    |
| Docker build failing              | Use `docker buildx build --platform linux/amd64` for AWS Lambda compatibility                                                |

---

## **❓ FAQs**

### **1️⃣ How do I update the Lambda function with new code?**

Rebuild and push the Docker image:

```bash
docker buildx build --platform linux/amd64 -t workout-processor .
docker tag <IMAGE_ID> 533267082184.dkr.ecr.us-west-2.amazonaws.com/workout-processor:latest
docker push 533267082184.dkr.ecr.us-west-2.amazonaws.com/workout-processor:latest
aws lambda update-function-code --function-name workout-processor --image-uri 533267082184.dkr.ecr.us-west-2.amazonaws.com/workout-processor:latest
```

### **2️⃣ How can I verify that the pipeline is working?**

- Upload a CSV to S3 and check CloudWatch logs.
- Subscribe an email to SNS and verify notifications.

### **3️⃣ How do I manually trigger the Lambda function?**

```bash
aws lambda invoke --function-name workout-processor --payload fileb://test_event.json response.json
```

---

## **🚀 Next Steps & Enhancements**

### **Short-Term Improvements**

✅ **Add API Gateway** – Enable external systems to trigger processing. ✅ **Improve Error Handling** – Implement DLQs for failed processing attempts. ✅ **Enhance Logging & Metrics** – Integrate CloudWatch insights for detailed analytics.

### **Long-Term Enhancements**

📌 **Real-Time Data Processing** – Utilize Kinesis or EventBridge for streaming data. 📌 **User Dashboard** – Build a frontend to visualize processed workout data. 📌 **Machine Learning Integration** – Analyze workout trends and recommend optimizations.

---

## **🎉 Conclusion**

This **User Guide** provides everything you need to set up, use, and troubleshoot the **Workout Data Processing Pipeline**. With continuous improvements, this system will become even more efficient and feature-rich in the future.

🚀 **Happy coding and fitness tracking!**

