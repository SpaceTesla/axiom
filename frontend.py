"""Streamlit frontend for Axiom API."""

import streamlit as st
import requests
from typing import Optional

# Page config
st.set_page_config(
    page_title="Axiom - Hyper-Rational Debate",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    div[data-testid="stContainer"] > div:has(> .response-box) {
        padding: 0 !important;
        margin: 0 !important;
    }
    .response-box {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0 0 0;
    }
    /* Ensure all text in response box is readable */
    .response-box, .response-box * {
        color: #212529 !important;
    }
    .response-box p {
        color: #212529 !important;
        margin-bottom: 1rem;
        line-height: 1.8;
    }
    .response-box h1, .response-box h2, .response-box h3, .response-box h4, .response-box h5, .response-box h6 {
        color: #212529 !important;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        font-weight: bold;
    }
    .response-box h3 {
        font-size: 1.3rem;
    }
    .response-box strong, .response-box b {
        color: #212529 !important;
        font-weight: bold;
    }
    .response-box ul, .response-box ol {
        color: #212529 !important;
        margin-left: 1.5rem;
        margin-bottom: 1rem;
    }
    .response-box li {
        color: #212529 !important;
        margin-bottom: 0.5rem;
        line-height: 1.6;
    }
    .response-box code {
        background-color: #e9ecef;
        color: #212529 !important;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
    }
    .response-box blockquote {
        border-left: 3px solid #1f77b4;
        padding-left: 1rem;
        margin-left: 0;
        color: #495057 !important;
        font-style: italic;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">⚡ Axiom</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Hyper-Rational Debate API</p>', unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Get API URL from environment or use default
    import os
    default_api_url = os.getenv("API_URL", st.session_state.get("api_url", "http://212.2.248.199"))
    
    api_url = st.text_input(
        "API URL",
        value=default_api_url,
        help="Enter your Axiom API URL (without trailing slash)"
    )
    st.session_state["api_url"] = api_url
    
    st.markdown("---")
    st.markdown("### 📖 About")
    st.markdown("""
    **Axiom** is a hyper-rational debate API that:
    - Calls out flawed logic instantly
    - Exposes contradictions without hesitation
    - Points out when evidence is zero
    - Pushes arguments into corners they can't escape
    
    No disrespect. No insults. Just pure, brutal logic.
    """)
    
    st.markdown("---")
    st.markdown("### 🔗 Links")
    st.markdown(f"[API Docs]({api_url}/docs)")
    st.markdown(f"[Health Check]({api_url}/health)")

# Main content
st.markdown("### 💬 Submit Your Argument")

argument = st.text_area(
    "Enter your argument or claim:",
    height=150,
    placeholder="Example: Jesus's resurrection is the best historical explanation for the empty tomb, post-resurrection appearances, and the disciples' willingness to die for their testimony...",
    help="Type your argument here. Axiom will provide a logical, direct response."
)

col1, col2 = st.columns([4, 1])

with col1:
    submit_button = st.button("🚀 Debate", type="primary", use_container_width=True)

with col2:
    if st.button("🗑️ Clear", use_container_width=True):
        st.rerun()

# Process submission
if submit_button and argument.strip():
    with st.spinner("🤔 Axiom is analyzing your argument..."):
        try:
            response = requests.post(
                f"{api_url}/api/v1/debate",
                json={"message": argument},
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            debate_response = data.get("response", "No response received")
            model_used = data.get("model", "Unknown")
            
            # Display response
            st.markdown("---")
            st.markdown("### ⚡ Axiom's Response")
            
            # Render in a clean container without extra spacing
            st.markdown("""
                <style>
                .stMarkdown:has(+ .response-container) {
                    margin-bottom: 0 !important;
                }
                </style>
            """, unsafe_allow_html=True)
            
            # Render markdown with styled background
            st.markdown(f'<div class="response-box">{debate_response}</div>', unsafe_allow_html=True)
            
            # Metadata
            with st.expander("ℹ️ Response Details"):
                st.write(f"**Model:** {model_used}")
                st.write(f"**API URL:** {api_url}")
                st.write(f"**Status Code:** {response.status_code}")
            
        except requests.exceptions.ConnectionError:
            st.error("❌ **Connection Error:** Could not connect to the API. Please check:")
            st.markdown("""
            - The API URL is correct
            - The API is running and accessible
            - Your network connection is working
            """)
        except requests.exceptions.Timeout:
            st.error("⏱️ **Timeout:** The API took too long to respond. The model might be processing a complex argument.")
        except requests.exceptions.HTTPError as e:
            st.error(f"❌ **HTTP Error {e.response.status_code}:** {e.response.text}")
        except Exception as e:
            st.error(f"❌ **Error:** {str(e)}")

elif submit_button and not argument.strip():
    st.warning("⚠️ Please enter an argument before submitting.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 1rem;'>"
    "Built with ❤️ using Streamlit | Powered by Axiom API"
    "</div>",
    unsafe_allow_html=True
)

