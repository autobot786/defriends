FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Install shared library
COPY packages/common /app/packages/common
RUN pip install --no-cache-dir -e /app/packages/common

# Install all service dependencies (superset)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy all service code and supporting files
COPY services /app/services
COPY rules /app/rules
COPY schemas /app/schemas
COPY examples /app/examples
COPY static /app/static
COPY app_unified.py /app/app_unified.py

ENV DIRTYBOT_MAPPING_PACK=/app/rules/mapping/mitre_cwe_context.v1.yaml
ENV DIRTYBOT_REPORT_SCHEMA=/app/schemas/report.schema.json

EXPOSE 8000
CMD ["uvicorn", "app_unified:app", "--host", "0.0.0.0", "--port", "8000"]
