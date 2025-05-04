import streamlit as st
import requests
import json

# Configuration
FASTAPI_URL = "http://localhost:8000"

# UI Setup
st.set_page_config(page_title="SHL Assessment Recommender", layout="wide")
st.title("SHL Assessment Recommendation System")
st.markdown("""
Enter a job description or requirements to get relevant SHL assessments.
""")

# Main UI Components
with st.form("recommendation_form"):
    query = st.text_area("Job Description or Requirements:", 
                        placeholder="e.g., 'Need cognitive test for software engineers'")
    top_k = st.slider("Number of recommendations:", 1, 10, 5)
    submitted = st.form_submit_button("Get Recommendations")

if submitted and query:
    with st.spinner("Finding the best assessments..."):
        try:
            response = requests.post(
                f"{FASTAPI_URL}/recommend",
                json={"query": query, "top_k": top_k}
            )
            
            if response.status_code == 200:
                results = response.json()["recommendations"]
                
                # Display results in a clean table
                st.subheader("Recommended Assessments")
                for i, assessment in enumerate(results, 1):
                    with st.expander(f"#{i}: {assessment['name']}"):
                        cols = st.columns([1,3])
                        with cols[0]:
                            st.markdown(f"**Score:** {assessment['score']:.2f}")
                            st.markdown(f"**Duration:** {assessment['duration']}")
                            st.markdown(f"**Remote:** {'✅' if assessment['remote_support'] else '❌'}")
                            st.markdown(f"**Adaptive:** {'✅' if assessment['adaptive_support'] else '❌'}")
                            st.markdown(f"**Types:** {', '.join(assessment['test_type'])}")
                        
                        with cols[1]:
                            st.markdown(f"**Description:** {assessment['description']}")
                            st.markdown(f"[View Assessment]({assessment['url']})")
                
                # Additional visual feedback
                st.success(f"Found {len(results)} recommendations!")
                
            else:
                st.error(f"API Error: {response.text}")
                
        except Exception as e:
            st.error(f"Failed to get recommendations: {str(e)}")

# Sidebar with examples
with st.sidebar:
    st.markdown("### Example Queries")
    examples = [
        "Cognitive test for software engineers under 30 minutes",
        "Personality assessment for customer service roles",
        "Technical test for Python developers with remote support"
    ]
    for example in examples:
        if st.button(example):
            st.session_state.query = example