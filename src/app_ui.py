"""
Disaster Relief Verification System - Enhanced Streamlit UI
This interface provides a modern, user-friendly experience for verifying disaster relief flyers.
"""

import streamlit as st
import asyncio
import tempfile
import os
from pathlib import Path
from PIL import Image
import plotly.graph_objects as go
import plotly.express as px

# Add the project root to sys.path to allow imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.forensic_agent import ForensicAgent

st.set_page_config(
    page_title="Disaster Relief Verification",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced Custom CSS with animations and modern design
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container styling */
    .main {
        padding-top: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Card styling */
    .card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
    
    /* Verdict banners with animations */
    .verdict-safe {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        font-size: 2.5rem;
        font-weight: 900;
        border: 3px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(16, 185, 129, 0.3);
        animation: pulse 2s ease-in-out infinite;
    }
    
    .verdict-suspicious {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        font-size: 2.5rem;
        font-weight: 900;
        border: 3px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(245, 158, 11, 0.3);
        animation: pulse 2s ease-in-out infinite;
    }
    
    .verdict-scam {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        font-size: 2.5rem;
        font-weight: 900;
        border: 3px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(239, 68, 68, 0.3);
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    /* Entity card styling */
    .entity-card {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-left: 4px solid #3b82f6;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .entity-card:hover {
        background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
    }
    
    .entity-flagged {
        border-left-color: #ef4444;
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
    }
    
    /* Risk meter with animation */
    .risk-meter-container {
        width: 100%;
        height: 24px;
        background: linear-gradient(90deg, #e5e7eb 0%, #d1d5db 100%);
        border-radius: 12px;
        margin: 1rem 0;
        overflow: hidden;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .risk-meter-fill {
        height: 100%;
        border-radius: 12px;
        transition: width 1s ease-out, background 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        position: relative;
    }
    
    .risk-meter-fill::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    /* Upload area styling */
    .upload-area {
        border: 3px dashed #cbd5e1;
        border-radius: 16px;
        padding: 3rem;
        text-align: center;
        background: rgba(255, 255, 255, 0.9);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .upload-area:hover {
        border-color: #3b82f6;
        background: rgba(59, 130, 246, 0.05);
        transform: scale(1.02);
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .verdict-safe, .verdict-suspicious, .verdict-scam {
            font-size: 1.5rem;
            padding: 1.5rem;
        }
        
        .card {
            padding: 1rem;
            margin: 0.5rem 0;
        }
    }
    
    /* Loading animation */
    .spinner-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 3rem;
    }
    
    .spinner {
        border: 4px solid #f3f4f6;
        border-top: 4px solid #3b82f6;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Evidence point styling */
    .evidence-point {
        padding: 0.75rem;
        margin: 0.5rem 0;
        background: rgba(59, 130, 246, 0.1);
        border-left: 3px solid #3b82f6;
        border-radius: 8px;
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize Streamlit session state."""
    if 'agent' not in st.session_state:
        st.session_state.agent = ForensicAgent()
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None

def create_risk_gauge(risk_score: int):
    """Create an interactive risk gauge chart using Plotly."""
    # Determine color based on score
    if risk_score < 40:
        color = '#10b981'  # Green (Safe)
        color_light = '#d1fae5'
    elif risk_score < 70:
        color = '#f59e0b'  # Amber (Suspicious)
        color_light = '#fef3c7'
    else:
        color = '#ef4444'  # Red (Scam)
        color_light = '#fee2e2'
    
    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = risk_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Risk Score", 'font': {'size': 20, 'color': '#1f2937'}},
        delta = {'reference': 50, 'position': "top"},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#1f2937"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': color,
            'steps': [
                {'range': [0, 40], 'color': '#d1fae5'},
                {'range': [40, 70], 'color': '#fef3c7'},
                {'range': [70, 100], 'color': '#fee2e2'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#1f2937', 'family': "Arial"}
    )
    
    return fig

def render_entity_cards(extracted_data: dict):
    """Render entity cards similar to AstraShield."""
    extracted = extracted_data.get('extracted', {})
    
    entities = []
    
    # Phone numbers
    for phone in extracted.get('phone_numbers', [])[:5]:
        entities.append({
            'type': 'PHONE',
            'value': phone,
            'icon': '📞',
            'color': '#3b82f6'
        })
    
    # Emails
    for email in extracted.get('emails', [])[:5]:
        entities.append({
            'type': 'EMAIL',
            'value': email,
            'icon': '📧',
            'color': '#8b5cf6'
        })
    
    # URLs
    for url in extracted.get('urls', [])[:5]:
        entities.append({
            'type': 'URL',
            'value': url,
            'icon': '🌐',
            'color': '#10b981'
        })
    
    # Domains
    for domain in extracted.get('domains', [])[:5]:
        entities.append({
            'type': 'DOMAIN',
            'value': domain,
            'icon': '🔗',
            'color': '#f59e0b'
        })
    
    if not entities:
        st.info("No entities extracted from the image.")
        return
    
    st.markdown("### 🔍 Extracted Entities")
    
    for entity in entities:
        st.markdown(f"""
        <div class="entity-card">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="font-size: 2rem;">{entity['icon']}</div>
                <div style="flex: 1;">
                    <div style="font-weight: 600; color: #1f2937; font-size: 1rem; word-break: break-all;">
                        {entity['value']}
                    </div>
                    <div style="font-size: 0.75rem; color: #6b7280; text-transform: uppercase; margin-top: 0.25rem;">
                        {entity['type']}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

async def run_analysis(image_path):
    """Run forensic analysis with enhanced progress indicators."""
    progress_container = st.container()
    
    with progress_container:
        st.markdown("""
        <div class="spinner-container">
            <div class="spinner"></div>
            <p style="margin-top: 1rem; font-size: 1.1rem; color: #1f2937; font-weight: 600;">
                🕵️ Forensic Analyst is investigating...
            </p>
            <p style="color: #6b7280; margin-top: 0.5rem;">
                This may take up to 30 seconds
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        steps = [
            "Extracting information from image...",
            "Analyzing text and QR codes...",
            "Checking domain registrations...",
            "Cross-referencing scam databases...",
            "Verifying organization registries...",
            "Compiling evidence...",
            "Generating report..."
        ]
        
        try:
            result = await st.session_state.agent.investigate(image_path)
            
            # Simulate progress updates
            for i, step in enumerate(steps):
                status_text.text(f"⏳ {step}")
                progress_bar.progress(int((i + 1) * 100 / len(steps)))
                await asyncio.sleep(0.1)  # Small delay for visual effect
            
            progress_container.empty()
            return result
        except Exception as e:
            progress_container.empty()
            st.error(f"❌ Analysis failed: {str(e)}")
            return None

def render_verdict(result):
    """Render verdict with enhanced visualizations."""
    verdict = result.get('verdict', 'unknown').lower()
    risk_score = result.get('risk_score', 0)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🛡️ Verification Result")
        
        if verdict == 'safe':
            st.markdown(f"""
                <div class="verdict-safe">
                    ✅ SAFE
                    <div style="font-size: 1rem; font-weight: normal; margin-top: 0.5rem; opacity: 0.9;">
                        Risk Score: {risk_score}/100
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.success("✅ This resource appears to be legitimate. However, always exercise reasonable caution.")
            
        elif verdict == 'suspicious':
            st.markdown(f"""
                <div class="verdict-suspicious">
                    ⚠️ SUSPICIOUS
                    <div style="font-size: 1rem; font-weight: normal; margin-top: 0.5rem; opacity: 0.9;">
                        Risk Score: {risk_score}/100
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.warning("⚠️ Caution advised. We found some indicators that require verification.")
            
        else:  # scam
            st.markdown(f"""
                <div class="verdict-scam">
                    ⛔ HIGH RISK / SCAM
                    <div style="font-size: 1rem; font-weight: normal; margin-top: 0.5rem; opacity: 0.9;">
                        Risk Score: {risk_score}/100
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.error("🚨 DO NOT TRUST. Strong indicators of fraudulent activity detected.")
    
    with col2:
        st.markdown("### 📊 Risk Gauge")
        fig = create_risk_gauge(risk_score)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def render_friendly_explanation(result):
    """Render user-friendly explanation with enhanced styling."""
    initial_data = result.get('initial_data', {})
    extracted_data = initial_data.get('extracted_data', {})
    extracted = extracted_data.get('extracted', {})
    raw_text = extracted_data.get('raw_text', '').strip()
    risk_factors = result.get('risk_factors', [])
    
    # Check extraction status
    has_data = bool(
        extracted.get('phone_numbers') or 
        extracted.get('emails') or 
        extracted.get('urls') or 
        extracted.get('domains') or
        (raw_text and raw_text != " ")
    )
    
    # Entity cards
    if has_data:
        render_entity_cards(extracted_data)
    else:
        st.warning("""
        ⚠️ **Extraction Warning**: No contact information could be extracted from this image.
        
        This may be due to:
        - Poor image quality or blurry text
        - Missing or unclear contact information on the flyer
        - Processing errors (check if Tesseract OCR and OpenAI API are configured)
        """)
    
    # Key findings
    if risk_factors:
        st.markdown("### 🔍 Key Findings")
        for factor in risk_factors:
            st.markdown(f"""
            <div class="evidence-point">
                <strong>⚠️</strong> {factor}
            </div>
            """, unsafe_allow_html=True)
    
    # Summary
    summary = result.get('summary', '')
    if summary:
        st.markdown("### 📝 Executive Summary")
        st.info(summary)
    
    # Recommendations
    recommendations = result.get('recommendations', [])
    if recommendations:
        st.markdown("### 💡 Recommendations")
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"""
            <div style="padding: 0.75rem; margin: 0.5rem 0; background: rgba(59, 130, 246, 0.1); 
                        border-radius: 8px; border-left: 3px solid #3b82f6;">
                <strong>{i}.</strong> {rec}
            </div>
            """, unsafe_allow_html=True)

def render_technical_details(result):
    """Render technical details in expandable section."""
    with st.expander("🔍 View Forensic Investigation Details (Technical)", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Case Information")
            st.json({
                'case_id': result.get('case_id'),
                'status': result.get('status'),
                'created_at': result.get('created_at'),
                'completed_at': result.get('completed_at'),
                'processing_time': f"{result.get('processing_time_seconds', 0):.2f}s"
            })
        
        with col2:
            st.markdown("#### Evidence Summary")
            evidence = result.get('evidence', [])
            st.metric("Evidence Points", len(evidence))
            st.metric("Risk Factors", len(result.get('risk_factors', [])))
        
        st.markdown("#### Complete Investigation Data")
        st.json(result)

def main():
    """Main application function."""
    init_session_state()
    
    # Header with gradient background
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 16px; margin-bottom: 2rem; text-align: center;">
        <h1 style="color: white; font-size: 3rem; margin: 0; font-weight: 900;">
            🛡️ Disaster Relief Verifier
        </h1>
        <p style="color: rgba(255, 255, 255, 0.9); font-size: 1.2rem; margin-top: 0.5rem;">
            Don't get scammed while trying to help. Verify flyers instantly.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Input section
    tab1, tab2 = st.tabs(["📷 Camera", "📤 Upload"])
    
    image_file = None
    
    with tab1:
        st.markdown("### Take a Photo")
        camera_image = st.camera_input("", label_visibility="collapsed")
        if camera_image:
            image_file = camera_image
            st.success("✅ Photo captured! Click 'Verify' below to analyze.")
            
    with tab2:
        st.markdown("### Upload an Image")
        uploaded_image = st.file_uploader(
            "Choose an image file",
            type=['jpg', 'jpeg', 'png', 'webp'],
            label_visibility="collapsed"
        )
        if uploaded_image:
            image_file = uploaded_image
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(image_file, use_container_width=True)
            with col2:
                st.success(f"✅ **{uploaded_image.name}** uploaded successfully!")
                st.caption(f"Size: {uploaded_image.size / 1024:.1f} KB")

    # Verify button
    if image_file:
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔍 Verify This Resource", type="primary", use_container_width=True):
                # Save temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                    tmp_file.write(image_file.getvalue())
                    tmp_path = tmp_file.name
                
                # Run analysis
                result = asyncio.run(run_analysis(tmp_path))
                st.session_state.analysis_result = result
                
                # Cleanup
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                
                # Rerun to show results
                st.rerun()

    # Display results
    if st.session_state.analysis_result:
        st.markdown("---")
        result = st.session_state.analysis_result
        
        # Main results section
        render_verdict(result)
        
        st.markdown("---")
        
        # Details section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            render_friendly_explanation(result)
        
        with col2:
            st.markdown("### ⏱️ Performance Metrics")
            st.metric(
                "Analysis Time",
                f"{result.get('processing_time_seconds', 0):.2f}s",
                help="Total time taken for investigation"
            )
            st.metric(
                "Evidence Points",
                len(result.get('evidence', [])),
                help="Number of evidence items collected"
            )
            st.metric(
                "Risk Factors",
                len(result.get('risk_factors', [])),
                help="Number of risk indicators found"
            )
            
            st.markdown("---")
            st.caption(f"**Case ID:** `{result.get('case_id')}`")
            
            if st.button("🔄 Verify Another", use_container_width=True):
                st.session_state.analysis_result = None
                st.rerun()
        
        st.markdown("---")
        render_technical_details(result)

if __name__ == "__main__":
    main()
