import streamlit as st
from rag_engine import CorporateRAG

# Professional UI Config
st.set_page_config(page_title="ERP AI Assistant", page_icon="🤖", layout="wide")

# Custom Styling
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .main-title { color: #1e3a8a; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>💼 ERP Functional Knowledge Assistant</h1>", unsafe_allow_html=True)
st.write("---")

# Sidebar for System Info
with st.sidebar:
    st.header("⚙️ System Status")
    st.success("Vector DB: Connected ✅")
    st.info("Engine: Gemini Flash Latest")
    st.divider()
    st.write("This assistant provides guidance on Finance, P2P, and O2C modules.")

# Initialize RAG system (cached to avoid reloading)
@st.cache_resource
def load_rag():
    return CorporateRAG()

rag = load_rag()

# Main Query Area
query = st.text_input("How can I assist you with your ERP tasks today?", placeholder="e.g., Explain the Journal Voucher process...")

if st.button("Generate Guidance"):
    if query:
        with st.spinner("Analyzing ERP Documentation..."):
            try:
                result = rag.query(query)
                st.markdown("### 🤖 Assistant Guidance")
                st.write(result['answer'])
                st.markdown("---")
                with st.expander("📚 View Document Sources"):
                    for source in result['sources']:
                        st.markdown(f"- 📄 {source}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
