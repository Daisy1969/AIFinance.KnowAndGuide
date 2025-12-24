FROM python:3.10-slim

WORKDIR /app


# Install system dependencies for compiling C-extensions (ecos, scs, cvxpy, pyportfolioopt)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["flask", "run", "--host=0.0.0.0"]
