# API DOCUMENTATION

## **📌 Overview**
This document details the APIs used in the **Workout Data Processing Pipeline**, including **internal APIs, external integrations, message protocols, and data structures**. The system interacts with **AWS services (Lambda, S3, SNS, ECS)** and follows event-driven message passing for seamless execution.

---

## **🛠 Internal APIs**

### **1️⃣ Lambda Handler API**
**Function Name**: `handler(event, context)`

#### **Request Structure**
The Lambda function receives an event payload from an **S3 trigger**. Example event:
```json
{
  "Records": [
    {
      "eventVersion": "2.1",
      "eventSource": "aws:s3",
      "awsRegion": "us-west-2",
      "eventTime": "2025-02-19T00:00:00.000Z",
      "eventName": "ObjectCreated:Put",
      "s3": {
        "bucket": {
          "name": "my-workout-data-bucket"
        },
        "object": {
          "key": "workouts/2025-02-19-workout.csv"
        }
      }
    }
  ]
}
```

#### **Processing Steps**
1. Extracts **S3 bucket name** and **file key** from the event.
2. Downloads the **CSV file** from S3.
3. Parses, cleans, and identifies new workout records.
4. Publishes a **notification to SNS** with the results.

#### **Response Structure**
```json
{
  "statusCode": 200,
  "body": "Workout data processed successfully: 25 new records."
}
```

---

### **2️⃣ SNS Notification API**
**Service**: `AWS Simple Notification Service (SNS)`

#### **Message Structure**
Lambda sends a JSON notification to **workout-processing SNS topic**:
```json
{
  "TopicArn": "arn:aws:sns:us-west-2:533267082184:workout-notifications",
  "Message": "Workout data processing complete: 25 new records added.",
  "Subject": "Workout Data Processed"
}
```

#### **SNS Subscriber Integration**
- **Subscribers:** Email, Webhook, Lambda, or other AWS services.
- **Message Format:** JSON message body containing processing summary.
- **Retries:** AWS SNS automatically retries failed deliveries.

---

## **🔗 External Integrations**

### **1️⃣ Amazon S3 (Storage & Event Triggering)**
- **Trigger**: S3 invokes Lambda on `s3:ObjectCreated:Put`.
- **Permissions**:
  - `s3:GetObject` (Lambda reads files from S3 bucket)
  - `s3:PutObject` (Future enhancement for writing back processed data)

### **2️⃣ Amazon ECS (Containerized Lambda Deployment)**
- **Function Deployment**: Lambda function is built and stored in ECS as a **Docker container**.
- **Key API Calls**:
  ```bash
  aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 533267082184.dkr.ecr.us-west-2.amazonaws.com
  aws lambda update-function-code --function-name workout-processor --image-uri 533267082184.dkr.ecr.us-west-2.amazonaws.com/workout-processor:latest
  ```

### **3️⃣ Amazon CloudWatch (Logging & Monitoring)**
- **Stores logs** from Lambda execution.
- **Enables alerts** for errors.
- **Key API Calls**:
  ```bash
  aws logs tail /aws/lambda/workout-processor --follow
  ```

---

## **📜 Message Protocols**

### **1️⃣ S3 Event Notification Format**
- **Protocol:** AWS S3 EventBridge
- **Triggers:** `s3:ObjectCreated:*`
- **Message Type:** JSON payload with file metadata.

### **2️⃣ SNS Message Format**
- **Protocol:** SNS (HTTP, Email, Lambda, or SMS delivery)
- **Message Type:** JSON with processing summary.
- **Retries:** SNS retries failed notifications for up to **5 minutes**.

---

## **📂 Data Structures**

### **1️⃣ Input Data Structure (CSV File)**
| **Column Name** | **Description** | **Example** |
|---------------|-------------|-----------|
| `timestamp` | UTC timestamp of the workout session | `2025-02-19T10:00:00Z` |
| `user_id` | Unique user identifier | `123456` |
| `activity_type` | Type of workout (e.g., Running, Cycling) | `Running` |
| `duration_minutes` | Length of workout in minutes | `45` |
| `calories_burned` | Estimated calories burned | `350` |

### **2️⃣ Processed Data Structure (Internal JSON Representation)**
```json
{
  "timestamp": "2025-02-19T10:00:00Z",
  "user_id": 123456,
  "activity_type": "Running",
  "duration_minutes": 45,
  "calories_burned": 350
}
```

### **3️⃣ SNS Notification Message Format**
```json
{
  "TopicArn": "arn:aws:sns:us-west-2:533267082184:workout-notifications",
  "Message": "Workout processed: 25 new records added.",
  "Subject": "Workout Data Updated"
}
```

---

## **🚀 Next Steps & Enhancements**

### **Short-Term Enhancements**
✅ **Add API Gateway** – Expose a REST API for external data submission.
✅ **Implement DynamoDB Integration** – Store processed records in a database.
✅ **Enhance Logging** – Store detailed processing logs for analytics.

### **Long-Term Improvements**
📌 **GraphQL API for Querying Processed Data** – Allow users to retrieve workout trends.
📌 **WebSocket Integration** – Real-time notifications for users when workouts are processed.
📌 **Streaming Data Processing with Kinesis** – Handle high-velocity workout data feeds.

---

## **🎉 Conclusion**
This API documentation provides a comprehensive breakdown of **internal Lambda APIs, external integrations with AWS services, message protocols, and data structures**. The next steps involve **enhancing API functionality, improving database storage, and enabling real-time analytics**.

🚀 **Future development will focus on expanding API capabilities and making the system more scalable!**

