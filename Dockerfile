# 1. Use the official lightweight Python 3.13 image as the base
FROM python:3.13-slim

# 2. Set the working directory inside the virtual container
WORKDIR /app

# 3. Copy just the requirements file first to optimize caching
COPY requirements.txt .

# 4. Install Flask inside the container's isolated space
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy all our local files (app.py, parser.py, legacy_claims.txt) into the container
COPY . .

# 6. Tell the container to open port 5000 to the outside world
EXPOSE 5000

# 7. The exact command to execute when the container boots up
CMD ["python", "app.py"]