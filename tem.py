import streamlit as st
import pandas as pd
from datetime import datetime
import io
import base64

# Page configuration
st.set_page_config(
    page_title="Church Reporting System",
    page_icon="⛪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimalist CSS with OS theme sync and grayscale palette
st.markdown("""
<style>
    /* CSS Variables for Theme Sync */
    :root {
        /* Light Theme (Default) */
        --bg-primary: #FFFFFF;
        --bg-secondary: #F8F9FA;
        --bg-tertiary: #F1F3F4;
        --text-primary: #202124;
        --text-secondary: #5F6368;
        --text-tertiary: #80868B;
        --border-color: #DADCE0;
        --border-hover: #BDC1C6;
        --accent-color: #1A73E8;
        --accent-hover: #0C63DA;
        --success-color: #0D652D;
        --warning-color: #EA8600;
        --error-color: #C5221F;
        --shadow-sm: 0 1px 2px rgba(60,64,67,0.1);
        --shadow-md: 0 2px 6px rgba(60,64,67,0.15);
        --shadow-lg: 0 4px 12px rgba(60,64,67,0.2);
        --radius-sm: 6px;
        --radius-md: 8px;
        --radius-lg: 12px;
    }
    
    /* Dark Theme Override */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-primary: #202124;
            --bg-secondary: #2D2E31;
            --bg-tertiary: #3C4043;
            --text-primary: #E8EAED;
            --text-secondary: #BDC1C6;
            --text-tertiary: #9AA0A6;
            --border-color: #5F6368;
            --border-hover: #80868B;
            --accent-color: #8AB4F8;
            --accent-hover: #AECBFA;
            --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
            --shadow-md: 0 2px 6px rgba(0,0,0,0.4);
            --shadow-lg: 0 4px 12px rgba(0,0,0,0.5);
        }
    }
    
    /* Main App Background */
    .stApp {
        background-color: var(--bg-primary);
        color: var(--text-primary);
        transition: background-color 0.3s ease, color 0.3s ease;
    }
    
    /* Main Header */
    .main-header {
        font-size: 2.5rem;
        font-weight: 300;
        color: var(--text-primary);
        text-align: center;
        padding: 1.5rem;
        margin-bottom: 2rem;
        border-bottom: 1px solid var(--border-color);
        letter-spacing: -0.025em;
        background-color: var(--bg-primary);
    }
    
    .main-header strong {
        font-weight: 600;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 500;
        color: var(--text-primary);
        padding: 0.75rem 0;
        margin: 2rem 0 1rem 0;
        border-bottom: 2px solid var(--border-color);
        background-color: var(--bg-primary);
    }
    
    /* Subsection Headers */
    .subsection-header {
        font-size: 1.1rem;
        font-weight: 500;
        color: var(--text-primary);
        padding: 0.5rem 0;
        margin: 1.5rem 0 1rem 0;
        background-color: var(--bg-primary);
    }
    
    /* Cards */
    .input-card {
        background-color: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        padding: 1.25rem;
        margin: 0.75rem 0;
        transition: all 0.2s ease;
    }
    
    .input-card:hover {
        border-color: var(--border-hover);
        box-shadow: var(--shadow-sm);
    }
    
    /* Metric Cards */
    .metric-card {
        background-color: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        padding: 1rem;
        text-align: center;
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        border-color: var(--border-hover);
        box-shadow: var(--shadow-sm);
    }
    
    /* Progress Container */
    .progress-container {
        background-color: var(--bg-tertiary);
        border-radius: 12px;
        height: 6px;
        margin: 1.5rem 0;
        overflow: hidden;
    }
    
    .progress-bar {
        height: 100%;
        background-color: var(--text-primary);
        border-radius: 12px;
        transition: width 0.5s ease;
    }
    
    /* Status Indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.875rem;
        color: var(--text-secondary);
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: var(--text-secondary);
    }
    
    .status-dot.complete {
        background-color: var(--success-color);
    }
    
    .status-dot.in-progress {
        background-color: var(--warning-color);
    }
    
    /* Signature Areas */
    .signature-area {
        background-color: var(--bg-secondary);
        border: 2px dashed var(--border-color);
        border-radius: var(--radius-md);
        padding: 1.25rem;
        text-align: center;
        min-height: 100px;
        transition: border-color 0.2s ease;
    }
    
    .signature-area:hover {
        border-color: var(--text-secondary);
    }
    
    /* Buttons */
    .primary-button {
        background-color: var(--text-primary);
        color: var(--bg-primary);
        border: 1px solid var(--text-primary);
        padding: 0.75rem 1.5rem;
        border-radius: var(--radius-sm);
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
        display: inline-block;
        text-align: center;
    }
    
    .primary-button:hover {
        background-color: var(--text-secondary);
        border-color: var(--text-secondary);
        color: var(--bg-primary);
        text-decoration: none;
    }
    
    .secondary-button {
        background-color: transparent;
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        padding: 0.75rem 1.5rem;
        border-radius: var(--radius-sm);
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .secondary-button:hover {
        background-color: var(--bg-tertiary);
        border-color: var(--border-hover);
    }
    
    /* Divider */
    .custom-divider {
        height: 1px;
        background-color: var(--border-color);
        margin: 1.5rem 0;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-secondary);
    }
    
    section[data-testid="stSidebar"] .stButton button {
        width: 100%;
        background-color: var(--text-primary);
        color: var(--bg-primary);
        border: none;
    }
    
    section[data-testid="stSidebar"] .stButton button:hover {
        background-color: var(--text-secondary);
    }
    
    /* Form Elements */
    .stTextInput input, .stTextArea textarea, .stNumberInput input, .stDateInput input, .stSelectbox select {
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus, .stDateInput input:focus {
        border-color: var(--text-primary) !important;
        box-shadow: 0 0 0 1px var(--text-primary) !important;
    }
    
    /* Data Editor */
    .dataframe {
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    /* Info Box */
    .info-box {
        background-color: var(--bg-secondary);
        border-left: 3px solid var(--border-color);
        padding: 1rem;
        margin: 1rem 0;
        color: var(--text-secondary);
    }
    
    /* Footer */
    .footer {
        background-color: var(--bg-secondary);
        color: var(--text-secondary);
        padding: 1.5rem;
        margin-top: 3rem;
        border-top: 1px solid var(--border-color);
        font-size: 0.875rem;
    }
    
    /* Required Field */
    .required-field::after {
        content: " *";
        color: var(--error-color);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 1px solid var(--border-color);
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: var(--text-secondary);
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: var(--radius-sm) var(--radius-sm) 0 0;
        margin-right: 1px;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: var(--bg-tertiary);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--bg-primary);
        color: var(--text-primary);
        border-bottom: 2px solid var(--text-primary);
    }
    
    /* Theme Indicator */
    .theme-indicator {
        font-size: 0.75rem;
        color: var(--text-tertiary);
        text-align: center;
        padding: 0.5rem;
        border-top: 1px solid var(--border-color);
        margin-top: 1rem;
    }
    
    /* Icon Styling */
    .icon {
        opacity: 0.8;
        margin-right: 0.5rem;
    }
    
    /* Table Styling */
    .data-table {
        background-color: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-sm);
        overflow: hidden;
    }
    
    /* File Upload */
    .stFileUploader {
        border: 1px dashed var(--border-color);
        border-radius: var(--radius-md);
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for storing data
if 'reports' not in st.session_state:
    st.session_state.reports = {}
if 'current_year' not in st.session_state:
    st.session_state.current_year = datetime.now().year
if 'completion_status' not in st.session_state:
    st.session_state.completion_status = {
        'church_info': False,
        'council_report': False,
        'lay_organizations': False,
        'trustees': False,
        'kindergarten': False,
        'workers': False,
        'leadership': False,
        'appendices': False
    }

# Initialize dataframes
if 'strategic_df' not in st.session_state:
    st.session_state.strategic_df = pd.DataFrame({
        'Strategic Area': [
            'MINISTRY EXPANSION',
            'LEADERSHIP DEVELOPMENT',
            'FINANCIAL SUSTAINABILITY and STRUCTURAL DEVELOPMENT',
            'PARTNERSHIP DEVELOPMENT',
            'CHURCH WORKERS HEALTH CARE DEVELOPMENT'
        ],
        'Objectives': [''] * 5,
        'Activities': [''] * 5,
        'Timeline': [''] * 5,
        'Responsible Persons': [''] * 5,
        'Budget (₱)': [0] * 5,
        'Status': [''] * 5
    })

if 'lay_df' not in st.session_state:
    st.session_state.lay_df = pd.DataFrame({
        'Organization': [
            'United Methodist Men',
            'United Methodist Women',
            'United Methodist Youth',
            'United Methodist Young Adults',
            'Children\'s Ministry',
            'Other (Specify)'
        ],
        'President': [''] * 6,
        'Contact Number': [''] * 6,
        'No. of Members': [0] * 6,
        'Regular Meetings': [''] * 6,
        'Key Programs': [''] * 6
    })

if 'trustee_df' not in st.session_state:
    st.session_state.trustee_df = pd.DataFrame({
        'Property Description': [''] * 3,
        'Date Acquired': [''] * 3,
        'Specific Project': [''] * 3,
        'Funding Source': [''] * 3,
        'Cost of CT (₱)': [0] * 3,
        'Total Cost (₱)': [0] * 3,
        'Remarks': [''] * 3
    })

if 'leadership_df' not in st.session_state:
    st.session_state.leadership_df = pd.DataFrame({
        'Position': [
            'Chairperson',
            'Vice-Chairperson',
            'Secretary',
            'Treasurer',
            'Auditor',
            'Board of Trustees Chair',
            'Lay Leader',
            'Other (Specify)'
        ],
        'Name': [''] * 8,
        'Contact Number': [''] * 8,
        'Email': [''] * 8,
        'Status (New/Old)': [''] * 8
    })

if 'appendix_df' not in st.session_state:
    st.session_state.appendix_df = pd.DataFrame({
        'Organization': [''] * 5,
        'Position': [''] * 5,
        'Name': [''] * 5,
        'Cell Phone Number': [''] * 5,
        'Facebook Account': [''] * 5,
        'Email': [''] * 5
    })

# Function to create downloadable report
def create_downloadable_report():
    """Generate the complete report as a downloadable file"""
    
    # Calculate completion percentage
    completed_sections = sum(st.session_state.completion_status.values())
    total_sections = len(st.session_state.completion_status)
    completion_percentage = (completed_sections / total_sections) * 100
    
    # Create a comprehensive report
    report_content = []
    
    # Header
    report_content.append("=" * 80)
    report_content.append("CHURCH ANNUAL REPORT")
    report_content.append("=" * 80)
    report_content.append(f"\nGenerated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    report_content.append(f"Reporting Year: {st.session_state.current_year}-{st.session_state.current_year + 1}")
    report_content.append(f"Completion Status: {completion_percentage:.1f}%")
    report_content.append("\n" + "=" * 80)
    
    # Church Information
    report_content.append("\n1. CHURCH BASIC INFORMATION")
    report_content.append("-" * 40)
    report_content.append(f"Church Name: {st.session_state.get('church_name', 'Not Provided')}")
    report_content.append(f"District: {st.session_state.get('district', 'Not Provided')}")
    report_content.append(f"Annual Conference: {st.session_state.get('annual_conference', 'Not Provided')}")
    report_content.append(f"Pastor: {st.session_state.get('pastor_name', 'Not Provided')}")
    report_content.append(f"Council Chairperson: {st.session_state.get('council_chairperson', 'Not Provided')}")
    
    # Vision, Mission, Core Values
    report_content.append("\nVision, Mission & Core Values:")
    report_content.append(f"Vision: {st.session_state.get('vision', 'Not Provided')}")
    report_content.append(f"Mission: {st.session_state.get('mission', 'Not Provided')}")
    report_content.append(f"Core Values: {st.session_state.get('core_values', 'Not Provided')}")
    
    # Church Council Report
    report_content.append("\n" + "=" * 80)
    report_content.append("\n2. CHURCH COUNCIL CHAIRPERSON REPORT")
    report_content.append("-" * 40)
    report_content.append(st.session_state.strategic_df.to_string(index=False))
    
    # Lay Organizations
    report_content.append("\n" + "=" * 80)
    report_content.append("\n3. LAY ORGANIZATIONS CONSOLIDATED REPORT")
    report_content.append("-" * 40)
    report_content.append(st.session_state.lay_df.to_string(index=False))
    
    # Board of Trustees
    report_content.append("\n" + "=" * 80)
    report_content.append("\n4. BOARD OF TRUSTEES REPORT")
    report_content.append("-" * 40)
    report_content.append(st.session_state.trustee_df.to_string(index=False))
    
    # Kindergarten Committee
    report_content.append("\n" + "=" * 80)
    report_content.append("\n5. KINDERGARTEN COMMITTEE REPORT")
    report_content.append("-" * 40)
    report_content.append(f"Nursery Enrollment: {st.session_state.get('nursery_enrolled', 0)}")
    report_content.append(f"Kindergarten Enrollment: {st.session_state.get('kinder_enrolled', 0)}")
    
    # Church Workers
    report_content.append("\n" + "=" * 80)
    report_content.append("\n6. CHURCH WORKERS REPORT")
    report_content.append("-" * 40)
    report_content.append(f"Total Church Membership: {st.session_state.get('membership', 0)}")
    
    # Leadership
    report_content.append("\n" + "=" * 80)
    report_content.append("\n7. LEADERSHIP 2026-2027")
    report_content.append("-" * 40)
    report_content.append(st.session_state.leadership_df.to_string(index=False))
    
    # Appendices
    report_content.append("\n" + "=" * 80)
    report_content.append("\n8. APPENDICES")
    report_content.append("-" * 40)
    report_content.append(st.session_state.appendix_df.to_string(index=False))
    
    report_content.append(f"\nAudit Completed: {st.session_state.get('audit', 'No')}")
    
    # Signatures
    report_content.append("\n" + "=" * 80)
    report_content.append("\nSIGNATURES")
    report_content.append("-" * 40)
    report_content.append(f"Church Council Chairperson: {st.session_state.get('council_signature', '')}")
    report_content.append(f"Administrative Pastor: {st.session_state.get('pastor_signature', '')}")
    report_content.append(f"Secretary: {st.session_state.get('secretary_signature', '')}")
    
    report_content.append("\n" + "=" * 80)
    report_content.append(f"\nREPORT COMPLETION: {completion_percentage:.1f}%")
    report_content.append("=" * 80)
    
    # Convert to string
    full_report = "\n".join(report_content)
    
    # Create a downloadable file
    b64 = base64.b64encode(full_report.encode()).decode()
    
    # Generate filename
    church_name = st.session_state.get('church_name', 'Church').replace(" ", "_")
    filename = f"{church_name}_Annual_Report_{datetime.now().strftime('%Y%m%d')}.txt"
    
    return b64, filename, full_report, completion_percentage

# Function to update completion status
def update_completion_status(section, is_complete):
    st.session_state.completion_status[section] = is_complete

# Minimalist Header
st.markdown("""
<div class="main-header">
    <strong>Church</strong> Annual Report System
</div>
""", unsafe_allow_html=True)

# Calculate completion percentage
completed_sections = sum(st.session_state.completion_status.values())
total_sections = len(st.session_state.completion_status)
completion_percentage = (completed_sections / total_sections) * 100

# Progress Bar
st.markdown(f"""
<div style="margin-bottom: 2rem;">
    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        <span style="color: var(--text-secondary); font-size: 0.875rem;">Report Progress</span>
        <span style="color: var(--text-primary); font-weight: 500;">{completion_percentage:.1f}%</span>
    </div>
    <div class="progress-container">
        <div class="progress-bar" style="width: {completion_percentage}%;"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar with minimal design
with st.sidebar:
    # Logo/Title
    st.markdown("""
    <div style="padding: 1.5rem 0; border-bottom: 1px solid var(--border-color);">
        <div style="font-size: 1.25rem; font-weight: 500; color: var(--text-primary);">
            ⛪ Reports
        </div>
        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.25rem;">
            Administrative Portal
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    st.markdown('<div style="font-size: 0.875rem; color: var(--text-secondary); margin: 1.5rem 0 0.75rem 0;">SECTIONS</div>', unsafe_allow_html=True)
    
    section_options = [
        ("📋", "Church Information", "church_info"),
        ("📊", "Council Report", "council_report"),
        ("👥", "Lay Organizations", "lay_organizations"),
        ("🏛️", "Board of Trustees", "trustees"),
        ("🏫", "Kindergarten", "kindergarten"),
        ("📚", "Grade Schools", "grade_schools"),
        ("👨‍💼", "Church Workers", "workers"),
        ("👑", "Leadership", "leadership"),
        ("🙋", "Youth Ministry", "youth_ministry"),
        ("📎", "Appendices", "appendices")
    ]
    
    selected_section = st.selectbox(
        "",
        [name for _, name, _ in section_options],
        label_visibility="collapsed",
        format_func=lambda x: f"{[icon for icon, name, _ in section_options if name == x][0]} {x}"
    )
    
    # Get selected key
    selected_key = [key for _, name, key in section_options if name == selected_section][0]
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Completion Status
    st.markdown('<div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.75rem;">STATUS</div>', unsafe_allow_html=True)
    
    for section, key in [("Church Info", "church_info"), ("Council", "council_report"), 
                         ("Lay Orgs", "lay_organizations"), ("Trustees", "trustees"),
                         ("Kindergarten", "kindergarten"), ("Workers", "workers"),
                         ("Leadership", "leadership"), ("Appendices", "appendices")]:
        status = st.session_state.completion_status[key]
        status_color = "var(--success-color)" if status else "var(--text-tertiary)"
        status_text = "✓" if status else "○"
        
        st.markdown(f"""
        <div class="status-indicator">
            <div class="status-dot {'complete' if status else ''}"></div>
            <span style="color: {'var(--text-primary)' if status else 'var(--text-tertiary)'}">{section}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Reporting Period
    st.markdown(f"""
    <div style="padding: 1rem; background-color: var(--bg-tertiary); border-radius: var(--radius-sm);">
        <div style="font-size: 0.875rem; color: var(--text-secondary);">Reporting Year</div>
        <div style="font-size: 1.125rem; color: var(--text-primary); font-weight: 500; margin-top: 0.25rem;">
            {st.session_state.current_year}-{st.session_state.current_year+1}
        </div>
        <div style="font-size: 0.75rem; color: var(--text-tertiary); margin-top: 0.25rem;">
            {datetime.now().strftime('%b %d, %Y')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Export Section
    st.markdown('<div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.75rem;">EXPORT</div>', unsafe_allow_html=True)
    
    if st.button("Generate Report", use_container_width=True, type="primary"):
        st.session_state.show_preview = True
    
    b64, filename, report_content, completion_percentage = create_downloadable_report()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}" class="primary-button" style="display: block; text-align: center; margin-top: 0.75rem;">Download Report</a>'
    st.markdown(href, unsafe_allow_html=True)
    
    # Theme Indicator
    st.markdown('<div class="theme-indicator">Theme: System</div>', unsafe_allow_html=True)

# Main content based on selected section
if selected_section == "Church Information":
    st.markdown('<div class="section-header">Church Information</div>', unsafe_allow_html=True)
    
    # Completion check
    def check_church_info_completion():
        required_fields = ['church_name', 'district', 'annual_conference', 'pastor_name', 'council_chairperson']
        is_complete = all(st.session_state.get(field, '') != '' for field in required_fields)
        update_completion_status('church_info', is_complete)
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown('<div class="subsection-header">Basic Details</div>', unsafe_allow_html=True)
            church_name = st.text_input("Church Name", key="church_name", on_change=check_church_info_completion)
            district = st.text_input("District", key="district", on_change=check_church_info_completion)
            annual_conference = st.text_input("Annual Conference", key="annual_conference", on_change=check_church_info_completion)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown('<div class="subsection-header">Leadership</div>', unsafe_allow_html=True)
            pastor_name = st.text_input("Pastor Name", key="pastor_name", on_change=check_church_info_completion)
            council_chairperson = st.text_input("Council Chairperson", key="council_chairperson", on_change=check_church_info_completion)
            report_date = st.date_input("Report Date", datetime.now(), key="report_date")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Vision, Mission, Core Values
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.markdown('<div class="subsection-header">Vision, Mission & Values</div>', unsafe_allow_html=True)
        vision = st.text_area("Annual Conference Vision", height=100, key="vision", on_change=check_church_info_completion)
        mission = st.text_area("Annual Conference Mission", height=100, key="mission", on_change=check_church_info_completion)
        core_values = st.text_area("Annual Conference Core Values", height=100, key="core_values", on_change=check_church_info_completion)
        st.markdown('</div>', unsafe_allow_html=True)

elif selected_section == "Council Report":
    st.markdown('<div class="section-header">Church Council Report</div>', unsafe_allow_html=True)
    
    # Strategic Plan
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.markdown('<div class="subsection-header">Strategic Plan</div>', unsafe_allow_html=True)
        edited_strategic = st.data_editor(
            st.session_state.strategic_df, 
            num_rows="dynamic", 
            use_container_width=True,
            key="strategic_editor"
        )
        st.session_state.strategic_df = edited_strategic
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Meetings Information
    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown('<div class="subsection-header">Meetings</div>', unsafe_allow_html=True)
            num_regular_meetings = st.number_input("Regular Meetings", min_value=0, value=12, key="num_meetings")
            num_special_meetings = st.number_input("Special Meetings", min_value=0, value=0, key="num_special")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown('<div class="subsection-header">Attendance</div>', unsafe_allow_html=True)
            average_attendance = st.number_input("Average Attendance (%)", min_value=0, max_value=100, value=85, key="avg_attendance")
            quorum_achieved = st.selectbox("Quorum Achieved", ["Always", "Mostly", "Sometimes", "Rarely"], key="quorum")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Key Decisions
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.markdown('<div class="subsection-header">Key Decisions</div>', unsafe_allow_html=True)
        key_decisions = st.text_area("", height=150, key="key_decisions", placeholder="Enter key decisions and resolutions...")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Update completion status
    update_completion_status('council_report', len(key_decisions) > 0)

elif selected_section == "Lay Organizations":
    st.markdown('<div class="section-header">Lay Organizations</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        edited_lay = st.data_editor(
            st.session_state.lay_df,
            num_rows="dynamic",
            use_container_width=True,
            key="lay_editor"
        )
        st.session_state.lay_df = edited_lay
        st.markdown('</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.markdown('<div class="subsection-header">Programs Summary</div>', unsafe_allow_html=True)
        programs_summary = st.text_area("", height=150, key="programs_summary", placeholder="Summarize programs and activities...")
        st.markdown('</div>', unsafe_allow_html=True)
    
    update_completion_status('lay_organizations', len(programs_summary) > 0)

elif selected_section == "Board of Trustees":
    st.markdown('<div class="section-header">Board of Trustees</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.markdown('<div class="subsection-header">Property Acquisition</div>', unsafe_allow_html=True)
        edited_trustee = st.data_editor(
            st.session_state.trustee_df,
            num_rows="dynamic",
            use_container_width=True,
            key="trustee_editor"
        )
        st.session_state.trustee_df = edited_trustee
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Info Box
    st.markdown("""
    <div class="info-box">
        <strong>Required Information:</strong><br>
        • Properties acquired after last charge conference<br>
        • New properties from June 01, 2025<br>
        • Inventory book must be presented
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.markdown('<div class="subsection-header">Inventory Upload</div>', unsafe_allow_html=True)
        inventory_files = st.file_uploader("", type=['pdf', 'xlsx', 'xls', 'docx'], accept_multiple_files=True, key="inventory_upload")
        st.markdown('</div>', unsafe_allow_html=True)
    
    has_data = not st.session_state.trustee_df['Property Description'].isna().all()
    update_completion_status('trustees', has_data)

elif selected_section == "Kindergarten":
    st.markdown('<div class="section-header">Kindergarten Committee</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown('<div class="subsection-header">Nursery</div>', unsafe_allow_html=True)
            nursery_enrolled = st.number_input("Enrolled", min_value=0, key="nursery_enrolled")
            nursery_current = st.number_input("Current", min_value=0, key="nursery_current")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown('<div class="subsection-header">Kindergarten</div>', unsafe_allow_html=True)
            kinder_enrolled = st.number_input("Enrolled", min_value=0, key="kinder_enrolled")
            kinder_current = st.number_input("Current", min_value=0, key="kinder_current")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown('<div class="subsection-header">Administrative</div>', unsafe_allow_html=True)
            status = st.selectbox("Status", ["Registered", "Recognized", "Permit to Operate", "Pending"], key="school_status")
            has_scholarships = st.radio("Scholarships", ["Yes", "No"], key="scholarships", horizontal=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.markdown('<div class="subsection-header">School Programs</div>', unsafe_allow_html=True)
        school_programs = st.text_area("", height=100, key="school_programs", placeholder="List programs and activities...")
        st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown('<div class="subsection-header">Registration Fee</div>', unsafe_allow_html=True)
            reg_fee = st.number_input("Amount (₱)", min_value=0.0, key="reg_fee", label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown('<div class="subsection-header">Miscellaneous</div>', unsafe_allow_html=True)
            misc_fee = st.number_input("Amount (₱)", min_value=0.0, key="misc_fee", label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown('<div class="subsection-header">Tuition Fee</div>', unsafe_allow_html=True)
            tuition_fee = st.number_input("Monthly (₱)", min_value=0.0, key="tuition_fee", label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)
    
    has_enrollment = (nursery_enrolled > 0 or kinder_enrolled > 0)
    update_completion_status('kindergarten', has_enrollment)

elif selected_section == "Grade Schools":
    st.markdown('<div class="section-header">Grade Schools</div>', unsafe_allow_html=True)
    
    grade_levels = ["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", "Grade 6"]
    
    grade_data = {
        'Grade Level': grade_levels,
        'Enrolled at Start': [0] * len(grade_levels),
        'Transferred In': [0] * len(grade_levels),
        'Transferred Out': [0] * len(grade_levels),
        'Current Enrollment': [0] * len(grade_levels),
        'Graduates': [0] * len(grade_levels)
    }
    
    grade_df = pd.DataFrame(grade_data)
    
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        edited_grade = st.data_editor(grade_df, num_rows="dynamic", use_container_width=True, key="grade_editor")
        st.session_state.grade_df = edited_grade
        st.markdown('</div>', unsafe_allow_html=True)
    
    total_enrolled = edited_grade['Enrolled at Start'].sum()
    total_current = edited_grade['Current Enrollment'].sum()
    total_graduates = edited_grade['Graduates'].sum()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.875rem; color: var(--text-secondary);">Enrolled</div>
            <div style="font-size: 1.5rem; color: var(--text-primary); font-weight: 500;">{total_enrolled}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.875rem; color: var(--text-secondary);">Current</div>
            <div style="font-size: 1.5rem; color: var(--text-primary); font-weight: 500;">{total_current}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.875rem; color: var(--text-secondary);">Graduates</div>
            <div style="font-size: 1.5rem; color: var(--text-primary); font-weight: 500;">{total_graduates}</div>
        </div>
        """, unsafe_allow_html=True)

elif selected_section == "Church Workers":
    st.markdown('<div class="section-header">Church Workers</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown('<div class="subsection-header">Pastor</div>', unsafe_allow_html=True)
            church_membership = st.number_input("Total Membership", min_value=0, key="membership")
            pastor_support = st.number_input("Monthly Support (₱)", min_value=0.0, key="pastor_support")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown('<div class="subsection-header">Deaconess</div>', unsafe_allow_html=True)
            deaconess_work = st.text_area("Nature of Work", height=100, key="deaconess_work")
            deaconess_support = st.number_input("Monthly Support (₱)", min_value=0.0, key="deaconess_support")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.markdown('<div class="subsection-header">Relationships & Situation</div>', unsafe_allow_html=True)
        workers_relationship = st.text_area("Worker Relationships", height=100, key="workers_relationship")
        housing_situation = st.selectbox("Housing Situation", ["Provided by Church", "Rented", "Own House", "Other"], key="housing")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.markdown('<div class="subsection-header">Recommendations</div>', unsafe_allow_html=True)
        ministry_entrants = st.text_area("Ministry Entrants", height=100, key="ministry_entrants")
        worker_benefits = st.text_area("Support Recommendations", height=100, key="worker_benefits")
        st.markdown('</div>', unsafe_allow_html=True)
    
    has_worker_info = (church_membership > 0 or len(deaconess_work) > 0)
    update_completion_status('workers', has_worker_info)

elif selected_section == "Leadership":
    st.markdown('<div class="section-header">Leadership 2026-2027</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.markdown('<div class="subsection-header">Council Officers</div>', unsafe_allow_html=True)
        edited_leadership = st.data_editor(
            st.session_state.leadership_df,
            num_rows="dynamic",
            use_container_width=True,
            key="leadership_editor"
        )
        st.session_state.leadership_df = edited_leadership
        st.markdown('</div>', unsafe_allow_html=True)
    
    committees = [
        'Worship Committee',
        'Finance Committee',
        'Administration Committee',
        'Membership & Evangelism',
        'Christian Education',
        'Social Concerns'
    ]
    
    committee_data = {
        'Committee': committees,
        'Chairperson': [''] * len(committees),
        'Members': [''] * len(committees)
    }
    
    committee_df = pd.DataFrame(committee_data)
    
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.markdown('<div class="subsection-header">Committees</div>', unsafe_allow_html=True)
        edited_committee = st.data_editor(committee_df, num_rows="dynamic", use_container_width=True, key="committee_editor")
        st.session_state.committee_df = edited_committee
        st.markdown('</div>', unsafe_allow_html=True)
    
    has_leadership_data = not st.session_state.leadership_df['Name'].isna().all()
    update_completion_status('leadership', has_leadership_data)

elif selected_section == "Appendices":
    st.markdown('<div class="section-header">Appendices</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.markdown('<div class="subsection-header">Contact List</div>', unsafe_allow_html=True)
        edited_appendix = st.data_editor(
            st.session_state.appendix_df,
            num_rows="dynamic",
            use_container_width=True,
            key="appendix_editor"
        )
        st.session_state.appendix_df = edited_appendix
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="subsection-header">Membership Statistics</div>', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        professing = st.number_input("Professing", min_value=0, key="professing", label_visibility="collapsed")
        st.markdown('<div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Professing</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        baptized = st.number_input("Baptized", min_value=0, key="baptized", label_visibility="collapsed")
        st.markdown('<div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Baptized</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        affiliate = st.number_input("Affiliate", min_value=0, key="affiliate", label_visibility="collapsed")
        st.markdown('<div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Affiliate</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        associate = st.number_input("Associate", min_value=0, key="associate", label_visibility="collapsed")
        st.markdown('<div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Associate</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col5:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        constituency = st.number_input("Constituency", min_value=0, key="constituency", label_visibility="collapsed")
        st.markdown('<div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Constituency</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown('<div class="subsection-header">Audit</div>', unsafe_allow_html=True)
            audit_completed = st.radio("Audit Completed", ["Yes", "No"], key="audit", horizontal=True)
            audit_date = st.date_input("Completion Date", key="audit_date")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown('<div class="subsection-header">Auditor</div>', unsafe_allow_html=True)
            auditor_name = st.text_input("Auditor Name", key="auditor_name")
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="subsection-header">Signatures</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="signature-area">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Council Chairperson</div>', unsafe_allow_html=True)
        council_signature = st.text_input("", key="council_signature", label_visibility="collapsed", placeholder="Name")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="signature-area">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Pastor</div>', unsafe_allow_html=True)
        pastor_signature = st.text_input("", key="pastor_signature", label_visibility="collapsed", placeholder="Name")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col3:
        st.markdown('<div class="signature-area">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Secretary</div>', unsafe_allow_html=True)
        secretary_signature = st.text_input("", key="secretary_signature", label_visibility="collapsed", placeholder="Name")
        st.markdown('</div>', unsafe_allow_html=True)
    
    has_signatures = (len(council_signature) > 0 or len(pastor_signature) > 0 or len(secretary_signature) > 0)
    has_membership = (professing > 0 or baptized > 0 or affiliate > 0 or associate > 0 or constituency > 0)
    update_completion_status('appendices', has_signatures or has_membership)

# Report Preview
if st.session_state.get('show_preview', False):
    st.markdown('<div class="section-header">Report Preview</div>', unsafe_allow_html=True)
    
    b64, filename, report_content, completion_percentage = create_downloadable_report()
    
    # Status indicator
    if completion_percentage < 50:
        status_msg = "Incomplete"
        status_color = "var(--error-color)"
    elif completion_percentage < 80:
        status_msg = "Partially Complete"
        status_color = "var(--warning-color)"
    else:
        status_msg = "Mostly Complete"
        status_color = "var(--success-color)"
    
    st.markdown(f"""
    <div style="padding: 1rem; background-color: var(--bg-secondary); border-radius: var(--radius-md); margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="color: var(--text-secondary); font-size: 0.875rem;">Status</div>
                <div style="color: {status_color}; font-weight: 500;">{status_msg}</div>
            </div>
            <div style="text-align: right;">
                <div style="color: var(--text-secondary); font-size: 0.875rem;">Completion</div>
                <div style="color: var(--text-primary); font-size: 1.25rem; font-weight: 500;">{completion_percentage:.0f}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("View Report Content", expanded=True):
        st.text_area("", report_content, height=300, label_visibility="collapsed")
    
    col1, col2 = st.columns(2)
    with col1:
        href = f'<a href="data:file/txt;base64,{b64}" download="{filename}" class="primary-button" style="display: block; text-align: center;">Download Report</a>'
        st.markdown(href, unsafe_allow_html=True)
    with col2:
        if st.button("Close Preview", type="secondary", use_container_width=True):
            st.session_state.show_preview = False
            st.rerun()

# Minimalist Footer
st.markdown("""
<div class="footer">
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem;">
        <div>
            <div style="font-weight: 500; color: var(--text-primary); margin-bottom: 0.5rem;">Requirements</div>
            <div style="font-size: 0.875rem; color: var(--text-secondary); line-height: 1.5;">
                • Committee signatures required<br>
                • Fasten reports in one folder<br>
                • Include workers' reports
            </div>
        </div>
        <div>
            <div style="font-weight: 500; color: var(--text-primary); margin-bottom: 0.5rem;">Mandatory</div>
            <div style="font-size: 0.875rem; color: var(--text-secondary); line-height: 1.5;">
                • Pre-Charge conference product<br>
                • Membership audit required<br>
                • Vision & Mission statement
            </div>
        </div>
        <div>
            <div style="font-weight: 500; color: var(--text-primary); margin-bottom: 0.5rem;">System</div>
            <div style="font-size: 0.875rem; color: var(--text-secondary); line-height: 1.5;">
                Church Annual Report System<br>
                Version 2.0 • {year}<br>
                All reports must be type written
            </div>
        </div>
    </div>
    <div class="custom-divider" style="margin: 1.5rem 0;"></div>
    <div style="text-align: center; color: var(--text-tertiary); font-size: 0.75rem;">
        Designed for clarity and efficiency • Adapts to system theme
    </div>
</div>
""".format(year=datetime.now().year), unsafe_allow_html=True)

# Completion reminder
if completion_percentage < 100:
    st.markdown(f"""
    <div class="info-box">
        <strong>Note:</strong> Report is {completion_percentage:.1f}% complete. 
        Complete all sections for a comprehensive report.
    </div>
    """, unsafe_allow_html=True)
