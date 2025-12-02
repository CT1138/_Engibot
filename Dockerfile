FROM python:3.11-alpine

RUN apk add --no-cache mariadb-connector-c-dev gcc musl-dev python3-dev

# Set working directory
WORKDIR /app

# Copy all project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 6934

# Run the bot
CMD ["python", "main.py"]