"""Streamlit deployment entry point for the retail recommendation engine."""

import streamlit as st

from backend import main as retail_api
from backend.data.database import get_all_customers


st.set_page_config(
    page_title="Retail Recommendation Agent",
    page_icon="🛍️",
    layout="wide",
)


@st.cache_resource(show_spinner="Loading recommendation models...")
def initialize_application():
    """Initialize the shared database and ML models once per Streamlit process."""
    retail_api.startup_event()
    return True


def main():
    st.title("Personalized Retail Recommendation Agent")
    st.caption("Recommendations powered by hybrid ML models, explainable AI, and governance checks.")

    initialize_application()
    customers = get_all_customers()
    customer_lookup = {
        f"{customer['name']} — {customer['persona_title']}": customer["id"]
        for customer in customers
    }

    with st.sidebar:
        st.header("Recommendation settings")
        selected_customer = st.selectbox("Customer persona", list(customer_lookup))
        season = st.selectbox("Season", ["Winter", "Spring", "Summer", "Fall"])
        model = st.selectbox(
            "Recommendation model",
            ["hybrid", "user_cf", "item_cf", "content", "svd", "ncf"],
            format_func=lambda value: {
                "hybrid": "Hybrid ensemble",
                "user_cf": "User collaborative filtering",
                "item_cf": "Item collaborative filtering",
                "content": "Content based filtering",
                "svd": "SVD matrix factorization",
                "ncf": "Neural collaborative filtering",
            }[value],
        )
        recommendation_count = st.slider("Recommendations", min_value=3, max_value=10, value=6)

    customer_id = customer_lookup[selected_customer]
    response = retail_api.get_recommendations(
        customer_id=customer_id,
        season=season,
        model_type=model,
        top_k=recommendation_count,
    )

    st.subheader(response["persona"].get("headline", "Customer profile"))
    st.write(response["persona"].get("narrative_profile", ""))

    metric_a, metric_b, metric_c = st.columns(3)
    metric_a.metric("Model", model.upper())
    metric_b.metric("Recommendations", len(response["recommendations"]))
    metric_c.metric("Latency", f"{response['latency_ms']} ms")

    st.subheader("Recommended products")
    columns = st.columns(3)
    for index, recommendation in enumerate(response["recommendations"]):
        product = recommendation["product"]
        explanation = recommendation["explanation"]
        with columns[index % 3]:
            st.markdown(f"### {product['title']}")
            st.caption(f"{product['brand']} · {product['category']}")
            st.write(f"**${product['price']:.2f}** · Rating {product['rating']}/5")
            st.progress(min(max(float(recommendation["confidence"]), 0.0), 1.0))
            st.write(explanation["reasoning"])
            citations = explanation.get("citations", [])
            if citations:
                st.caption(" · ".join(citations))

    st.subheader("Ask the shopping assistant")
    prompt = st.chat_input("For example: Find an item under $100")
    if prompt:
        answer = retail_api.conversational_agent.chat(customer_id, prompt, [])
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write(answer["reply"])


if __name__ == "__main__":
    main()
