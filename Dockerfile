FROM python:3.10-slim

WORKDIR /app

# Install lightweight backend dependencies
RUN pip install --no-cache-dir pydantic fastapi uvicorn openai

COPY . .

EXPOSE 7860

# Runs the containerized OpenEnv API layer (Hugging Face Spaces compatible)
CMD ["python", "-m", "server.app"]
