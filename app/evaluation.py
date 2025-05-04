import requests
import json

K = 5  # Top-K recommendations to evaluate

def precision_at_k(predicted, relevant, k=5):
    predicted_set = set(predicted[:k])
    relevant_set = set(relevant)
    return len(predicted_set & relevant_set) / k

def recall_at_k(predicted, relevant, k=5):
    predicted_set = set(predicted[:k])
    relevant_set = set(relevant)
    return len(predicted_set & relevant_set) / len(relevant) if relevant else 0

def evaluate():
    with open("data/test_queries.json", "r") as f:
        test_data = json.load(f)

    precision_scores = []
    recall_scores = []

    for entry in test_data:
        query = entry["query"]
        relevant = entry["relevant_assessments"]

        response = requests.post(
            "http://127.0.0.1:8000/recommend",  # Local development server
            json={"query": query, "top_k": K}
        )

        if response.status_code != 200:
            print(f"❌ Failed to get response for query: {query}")
            continue

        result = response.json()
        predicted_urls = [
            item["url"].strip().lower().rstrip("/")
            for item in result.get("recommendations", [])
            if item.get("url")
        ]

        relevant = [
            url.strip().lower().rstrip("/") for url in relevant
        ]

        print(f"   Predicted: {predicted_urls}\n   Relevant: {relevant}")

        precision = precision_at_k(predicted_urls, relevant, k=K)
        recall = recall_at_k(predicted_urls, relevant, k=K)

        precision_scores.append(precision)
        recall_scores.append(recall)

        print(f"\n🔹 Query: {query}")
        print(f"   Precision@{K}: {precision:.2f}")
        print(f"   Recall@{K}: {recall:.2f}")

    if precision_scores:
        avg_precision = sum(precision_scores) / len(precision_scores)
        avg_recall = sum(recall_scores) / len(recall_scores)

        print("\n📊 Final Evaluation:")
        print(f"   Average Precision@{K}: {avg_precision:.2f}")
        print(f"   Average Recall@{K}: {avg_recall:.2f}")
    else:
        print("\n⚠️ No successful responses received. Check your API URL or server status.")

if __name__ == "__main__":
    evaluate()