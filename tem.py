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

# Enhanced Aesthetic CSS with Complementary Colors (Blue & Orange)
st.markdown("""
<style>
    /* Main Colors: Blue (#1E3A8A) and Complementary Orange (#F97316) */
    :root {
        --primary-blue: #1E3A8A;
        --secondary-blue: #3B82F6;
        --light-blue: #EFF6FF;
        --accent-orange: #F97316;
        --light-orange: #FFEDD5;
        --dark-gray: #374151;
        --light-gray: #F9FAFB;
        --white: #FFFFFF;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Main Header */
    .main-header {
        font-size: 2.8rem;
        color: var(--primary-blue);
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, var(--white) 0%, var(--light-blue) 100%);
        border-radius: 16px;
        margin-bottom: 2.5rem;
        box-shadow: 0 4px 20px rgba(30, 58, 138, 0.1);
        border: 2px solid var(--secondary-blue);
        font-weight: 700;
        letter-spacing: -0.5px;
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: "⛪";
        position: absolute;
        right: 30px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 3rem;
        opacity: 0.1;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.9rem;
        color: var(--primary-blue);
        background: linear-gradient(90deg, var(--light-blue) 0%, var(--white) 100%);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
        border-left: 6px solid var(--accent-orange);
        box-shadow: 0 2px 12px rgba(30, 58, 138, 0.08);
        font-weight: 600;
    }
    
    /* Subsection Headers */
    .subsection-header {
        font-size: 1.5rem;
        color: var(--dark-gray);
        padding: 0.8rem 1.2rem;
        border-left: 4px solid var(--secondary-blue);
        background: var(--white);
        border-radius: 8px;
        margin-top: 1.8rem;
        margin-bottom: 1rem;
        font-weight: 500;
        box-shadow: 0 1px 6px rgba(0, 0, 0, 0.05);
    }
    
    /* Card Style for Input Groups */
    .input-card {
        background: var(--white);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        border: 1px solid #e5e7eb;
        transition: all 0.3s ease;
    }
    
    .input-card:hover {
        box-shadow: 0 4px 20px rgba(30, 58, 138, 0.12);
        transform: translateY(-2px);
    }
    
    /* Required Field */
    .required-field::after {
        content: " *";
        color: #EF4444;
        font-weight: bold;
    }
    
    /* Signature Area */
    .signature-area {
        background: linear-gradient(135deg, var(--light-blue) 0%, var(--white) 100%);
        border: 2px dashed var(--secondary-blue);
        padding: 1.5rem;
        margin: 1rem 0;
        text-align: center;
        min-height: 120px;
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    
    .signature-area:hover {
        border-color: var(--accent-orange);
        background: linear-gradient(135deg, var(--light-orange) 0%, var(--white) 100%);
    }
    
    /* Download Button */
    .download-btn {
        background: linear-gradient(135deg, var(--accent-orange) 0%, #EA580C 100%);
        color: white;
        padding: 14px 28px;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        font-size: 16px;
        font-weight: 600;
        margin: 10px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
    }
    
    .download-btn:hover {
        background: linear-gradient(135deg, #EA580C 0%, #C2410C 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(249, 115, 22, 0.4);
        color: white;
        text-decoration: none;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--primary-blue) 0%, #1E40AF 100%);
    }
    
    /* Metric Cards */
    .metric-card {
        background: var(--white);
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
        border-top: 4px solid var(--accent-orange);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: var(--light-blue);
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        font-weight: 500;
        border: 1px solid #e5e7eb;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-blue) !important;
        color: white !important;
    }
    
    /* Progress Bar */
    .progress-container {
        background: var(--light-blue);
        border-radius: 10px;
        padding: 3px;
        margin: 20px 0;
    }
    
    .progress-bar {
        height: 10px;
        background: linear-gradient(90deg, var(--accent-orange) 0%, var(--secondary-blue) 100%);
        border-radius: 8px;
        transition: width 0.5s ease;
    }
    
    /* Success Message */
    .success-message {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
    
    /* Warning/Info Message */
    .info-message {
        background: linear-gradient(135deg, var(--light-blue) 0%, #DBEAFE 100%);
        color: var(--primary-blue);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid var(--secondary-blue);
        font-weight: 500;
    }
    
    /* Footer Styling */
    .footer {
        background: linear-gradient(135deg, var(--primary-blue) 0%, #1E40AF 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-top: 3rem;
        text-align: center;
        box-shadow: 0 -4px 20px rgba(30, 58, 138, 0.2);
    }
    
    /* Icon Styling */
    .section-icon {
        color: var(--accent-orange);
        margin-right: 10px;
        font-size: 1.4em;
    }
    
    /* Custom Button */
    .custom-button {
        background: linear-gradient(135deg, var(--secondary-blue) 0%, var(--primary-blue) 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .custom-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    
    /* Data Editor Styling */
    .dataframe {
        border-radius: 10px !important;
        overflow: hidden !important;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08) !important;
    }
    
    /* Form Input Focus */
    .stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus, .stDateInput input:focus {
        border-color: var(--accent-orange) !important;
        box-shadow: 0 0 0 2px rgba(249, 115, 22, 0.2) !important;
    }
    
    /* Status Indicator */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-complete {
        background-color: #10B981;
    }
    
    .status-in-progress {
        background-color: #F59E0B;
    }
    
    .status-pending {
        background-color: #EF4444;
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

# Initialize dataframes in session state
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
    
    # Header with completion status
    report_content.append("=" * 80)
    report_content.append(f"CHURCH ANNUAL REPORT - COMPLETION: {completion_percentage:.1f}%")
    report_content.append("=" * 80)
    report_content.append(f"\nGenerated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    report_content.append(f"Reporting Year: {st.session_state.current_year}-{st.session_state.current_year + 1}")
    report_content.append("\n" + "=" * 80)
    
    # Church Basic Information
    report_content.append("\nSECTION 1: CHURCH BASIC INFORMATION")
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
    if st.session_state.get('local_vision'):
        report_content.append(f"Local Church Vision: {st.session_state.get('local_vision')}")
    if st.session_state.get('local_mission'):
        report_content.append(f"Local Church Mission: {st.session_state.get('local_mission')}")
    
    # Church Council Report
    report_content.append("\n" + "=" * 80)
    report_content.append("\nSECTION 2: CHURCH COUNCIL CHAIRPERSON REPORT")
    report_content.append("-" * 40)
    
    report_content.append("\nSTRATEGIC PLAN:")
    report_content.append(st.session_state.strategic_df.to_string(index=False))
    
    report_content.append("\n\nMEETINGS INFORMATION:")
    report_content.append(f"Number of Regular Meetings: {st.session_state.get('num_meetings', 0)}")
    report_content.append(f"Number of Special Meetings: {st.session_state.get('num_special', 0)}")
    report_content.append(f"Average Attendance: {st.session_state.get('avg_attendance', 0)}%")
    report_content.append(f"Quorum Achieved: {st.session_state.get('quorum', 'Not Provided')}")
    report_content.append(f"Key Decisions: {st.session_state.get('key_decisions', 'None recorded')}")
    
    # Lay Organizations
    report_content.append("\n" + "=" * 80)
    report_content.append("\nSECTION 3: LAY ORGANIZATIONS CONSOLIDATED REPORT")
    report_content.append("-" * 40)
    report_content.append(st.session_state.lay_df.to_string(index=False))
    report_content.append(f"\nPrograms Summary: {st.session_state.get('programs_summary', 'Not Provided')}")
    
    # Board of Trustees
    report_content.append("\n" + "=" * 80)
    report_content.append("\nSECTION 4: BOARD OF TRUSTEES REPORT")
    report_content.append("-" * 40)
    report_content.append(st.session_state.trustee_df.to_string(index=False))
    
    # Kindergarten Committee
    report_content.append("\n" + "=" * 80)
    report_content.append("\nSECTION 5: KINDERGARTEN COMMITTEE REPORT")
    report_content.append("-" * 40)
    report_content.append(f"Nursery Enrollment: {st.session_state.get('nursery_enrolled', 0)}")
    report_content.append(f"Kindergarten Enrollment: {st.session_state.get('kinder_enrolled', 0)}")
    report_content.append(f"School Status: {st.session_state.get('school_status', 'Not Provided')}")
    report_content.append(f"Scholarships Offered: {st.session_state.get('scholarships', 'No')}")
    
    # Church Workers
    report_content.append("\n" + "=" * 80)
    report_content.append("\nSECTION 6: CHURCH WORKERS REPORT")
    report_content.append("-" * 40)
    report_content.append(f"Total Church Membership: {st.session_state.get('membership', 0)}")
    report_content.append(f"Pastor Support: ₱{st.session_state.get('pastor_support', 0):.2f}")
    report_content.append(f"Deaconess Support: ₱{st.session_state.get('deaconess_support', 0):.2f}")
    report_content.append(f"Workers Relationship: {st.session_state.get('workers_relationship', 'Not Provided')}")
    report_content.append(f"Housing Situation: {st.session_state.get('housing', 'Not Provided')}")
    
    # Leadership
    report_content.append("\n" + "=" * 80)
    report_content.append("\nSECTION 7: LEADERSHIP 2026-2027")
    report_content.append("-" * 40)
    report_content.append(st.session_state.leadership_df.to_string(index=False))
    
    # Appendices
    report_content.append("\n" + "=" * 80)
    report_content.append("\nSECTION 8: APPENDICES")
    report_content.append("-" * 40)
    
    report_content.append("\nLAY ORGANIZATION OFFICERS CONTACT LIST:")
    report_content.append(st.session_state.appendix_df.to_string(index=False))
    
    report_content.append("\n\nMEMBERSHIP STATISTICS:")
    report_content.append(f"Professing Members: {st.session_state.get('professing', 0)}")
    report_content.append(f"Baptized Members: {st.session_state.get('baptized', 0)}")
    report_content.append(f"Affiliate Members: {st.session_state.get('affiliate', 0)}")
    report_content.append(f"Associate Members: {st.session_state.get('associate', 0)}")
    report_content.append(f"Constituency: {st.session_state.get('constituency', 0)}")
    
    report_content.append(f"\nAudit Completed: {st.session_state.get('audit', 'No')}")
    report_content.append(f"Audit Date: {st.session_state.get('audit_date', 'Not Provided')}")
    report_content.append(f"Auditor: {st.session_state.get('auditor_name', 'Not Provided')}")
    
    # Signatures
    report_content.append("\n" + "=" * 80)
    report_content.append("\nSIGNATURES")
    report_content.append("-" * 40)
    report_content.append(f"\nChurch Council Chairperson: {st.session_state.get('council_signature', '')}")
    report_content.append(f"Date: {st.session_state.get('council_date', '')}")
    report_content.append(f"\nAdministrative Pastor: {st.session_state.get('pastor_signature', '')}")
    report_content.append(f"Date: {st.session_state.get('pastor_date', '')}")
    report_content.append(f"\nSecretary: {st.session_state.get('secretary_signature', '')}")
    report_content.append(f"Date: {st.session_state.get('secretary_date', '')}")
    
    report_content.append("\n" + "=" * 80)
    report_content.append(f"\nREPORT STATUS: {completion_percentage:.1f}% COMPLETE")
    report_content.append("=" * 80)
    
    # Convert to string
    full_report = "\n".join(report_content)
    
    # Create a downloadable file
    b64 = base64.b64encode(full_report.encode()).decode()
    
    # Generate filename
    church_name = st.session_state.get('church_name', 'Church').replace(" ", "_")
    filename = f"{church_name}_Annual_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    
    return b64, filename, full_report, completion_percentage

# Function to update completion status
def update_completion_status(section, is_complete):
    st.session_state.completion_status[section] = is_complete

# Main header with elegant design
st.markdown("""
<div class="main-header">
    ⛪ Church Annual Report System
    <div style="font-size: 1.2rem; color: #6B7280; margin-top: 10px; font-weight: 400;">
        Comprehensive Reporting Tool for Church Administration
    </div>
</div>
""", unsafe_allow_html=True)

# Calculate completion percentage
completed_sections = sum(st.session_state.completion_status.values())
total_sections = len(st.session_state.completion_status)
completion_percentage = (completed_sections / total_sections) * 100

# Progress bar at the top
st.markdown(f"""
<div class="progress-container">
    <div class="progress-bar" style="width: {completion_percentage}%;"></div>
</div>
<div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
    <span style="color: #374151; font-weight: 500;">Report Completion</span>
    <span style="color: #1E3A8A; font-weight: 600;">{completion_percentage:.1f}% Complete</span>
</div>
""", unsafe_allow_html=True)

# Sidebar navigation with enhanced design
with st.sidebar:
    # Church logo/icon
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <div style="background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); 
                    width: 80px; height: 80px; border-radius: 20px; 
                    display: flex; align-items: center; justify-content: center; 
                    margin: 0 auto 15px; box-shadow: 0 4px 12px rgba(30, 58, 138, 0.3);">
            <span style="font-size: 40px; color: white;">⛪</span>
        </div>
        <h3 style="color: white; margin: 0;">Church Reports</h3>
        <p style="color: #DBEAFE; margin: 5px 0 0;">Administrative Portal</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Navigation
    st.markdown("### 📋 Navigation")
    report_section = st.selectbox(
        "Select Report Section",
        ["📋 Church Information", "📊 Church Council Report", "👥 Lay Organizations", 
         "🏛️ Board of Trustees", "🏫 Kindergarten Committee", "📚 Grade Schools",
         "👨‍💼 Church Workers", "👑 Leadership", "🙋 Youth Ministry", "📎 Appendices"],
        label_visibility="collapsed"
    )
    
    # Extract section name for logic
    section_map = {
        "📋 Church Information": "church_info",
        "📊 Church Council Report": "council_report",
        "👥 Lay Organizations": "lay_organizations",
        "🏛️ Board of Trustees": "trustees",
        "🏫 Kindergarten Committee": "kindergarten",
        "📚 Grade Schools": "grade_schools",
        "👨‍💼 Church Workers": "workers",
        "👑 Leadership": "leadership",
        "🙋 Youth Ministry": "youth_ministry",
        "📎 Appendices": "appendices"
    }
    
    current_section_key = section_map[report_section]
    
    st.divider()
    
    # Status indicators
    st.markdown("### 📈 Completion Status")
    for section, status in st.session_state.completion_status.items():
        status_color = "#10B981" if status else "#9CA3AF"
        status_text = "✓" if status else "○"
        section_name = section.replace("_", " ").title()
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin: 8px 0;">
            <span style="color: {status_color}; font-size: 1.2rem; margin-right: 10px;">{status_text}</span>
            <span style="color: #E5E7EB;">{section_name}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Year and date info
    st.markdown(f"""
    <div style="background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 10px;">
        <p style="color: #DBEAFE; margin: 0; font-weight: 500;">📅 Reporting Year</p>
        <p style="color: white; font-size: 1.4rem; margin: 5px 0; font-weight: 600;">
            {st.session_state.current_year}-{st.session_state.current_year+1}
        </p>
        <p style="color: #DBEAFE; margin: 5px 0 0; font-size: 0.9rem;">
            {datetime.now().strftime('%B %d, %Y')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Download section
    st.markdown("### 📥 Export Report")
    
    if st.button("🔄 Generate Full Report", use_container_width=True):
        st.session_state.generate_report = True
    
    # Always show download button
    b64, filename, report_content, completion_percentage = create_downloadable_report()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}" class="download-btn">📥 Download Complete Report</a>'
    st.markdown(href, unsafe_allow_html=True)
    
    if completion_percentage < 100:
        st.warning(f"Report is {completion_percentage:.1f}% complete. Some sections may be missing.")

# Main content based on selected section
if "Church Information" in report_section:
    st.markdown('<div class="section-header"><span class="section-icon">📋</span> Church Basic Information</div>', unsafe_allow_html=True)
    
    # Completion check
    def check_church_info_completion():
        required_fields = ['church_name', 'district', 'annual_conference', 'pastor_name', 'council_chairperson']
        is_complete = all(st.session_state.get(field, '') != '' for field in required_fields)
        update_completion_status('church_info', is_complete)
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            church_name = st.text_input("Church Name *", key="church_name", on_change=check_church_info_completion)
            district = st.text_input("District *", key="district", on_change=check_church_info_completion)
            annual_conference = st.text_input("Annual Conference *", key="annual_conference", on_change=check_church_info_completion)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            pastor_name = st.text_input("Pastor Name *", key="pastor_name", on_change=check_church_info_completion)
            council_chairperson = st.text_input("Church Council Chairperson *", key="council_chairperson", on_change=check_church_info_completion)
            report_date = st.date_input("Report Date *", datetime.now(), key="report_date")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Vision, Mission, Core Values
    st.markdown('<div class="subsection-header"><span class="section-icon">🌟</span> Vision, Mission & Core Values</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        vision = st.text_area("Annual Conference Vision *", height=100, key="vision", on_change=check_church_info_completion)
        mission = st.text_area("Annual Conference Mission *", height=100, key="mission", on_change=check_church_info_completion)
        core_values = st.text_area("Annual Conference Core Values *", height=100, key="core_values", on_change=check_church_info_completion)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.markdown("#### Local Church Vision & Mission (Optional)")
        local_vision = st.text_area("Local Church Vision (if different)", height=80, key="local_vision")
        local_mission = st.text_area("Local Church Mission (if different)", height=80, key="local_mission")
        st.markdown('</div>', unsafe_allow_html=True)

elif "Church Council Report" in report_section:
    st.markdown('<div class="section-header"><span class="section-icon">📊</span> Church Council Chairperson Report</div>', unsafe_allow_html=True)
    
    # Strategic Plan in Tabular Form
    st.markdown('<div class="subsection-header"><span class="section-icon">🎯</span> Strategic Plan (Tabular Form)</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        edited_strategic = st.data_editor(
            st.session_state.strategic_df, 
            num_rows="dynamic", 
            use_container_width=True,
            key="strategic_editor"
        )
        st.session_state.strategic_df = edited_strategic
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Meetings Information
    st.markdown('<div class="subsection-header"><span class="section-icon">📅</span> Meetings Information</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            num_regular_meetings = st.number_input("Number of Regular Meetings", min_value=0, value=12, key="num_meetings")
            num_special_meetings = st.number_input("Number of Special Meetings", min_value=0, value=0, key="num_special")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            average_attendance = st.number_input("Average Attendance (%)", min_value=0, max_value=100, value=85, key="avg_attendance")
            quorum_achieved = st.selectbox("Quorum Achieved?", ["Always", "Mostly", "Sometimes", "Rarely"], key="quorum")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Key Decisions
    st.markdown('<div class="subsection-header"><span class="section-icon">💡</span> Key Decisions</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        key_decisions = st.text_area("Key Decisions Made by Church Council", height=150, key="key_decisions", 
                                   placeholder="Enter key decisions and resolutions made during council meetings...")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Update completion status
    update_completion_status('council_report', len(key_decisions) > 0)

elif "Lay Organizations" in report_section:
    st.markdown('<div class="section-header"><span class="section-icon">👥</span> Lay Organizations Consolidated Report</div>', unsafe_allow_html=True)
    
    # Lay Organizations Table
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
    
    # Programs and Activities Summary
    st.markdown('<div class="subsection-header"><span class="section-icon">📋</span> Consolidated Programs & Activities</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        programs_summary = st.text_area("Summary of all lay organization programs and activities", height=150, key="programs_summary",
                                      placeholder="Summarize the key programs, activities, and achievements of all lay organizations...")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Update completion status
    update_completion_status('lay_organizations', len(programs_summary) > 0)

elif "Board of Trustees" in report_section:
    st.markdown('<div class="section-header"><span class="section-icon">🏛️</span> Board of Trustees Report</div>', unsafe_allow_html=True)
    
    # Property Acquisition
    st.markdown('<div class="subsection-header"><span class="section-icon">🏠</span> Property Acquisition (Tabular Form)</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        edited_trustee = st.data_editor(
            st.session_state.trustee_df,
            num_rows="dynamic",
            use_container_width=True,
            key="trustee_editor"
        )
        st.session_state.trustee_df = edited_trustee
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Instructions in info card
    st.markdown("""
    <div class="info-message">
        <strong>📋 Required Information:</strong><br>
        • All church properties acquired after the last charge conference 2024-2025<br>
        • All newly acquired properties this C.Y. 2025-2026 - from June 01, 2025, to present<br>
        • DATE ACQUIRED, SPECIFIC PROJECT, FUNDING (Donation/Gen. Fund) COST OF CT<br>
        • TOTAL COST<br>
        • Must present Inventory Book of Properties: Church, School, Parsonage, Deaconess Quarters
    </div>
    """, unsafe_allow_html=True)
    
    # Inventory Upload
    st.markdown('<div class="subsection-header"><span class="section-icon">📎</span> Inventory Upload</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        inventory_files = st.file_uploader("Upload Inventory Book/Sheets", 
                                         type=['pdf', 'xlsx', 'xls', 'docx'],
                                         accept_multiple_files=True,
                                         key="inventory_upload")
        
        if inventory_files:
            st.success(f"✅ {len(inventory_files)} file(s) uploaded successfully")
            st.markdown('<div class="success-message">Files uploaded and attached to report</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Update completion status
    has_data = not st.session_state.trustee_df['Property Description'].isna().all()
    update_completion_status('trustees', has_data)

elif "Kindergarten Committee" in report_section:
    st.markdown('<div class="section-header"><span class="section-icon">🏫</span> Kindergarten Committee Report</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.markdown("#### 👶 Nursery")
        nursery_enrolled = st.number_input("No. of pupils enrolled", min_value=0, key="nursery_enrolled")
        nursery_transferred_in = st.number_input("Transferred in", min_value=0, key="nursery_in")
        nursery_transferred_out = st.number_input("Transferred out", min_value=0, key="nursery_out")
        nursery_dropouts = st.number_input("Dropouts", min_value=0, key="nursery_dropouts")
        nursery_current = st.number_input("Current no. of pupils", min_value=0, key="nursery_current")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.markdown("#### 🧒 Kindergarten")
        kinder_enrolled = st.number_input("No. of pupils enrolled", min_value=0, key="kinder_enrolled")
        kinder_transferred_in = st.number_input("Transferred in", min_value=0, key="kinder_in")
        kinder_transferred_out = st.number_input("Transferred out", min_value=0, key="kinder_out")
        kinder_dropouts = st.number_input("Dropouts", min_value=0, key="kinder_dropouts")
        kinder_current = st.number_input("Current no. of pupils", min_value=0, key="kinder_current")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.markdown("#### 📋 Administrative")
        status = st.selectbox("Status", 
                            ["Registered", "Recognized", "Permit to Operate", "Pending"],
                            key="school_status")
        has_scholarships = st.radio("Scholarships offered?", ["Yes", "No"], key="scholarships")
        
        if has_scholarships == "Yes":
            scholarship_details = st.text_area("Scholarship details", key="scholarship_details")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # School Programs
    st.markdown('<div class="subsection-header"><span class="section-icon">📚</span> School Programs</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        school_programs = st.text_area("List school programs and activities", height=100, key="school_programs",
                                     placeholder="List educational programs, extracurricular activities, special events...")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Financial Information
    st.markdown('<div class="subsection-header"><span class="section-icon">💰</span> Financial Information</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            reg_fee = st.number_input("Registration Fee (₱)", min_value=0.0, key="reg_fee")
            st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            misc_fee = st.number_input("Miscellaneous Fee (₱)", min_value=0.0, key="misc_fee")
            st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            tuition_fee = st.number_input("Monthly Tuition Fee (₱)", min_value=0.0, key="tuition_fee")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Financial Report Upload
    st.markdown('<div class="subsection-header"><span class="section-icon">📄</span> Financial Statements</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        financial_report = st.file_uploader("Upload Financial Statements", type=['pdf', 'xlsx', 'xls'], key="financial_upload")
        if financial_report:
            st.success("✅ Financial statements uploaded successfully")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Update completion status
    has_enrollment = (nursery_enrolled > 0 or kinder_enrolled > 0)
    update_completion_status('kindergarten', has_enrollment)

elif "Grade Schools" in report_section:
    st.markdown('<div class="section-header"><span class="section-icon">📚</span> Grade Schools Report</div>', unsafe_allow_html=True)
    
    grade_levels = ["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", "Grade 6"]
    
    grade_data = {
        'Grade Level': grade_levels,
        'Enrolled at Start': [0] * len(grade_levels),
        'Transferred In': [0] * len(grade_levels),
        'Transferred Out': [0] * len(grade_levels),
        'Dropouts': [0] * len(grade_levels),
        'Current Enrollment': [0] * len(grade_levels),
        'Number of Graduates': [0] * len(grade_levels)
    }
    
    grade_df = pd.DataFrame(grade_data)
    
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        edited_grade = st.data_editor(grade_df, num_rows="dynamic", use_container_width=True, key="grade_editor")
        st.session_state.grade_df = edited_grade
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Summary Statistics in metric cards
    total_enrolled = edited_grade['Enrolled at Start'].sum()
    total_current = edited_grade['Current Enrollment'].sum()
    total_graduates = edited_grade['Number of Graduates'].sum()
    
    st.markdown('<div class="subsection-header"><span class="section-icon">📊</span> Summary Statistics</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #6B7280; margin-bottom: 5px;">Total Enrolled</div>
            <div style="font-size: 2rem; color: #1E3A8A; font-weight: 700;">{total_enrolled}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #6B7280; margin-bottom: 5px;">Current Enrollment</div>
            <div style="font-size: 2rem; color: #1E3A8A; font-weight: 700;">{total_current}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #6B7280; margin-bottom: 5px;">Total Graduates</div>
            <div style="font-size: 2rem; color: #1E3A8A; font-weight: 700;">{total_graduates}</div>
        </div>
        """, unsafe_allow_html=True)

elif "Church Workers" in report_section:
    st.markdown('<div class="section-header"><span class="section-icon">👨‍💼</span> Church Workers Report</div>', unsafe_allow_html=True)
    
    # Pastor Report
    st.markdown('<div class="subsection-header"><span class="section-icon">🙏</span> Pastor Report</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            church_membership = st.number_input("Total Church Membership", min_value=0, key="membership")
            pastor_support = st.number_input("Actual Support Received (Monthly ₱)", min_value=0.0, key="pastor_support")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            nature_of_work = st.text_area("Nature of Work", height=100, key="pastor_work")
            additional_info = st.text_area("Additional Information", height=100, key="pastor_additional")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Deaconess Report
    st.markdown('<div class="subsection-header"><span class="section-icon">👩‍⚕️</span> Deaconess Report</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            deaconess_work = st.text_area("Nature of Work", height=100, key="deaconess_work")
            st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            deaconess_support = st.number_input("Actual Support Received (Monthly ₱)", min_value=0.0, key="deaconess_support")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Church Workers Relationships
    st.markdown('<div class="subsection-header"><span class="section-icon">🤝</span> Church Workers Relationships</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        workers_relationship = st.text_area("State the relationship between church workers", height=100, key="workers_relationship")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Church Workers Situation
    st.markdown('<div class="subsection-header"><span class="section-icon">🏠</span> Church Workers Situation</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        housing_situation = st.selectbox("Housing Situation", 
                                        ["Provided by Church", "Rented with Allowance", "Own House", "Other"],
                                        key="housing")
        support_situation = st.text_area("Support received (cash/in-kind) as mandated by Annual Conference", 
                                       height=100, key="support_situation")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Recommendations
    st.markdown('<div class="subsection-header"><span class="section-icon">📋</span> Recommendations</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        ministry_entrants = st.text_area("Recommend those who want to enter ministry (Pastor, Deaconess, Lay Minister)", 
                                        height=100, key="ministry_entrants")
        
        lay_servants = st.text_area("Recommend those who want to be added as Lay Servant Ministers", 
                                   height=100, key="lay_servants")
        
        worker_benefits = st.text_area("Recommend church workers support and other benefits", 
                                      height=100, key="worker_benefits")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Update completion status
    has_worker_info = (church_membership > 0 or len(nature_of_work) > 0 or len(deaconess_work) > 0)
    update_completion_status('workers', has_worker_info)

elif "Leadership" in report_section:
    st.markdown('<div class="section-header"><span class="section-icon">👑</span> Leadership 2026-2027</div>', unsafe_allow_html=True)
    
    # Church Council Officers
    st.markdown('<div class="subsection-header"><span class="section-icon">👥</span> Church Council Officers (CY 2026-2027)</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        edited_leadership = st.data_editor(
            st.session_state.leadership_df,
            num_rows="dynamic",
            use_container_width=True,
            key="leadership_editor"
        )
        st.session_state.leadership_df = edited_leadership
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Committee Members
    st.markdown('<div class="subsection-header"><span class="section-icon">📋</span> Committee Chairpersons & Members</div>', unsafe_allow_html=True)
    
    committees = [
        'Worship Committee',
        'Finance Committee',
        'Administration Committee',
        'Membership & Evangelism',
        'Christian Education',
        'Social Concerns',
        'Youth Ministry',
        'Children\'s Ministry'
    ]
    
    committee_data = {
        'Committee': committees,
        'Chairperson': [''] * len(committees),
        'Members (List names)': [''] * len(committees)
    }
    
    committee_df = pd.DataFrame(committee_data)
    
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        edited_committee = st.data_editor(committee_df, num_rows="dynamic", use_container_width=True, key="committee_editor")
        st.session_state.committee_df = edited_committee
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Update completion status
    has_leadership_data = not st.session_state.leadership_df['Name'].isna().all()
    update_completion_status('leadership', has_leadership_data)

elif "Appendices" in report_section:
    st.markdown('<div class="section-header"><span class="section-icon">📎</span> Appendices</div>', unsafe_allow_html=True)
    
    # Lay Organization Officers with Contacts
    st.markdown('<div class="subsection-header"><span class="section-icon">📞</span> Lay Organization Officers Contact List</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        edited_appendix = st.data_editor(
            st.session_state.appendix_df,
            num_rows="dynamic",
            use_container_width=True,
            key="appendix_editor"
        )
        st.session_state.appendix_df = edited_appendix
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Membership Statistics
    st.markdown('<div class="subsection-header"><span class="section-icon">📊</span> Membership Statistics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        professing = st.number_input("Professing Members", min_value=0, key="professing")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        baptized = st.number_input("Baptized Members", min_value=0, key="baptized")
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        affiliate = st.number_input("Affiliate Members", min_value=0, key="affiliate")
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        associate = st.number_input("Associate Members", min_value=0, key="associate")
        st.markdown('</div>', unsafe_allow_html=True)
    with col5:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        constituency = st.number_input("Constituency", min_value=0, key="constituency")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Audit Confirmation
    st.markdown('<div class="subsection-header"><span class="section-icon">✅</span> Audit Confirmation</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            audit_completed = st.radio("Has the membership been audited?", ["Yes", "No"], key="audit")
            st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            audit_date = st.date_input("Audit Completion Date", key="audit_date")
            st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            auditor_name = st.text_input("Auditor Name", key="auditor_name")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Signatures
    st.markdown('<div class="subsection-header"><span class="section-icon">✍️</span> Signatures</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="signature-area">', unsafe_allow_html=True)
        st.markdown("**Church Council Chairperson**")
        council_signature = st.text_input("Name", key="council_signature", label_visibility="collapsed")
        council_date = st.date_input("Date", key="council_date", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="signature-area">', unsafe_allow_html=True)
        st.markdown("**Administrative Pastor**")
        pastor_signature = st.text_input("Name", key="pastor_signature", label_visibility="collapsed")
        pastor_date = st.date_input("Date", key="pastor_date", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col3:
        st.markdown('<div class="signature-area">', unsafe_allow_html=True)
        st.markdown("**Secretary**")
        secretary_signature = st.text_input("Name", key="secretary_signature", label_visibility="collapsed")
        secretary_date = st.date_input("Date", key="secretary_date", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Update completion status
    has_signatures = (len(council_signature) > 0 or len(pastor_signature) > 0 or len(secretary_signature) > 0)
    has_membership = (professing > 0 or baptized > 0 or affiliate > 0 or associate > 0 or constituency > 0)
    update_completion_status('appendices', has_signatures or has_membership)

# Report Preview Section
if st.session_state.get('generate_report', False):
    st.markdown("---")
    st.markdown('<div class="section-header"><span class="section-icon">📄</span> Report Preview</div>', unsafe_allow_html=True)
    
    # Generate and show preview
    b64, filename, report_content, completion_percentage = create_downloadable_report()
    
    # Completion status indicator
    if completion_percentage < 50:
        status_color = "#EF4444"
        status_msg = "⚠️ Low Completion"
    elif completion_percentage < 80:
        status_color = "#F59E0B"
        status_msg = "📋 Moderate Completion"
    else:
        status_color = "#10B981"
        status_msg = "✅ High Completion"
    
    st.markdown(f"""
    <div style="background: {status_color}15; border-left: 4px solid {status_color}; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <strong style="color: {status_color};">{status_msg}</strong>
                <div style="color: #6B7280; font-size: 0.9rem;">Your report is {completion_percentage:.1f}% complete</div>
            </div>
            <div style="font-size: 1.5rem; font-weight: 700; color: {status_color};">{completion_percentage:.0f}%</div>
        </div>
        <div class="progress-container" style="margin-top: 10px;">
            <div class="progress-bar" style="width: {completion_percentage}%; background: {status_color};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show in expandable preview
    with st.expander("📋 Click to view full report preview", expanded=True):
        st.text_area("Report Preview", report_content, height=400)
    
    # Download buttons in preview
    col1, col2 = st.columns(2)
    with col1:
        href = f'<a href="data:file/txt;base64,{b64}" download="{filename}" class="download-btn">📥 Download Complete Report</a>'
        st.markdown(href, unsafe_allow_html=True)
    with col2:
        if st.button("Close Preview", use_container_width=True):
            st.session_state.generate_report = False
            st.rerun()

# Enhanced Footer
st.markdown("""
<div class="footer">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div style="text-align: left;">
            <h4 style="margin: 0; color: white;">⛪ Church Annual Report System</h4>
            <p style="margin: 5px 0 0; color: #DBEAFE; font-size: 0.9rem;">
                Comprehensive Reporting Tool for Church Administration
            </p>
        </div>
        <div style="text-align: right;">
            <p style="margin: 0; color: #DBEAFE; font-size: 0.9rem;">
                Version 2.0 • {year}
            </p>
            <p style="margin: 5px 0 0; color: #DBEAFE; font-size: 0.8rem;">
                All reports must be computerized or type written
            </p>
        </div>
    </div>
    <hr style="border-color: rgba(255,255,255,0.2); margin: 20px 0;">
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; text-align: left;">
        <div>
            <p style="color: white; font-weight: 500; margin-bottom: 10px;">📋 Requirements</p>
            <ul style="color: #DBEAFE; font-size: 0.85rem; margin: 0; padding-left: 20px;">
                <li>Committee signatures required</li>
                <li>Fasten in one folder</li>
                <li>Include workers' reports</li>
            </ul>
        </div>
        <div>
            <p style="color: white; font-weight: 500; margin-bottom: 10px;">✅ Mandatory</p>
            <ul style="color: #DBEAFE; font-size: 0.85rem; margin: 0; padding-left: 20px;">
                <li>Pre-Charge conference product</li>
                <li>Membership audit required</li>
                <li>Vision & Mission statement</li>
            </ul>
        </div>
        <div>
            <p style="color: white; font-weight: 500; margin-bottom: 10px;">📞 Contact</p>
            <p style="color: #DBEAFE; font-size: 0.85rem; margin: 0;">
                For support and assistance with reporting
            </p>
        </div>
    </div>
</div>
""".format(year=datetime.now().year), unsafe_allow_html=True)

# Information message at the bottom
if completion_percentage < 100:
    st.markdown(f"""
    <div class="info-message">
        💡 <strong>Tip:</strong> Your report is {completion_percentage:.1f}% complete. 
        Navigate through all sections using the sidebar to complete missing information. 
        Required sections are marked with an asterisk (*).
    </div>
    """, unsafe_allow_html=True)
