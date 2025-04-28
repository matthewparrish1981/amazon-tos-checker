
import streamlit as st
import pandas as pd
from datetime import datetime

# TOS violation rules
def violates_amazon_tos(text):
    text_lower = str(text).lower()
    if "shipping" in text_lower or "delivery" in text_lower:
        return "Shipping/Delivery Issue"
    if "received wrong item" in text_lower or "knockoff" in text_lower or "counterfeit" in text_lower:
        return "Wrong Item/Counterfeit"
    if "did not receive" in text_lower:
        return "Non-Delivery"
    if "seller" in text_lower and "product" not in text_lower:
        return "Seller Complaint"
    if "refund" in text_lower or "return" in text_lower:
        return "Return/Refund Issue"
    if any(word in text_lower for word in ["scam", "fraud", "ripoff", "fake"]):
        return "Potentially Defamatory"
    if any(word in text_lower for word in ["hate", "disgusting", "crap", "sucks"]):
        return "Offensive Language"
    return None

# Streamlit UI
st.title("Amazon TOS Violation Checker for Trtl Reviews")

uploaded_file = st.file_uploader("Upload the latest Amazon reviews CSV file", type="csv")
previous_file = st.file_uploader("(Optional) Upload previous TOS violations file for comparison", type="csv")

if uploaded_file:
    current_df = pd.read_csv(uploaded_file)
    one_star_reviews = current_df[current_df['Rating'] == 1.0].copy()
    one_star_reviews['TOS_Violation'] = one_star_reviews['Body'].apply(violates_amazon_tos)
    violating_reviews = one_star_reviews[one_star_reviews['TOS_Violation'].notnull()]

    st.subheader("Detected TOS Violations")
    st.dataframe(violating_reviews[['Date', 'Author', 'Title', 'Body', 'TOS_Violation']])

    today_str = datetime.today().strftime('%Y-%m-%d')
    filename = f"TOS_Violations_{today_str}.csv"
    
    # Download button for the violations file
    st.download_button(
        label="Download Current Violations List",
        data=violating_reviews.to_csv(index=False).encode('utf-8'),
        file_name=filename,
        mime='text/csv'
    )

    # Compare with previous violations if available
    if previous_file:
        previous_df = pd.read_csv(previous_file)

        previous_urls = set(previous_df['URL']) if 'URL' in previous_df.columns else set()
        current_urls = set(violating_reviews['URL']) if 'URL' in violating_reviews.columns else set()

        new_violations = current_urls - previous_urls
        removed_violations = previous_urls - current_urls

        st.subheader("Comparison with Previous File")
        st.write(f"**New Violations:** {len(new_violations)}")
        st.write(f"**Removed Violations:** {len(removed_violations)}")

        if new_violations:
            st.write("### New Violation URLs:")
            st.write(list(new_violations))
        if removed_violations:
            st.write("### Removed Violation URLs:")
            st.write(list(removed_violations))
