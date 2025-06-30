FROM python:3.10-slim

WORKDIR /news_sentiment

# Install cron
RUN apt update && apt install -y cron
RUN apt update && apt-get install -y tzdata
ENV TZ=Asia/Bangkok

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies
ADD requirements.txt .
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Add crontab
RUN chmod 0644 crontab
RUN crontab crontab

# Start cron in the foreground
CMD ["cron", "-f"]
