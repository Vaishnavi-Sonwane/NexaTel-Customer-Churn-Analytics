FROM python:3.12-slim
WORKDIR /app
COPY requirements-dashboard.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py ./app.py
COPY data/clean ./data/clean
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
