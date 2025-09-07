# Real-Time Log Processing Pipeline (Mock AWS + Python)

## 📌 Problem Statement
This project simulates a **real-time log processing pipeline** using Python and AWS concepts.  
It ingests JSON logs, validates + transforms them, and stores results in Parquet (valid) or JSON (errors).  
The design mirrors an AWS architecture with **S3 → Lambda → S3 (clean/error) → CloudWatch → API Gateway**.

---

## 🛠️ Features
- **Validation**: Ensures `timestamp`, `user_id`, `action` fields exist.
- **Transformation**:
  - Convert timestamp into `YYYY-MM-DD HH:MM:SS`
  - Add `day_of_week`
- **Storage**:
  - Clean logs → Parquet (columnar format)
  - Invalid logs → JSON Lines
- **Monitoring**: Logs metrics (#processed, #errors).
- **REST API**: Query `/logins_today` to check how many login actions happened today.

---

## 📂 Files
- `processor.py` → validation + transformation
- `storage.py` → write Parquet + JSONL
- `lambda_handler.py` → AWS Lambda–style function
- `pipeline_moto.py` → simulates S3 event → Lambda trigger (using Moto)
- `api.py` → FastAPI API to query clean logs
- `requirements.txt` → Python dependencies

---

## 🚀 How to Run

### 1. Setup environment
```bash
python -m venv venv
source venv/bin/activate   # mac/linux
venv\Scripts\activate    # windows
pip install -r requirements.txt
```

### 2. Run pipeline (Moto simulation)
```bash
python pipeline_moto.py
```
You should see logs like:
```
Lambda result: {'processed': 3, 'valid': 1, 'errors': 2}
Wrote local copy: data/clean/clean_from_moto.parquet
```

### 3. Start API
```bash
uvicorn api:app --reload
```

### 4. Test API
In a browser or terminal:
```
http://127.0.0.1:8000/logins_today
```

Expected response (if today’s date exists in logs):
```json
{"logins_today": 1}
```

Swagger UI docs:
```
http://127.0.0.1:8000/docs
```

---

## 📊 AWS Architecture (Mirrored)

```
S3 (input) → Lambda → S3 (clean/error)
                     ↓
                CloudWatch (metrics)
                     ↓
           API Gateway → /logins_today
```
```mermaid
%%{ init: { 'flowchart': { 'curve': 'cardinal' } } }%%
flowchart TD
    A@{ shape: cyl, label: "S3 Input Logs 📥", class: 's3' }
    B@{ shape: fr-rect, label: "Lambda\nFunction", class: 'lambda' }
    C@{ shape: cyl, label: "S3 Clean Parquet 🧹", class: 's3' }
    D@{ shape: hex, label: "S3 Error Logs ❗", class: 's3-error' }
    E@{ shape: stadium, label: "CloudWatch Metrics 📊", class: 'cw' }
    F@{ shape: hex, label: "API Gateway\n/logins_today", class: 'api' }

    A --> B
    B --> C
    B --> D
    B --> E
    E --> F

    %% Style definitions
    classDef s3 fill:#d5e6fa,stroke:#1e7dd9,stroke-width:2px;
    classDef s3-error fill:#ffd6d6,stroke:#f44336,stroke-width:2px;
    classDef lambda fill:#feeead,stroke:#f6b93b,stroke-width:2px;
    classDef cw fill:#e9f7d5,stroke:#27ae60,stroke-width:2px;
    classDef api fill:#fcf6e3,stroke:#8854d0,stroke-width:2px,font-weight:bold;

---

## 📌 Failure Handling & Monitoring
- Invalid logs → stored in **error S3 bucket**.
- Malformed files → logged as errors in CloudWatch.
- Lambda errors → automatically retried; failed events can go to a **Dead Letter Queue (DLQ)**.
- Monitoring → CloudWatch tracks processed vs failed counts; alerts via SNS/email if thresholds exceeded.


