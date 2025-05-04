# SHL Assessment Recommendation System

![SHL Logo](https://www.shl.com/-/media/project/shl-sites/shlglobal/rebrand-2021/shl-logo.svg)  
*A RAG-powered recommendation system for SHL assessments*

## 📌 Table of Contents
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Setup Guide](#-setup-guide)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [API Documentation](#-api-documentation)
  - [Endpoints](#endpoints)
  - [Request/Response Examples](#requestresponse-examples)
- [Running the UI](#-running-the-ui)
- [Evaluation](#-evaluation)

## 🌟 Features
- **Natural Language Processing**: Understands job descriptions in plain English
- **RAG Architecture**: Combines vector search with LLM refinement
- **Smart Filtering**: Considers duration, remote support, and assessment type
- **Evaluation Ready**: Built-in support for Recall@K and MAP@K metrics
- **Demo UI**: Streamlit-based interface for easy testing

## 🛠 Tech Stack
| Component       | Technology |
|----------------|------------|
| Backend        | FastAPI    |
| Vector DB      | ChromaDB   |
| Embeddings     | all-MiniLM-L6-v2 |
| LLM            | Gemini Pro |
| UI             | Streamlit  |
| Evaluation     | Recall@K, MAP@K |

## 🚀 Setup Guide

### Prerequisites
- Python 3.9+
- Google Gemini API key
- (Optional) Node.js for alternative UI

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/shl-recommender.git
   cd shl-recommender
   ```

2. Set up environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/Mac
    .\.venv\Scripts\activate  # Windows
    ```
3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```
4. Set up environment variables:
    ```bash
    echo "GEMINI_API_KEY=your_api_key_here" > .env
    ```
5. Initialize the FastAPI service:
    ```bash
    uvicorn app.main:app --reload
    ```
Access FastAPI Swagger docs at: http://localhost:8000/docs

### 📡 API Documentation
#### Endpoints
1. Health Check
    ```http
    GET /health
    ```
    Response:

    ```json
    {"status": "healthy"}
    ```
2. Recommendation
    ```http
    POST /recommend
    ```

    Request Body:

    ```json
    {
    "query": "cognitive test for engineers",
    "top_k": 5
    }
    ```
    Response Example:
    ```json
    {
    "recommendations": [
        {
        "url": "https://www.shl.com/assessments/verify-inductive/",
        "adaptive_support": true,
        "description": "Measures logical reasoning with abstract patterns",
        "duration": "25 minutes",
        "remote_support": true,
        "test_type": ["Cognitive", "Logical"],
        "score": 0.92
        }
    ]
    }
    ```
### 🖥 Running the UI
Streamlit UI

```bash
streamlit run ui.py
```
Access Streamlit UI at: http://localhost:8501

### 📊 Evaluation

To assess the recommendation quality, we include an evaluation module using curated test queries.

#### 📁 Files:
- `app/evaluation.py`: evaluation script
- `data/test_queries.json`: benchmark test queries and expected URLs

#### 📐 Metrics:
- `Precision@5`
- `Recall@5`

#### ▶️ How to Run:
```bash
python app/evaluation.py
```

#### 📈 Sample Output:
```text
🔹 Query: Need to assess Java skills of entry-level developers.
   Precision@5: 0.20
   Recall@5: 1.00

📊 Final Evaluation:
   Average Precision@5: 0.20
   Average Recall@5: 1.00
```