# Use AWS's official Python 3.11 Lambda runtime base image
FROM public.ecr.aws/lambda/python:3.11

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements first (for better caching)
COPY requirements/prod.txt .
RUN pip install --no-cache-dir -r prod.txt

# Copy function code
COPY src/ .

# Set the CMD to your handler
CMD [ "workout_processor.handler" ]