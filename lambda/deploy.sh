#!/bin/bash
set -e  # Exit on any error

# Define AWS and Docker variables
ECR_REPOSITORY="533267082184.dkr.ecr.us-west-2.amazonaws.com/workout-processor"
IMAGE_TAG="latest"
LAMBDA_FUNCTION_NAME="workout-processor"

echo "🚀 Starting Deployment Process..."

# Step 1: Build the Docker image (Ensuring compatibility with AWS Lambda)
echo "🔨 Building Docker image..."
docker buildx build --platform linux/amd64 -t $ECR_REPOSITORY:$IMAGE_TAG .

# Step 2: Tag the latest image (Ensures correct version is deployed)
echo "🏷️ Tagging the latest image..."
LATEST_IMAGE_ID=$(docker images -q $ECR_REPOSITORY | head -n 1)

# Debugging output
echo "🛠️ Debug: Found image ID = $LATEST_IMAGE_ID"

if [ -z "$LATEST_IMAGE_ID" ]; then
    echo "❌ Error: No image found for '$ECR_REPOSITORY'. Ensure the build was successful."
    exit 1
fi

docker tag $LATEST_IMAGE_ID $ECR_REPOSITORY:$IMAGE_TAG

# Step 3: Push the image to AWS ECR
echo "📤 Pushing the image to AWS ECR..."
docker push $ECR_REPOSITORY:$IMAGE_TAG

# Step 4: Update Lambda function
echo "🚀 Deploying new image to AWS Lambda..."
if ! aws lambda update-function-code --function-name $LAMBDA_FUNCTION_NAME --image-uri $ECR_REPOSITORY:$IMAGE_TAG --output json; 
then
    echo "❌ Lambda update failed"
    exit 1
fi

# Add wait for function update
echo "⏳ Waiting for function update to complete..."
aws lambda wait function-updated --function-name $LAMBDA_FUNCTION_NAME

# Step 5: Verify Deployment
echo "🔍 Verifying Lambda deployment..."
aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME

# Add after the Lambda update
echo "🔍 Validating Lambda function..."
FUNCTION_CONFIG=$(aws lambda get-function-configuration \
    --function-name $LAMBDA_FUNCTION_NAME \
    --output json)

# Check if the function configuration was retrieved successfully
if [ $? -eq 0 ]; then
    echo "✅ Lambda function configuration is valid"
    echo "📋 Function details:"
    echo "$FUNCTION_CONFIG" | '.'
else
    echo "❌ Error retrieving function configuration"
    exit 1
fi

echo "✅ Deployment Complete!"
