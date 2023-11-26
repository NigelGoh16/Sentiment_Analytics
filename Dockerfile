# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR /app
COPY . .

# Install production dependencies.
RUN pip install -r requirements.txt


EXPOSE 8080

CMD ["gunicorn", "--workers", "4", "--max-requests", "20000", "app:server"]

# gcloud builds submit --tag gcr.io/ProjectID/dash-youtube-example  --project=ProjectID
# gcloud run deploy --image gcr.io/ProjectID/dash-youtube-example --platform managed  --project=ProjectID --allow-unauthenticated

# ytsent-404915
# gcloud builds submit --tag gcr.io/ytsentanalytics/sentiment-analytics  --project=ytsentanalytics
# gcloud run deploy sentiment-analytics --image gcr.io/ytsentanalytics/sentiment-analytics --platform managed --region=asia-southeast1 --project=ytsentanalytics --allow-unauthenticated

# gcloud builds submit --tag gcr.io/ytsentanalytics/sentiment-test  --project=ytsentanalytics
# gcloud run deploy sentiment-test --image gcr.io/ytsentanalytics/sentiment-test --platform managed --region=asia-southeast1 --project=ytsentanalytics --allow-unauthenticated
