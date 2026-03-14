FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY app.py data.py rag_engine.py build_rag.py ./
COPY rag_data/ ./rag_data/
COPY static/ ./static/
COPY templates/ ./templates/

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "app:app"]
