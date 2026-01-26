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

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        padding: 1rem;
        background-color: #F0F9FF;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #1E3A8A;
        background-color: #EFF6FF;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        margin-top: 2rem;
    }
    .subsection-header {
        font-size: 1.4rem;
        color: #1D4ED8;
        padding: 0.5rem;
        border-left: 4px solid #3B82F6;
    }
    .required-field::after {
        content: " *";
        color: red;
    }
    .signature-area {
        border: 2px dashed #ccc;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
        min-height: 100px;
    }
    .download-btn {
        background-color: #4CAF50;
        color: white;
        padding: 12px 24px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 16px;
        margin: 10px;
    }
    .download-btn:hover {
        background-color: #45a049;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for storing data
if 'reports' not in st.session_state:
    st.session_state.reports = {}
if 'current_year' not in st.session_state:
    st.session_state.current_year = datetime.now().year

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
    
    # Create a comprehensive report
    report_content = []
    
    # Church Information
    report_content.append("=" * 80)
    report_content.append("CHURCH ANNUAL REPORT")
    report_content.append("=" * 80)
    report_content.append(f"\nReport Date: {datetime.now().strftime('%B %d, %Y')}")
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
    report_content.append("\nEND OF REPORT")
    report_content.append("=" * 80)
    
    # Convert to string
    full_report = "\n".join(report_content)
    
    # Create a downloadable file
    b64 = base64.b64encode(full_report.encode()).decode()
    
    # Generate filename
    church_name = st.session_state.get('church_name', 'Church').replace(" ", "_")
    filename = f"{church_name}_Annual_Report_{datetime.now().strftime('%Y%m%d')}.txt"
    
    # Create download link
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}" class="download-btn">📥 Download Complete Report</a>'
    return href, full_report

# Main header
st.markdown('<div class="main-header">⛪ Church Annual Report System</div>', unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/church.png", width=100)
    st.title("Navigation")
    report_section = st.selectbox(
        "Select Report Section",
        ["Church Information", "Church Council Report", "Lay Organizations", 
         "Structural Development", "Board of Trustees", "Kindergarten Committee",
         "Grade Schools", "Church Workers", "Leadership", "Youth Ministry", "Appendices"]
    )
    
    st.divider()
    st.info(f"Reporting Year: {st.session_state.current_year}-{st.session_state.current_year+1}")
    
    # Download section in sidebar
    st.divider()
    st.markdown("### 📊 Report Generation")
    
    if st.button("🔄 Refresh Report Preview"):
        st.rerun()
    
    # Always show download button in sidebar
    st.markdown("---")
    st.markdown("### 📥 Download Options")
    
    # Generate download link
    download_link, report_content = create_downloadable_report()
    st.markdown(download_link, unsafe_allow_html=True)
    
    # Also show preview option
    if st.button("👁️ Preview Report"):
        st.session_state.show_preview = True

# Main content based on selected section
if report_section == "Church Information":
    st.markdown('<div class="section-header">📋 Church Basic Information</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        church_name = st.text_input("Church Name *", key="church_name")
        district = st.text_input("District *", key="district")
        annual_conference = st.text_input("Annual Conference *", key="annual_conference")
    
    with col2:
        pastor_name = st.text_input("Pastor Name *", key="pastor_name")
        council_chairperson = st.text_input("Church Council Chairperson *", key="council_chairperson")
        report_date = st.date_input("Report Date *", datetime.now(), key="report_date")
    
    # Vision, Mission, Core Values
    st.markdown('<div class="subsection-header">Vision, Mission & Core Values</div>', unsafe_allow_html=True)
    
    vision = st.text_area("Annual Conference Vision *", height=80, key="vision")
    mission = st.text_area("Annual Conference Mission *", height=80, key="mission")
    core_values = st.text_area("Annual Conference Core Values *", height=80, key="core_values")
    
    local_vision = st.text_area("Local Church Vision (if different)", height=80, key="local_vision")
    local_mission = st.text_area("Local Church Mission (if different)", height=80, key="local_mission")

elif report_section == "Church Council Report":
    st.markdown('<div class="section-header">📊 Church Council Chairperson Report</div>', unsafe_allow_html=True)
    
    # Strategic Plan in Tabular Form
    st.markdown('<div class="subsection-header">Strategic Plan (Tabular Form)</div>', unsafe_allow_html=True)
    
    # Use session state dataframe
    edited_strategic = st.data_editor(
        st.session_state.strategic_df, 
        num_rows="dynamic", 
        use_container_width=True,
        key="strategic_editor"
    )
    st.session_state.strategic_df = edited_strategic
    
    # Meetings Information
    st.markdown('<div class="subsection-header">Meetings Information</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        num_regular_meetings = st.number_input("Number of Regular Meetings", min_value=0, value=12, key="num_meetings")
        num_special_meetings = st.number_input("Number of Special Meetings", min_value=0, value=0, key="num_special")
    
    with col2:
        average_attendance = st.number_input("Average Attendance (%)", min_value=0, max_value=100, value=85, key="avg_attendance")
        quorum_achieved = st.selectbox("Quorum Achieved?", ["Always", "Mostly", "Sometimes", "Rarely"], key="quorum")
    
    # Key Decisions
    st.text_area("Key Decisions Made by Church Council", height=150, key="key_decisions")

elif report_section == "Lay Organizations":
    st.markdown('<div class="section-header">👥 Lay Organizations Consolidated Report</div>', unsafe_allow_html=True)
    
    # Lay Organizations Table
    edited_lay = st.data_editor(
        st.session_state.lay_df,
        num_rows="dynamic",
        use_container_width=True,
        key="lay_editor"
    )
    st.session_state.lay_df = edited_lay
    
    # Programs and Activities Summary
    st.markdown('<div class="subsection-header">Consolidated Programs & Activities</div>', unsafe_allow_html=True)
    programs_summary = st.text_area("Summary of all lay organization programs and activities", height=150, key="programs_summary")

elif report_section == "Board of Trustees":
    st.markdown('<div class="section-header">🏛️ Board of Trustees Report</div>', unsafe_allow_html=True)
    
    # Property Acquisition
    st.markdown('<div class="subsection-header">Property Acquisition (Tabular Form)</div>', unsafe_allow_html=True)
    
    edited_trustee = st.data_editor(
        st.session_state.trustee_df,
        num_rows="dynamic",
        use_container_width=True,
        key="trustee_editor"
    )
    st.session_state.trustee_df = edited_trustee
    
    # Instructions
    st.markdown("""
    **Required Information:**
    - a) All church properties acquired after the last charge conference 2024-2025
    - b) All newly acquired properties this C.Y. 2025-2026 - from June 01, 2025, to present
    - c) DATE ACQUIRED, SPECIFIC PROJECT, FUNDING (Donation/Gen. Fund) COST OF CT
    - d) TOTAL COST
    - e) Must present Inventory Book of Properties: Church, School, Parsonage, Deaconess Quarters
    """)
    
    # Inventory Upload
    st.markdown('<div class="subsection-header">Inventory Upload</div>', unsafe_allow_html=True)
    inventory_files = st.file_uploader("Upload Inventory Book/Sheets", 
                                     type=['pdf', 'xlsx', 'xls', 'docx'],
                                     accept_multiple_files=True,
                                     key="inventory_upload")
    
    if inventory_files:
        st.success(f"{len(inventory_files)} file(s) uploaded successfully")

elif report_section == "Kindergarten Committee":
    st.markdown('<div class="section-header">🏫 Kindergarten Committee Report</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Nursery")
        nursery_enrolled = st.number_input("No. of pupils enrolled", min_value=0, key="nursery_enrolled")
        nursery_transferred_in = st.number_input("Transferred in", min_value=0, key="nursery_in")
        nursery_transferred_out = st.number_input("Transferred out", min_value=0, key="nursery_out")
        nursery_dropouts = st.number_input("Dropouts", min_value=0, key="nursery_dropouts")
        nursery_current = st.number_input("Current no. of pupils", min_value=0, key="nursery_current")
    
    with col2:
        st.subheader("Kindergarten")
        kinder_enrolled = st.number_input("No. of pupils enrolled", min_value=0, key="kinder_enrolled")
        kinder_transferred_in = st.number_input("Transferred in", min_value=0, key="kinder_in")
        kinder_transferred_out = st.number_input("Transferred out", min_value=0, key="kinder_out")
        kinder_dropouts = st.number_input("Dropouts", min_value=0, key="kinder_dropouts")
        kinder_current = st.number_input("Current no. of pupils", min_value=0, key="kinder_current")
    
    with col3:
        st.subheader("Administrative")
        status = st.selectbox("Status", 
                            ["Registered", "Recognized", "Permit to Operate", "Pending"],
                            key="school_status")
        has_scholarships = st.radio("Scholarships offered?", ["Yes", "No"], key="scholarships")
        
        if has_scholarships == "Yes":
            scholarship_details = st.text_area("Scholarship details", key="scholarship_details")
    
    # School Programs
    st.markdown('<div class="subsection-header">School Programs</div>', unsafe_allow_html=True)
    school_programs = st.text_area("List school programs and activities", height=100, key="school_programs")
    
    # Financial Information
    st.markdown('<div class="subsection-header">Financial Information</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        reg_fee = st.number_input("Registration Fee (₱)", min_value=0.0, key="reg_fee")
    with col2:
        misc_fee = st.number_input("Miscellaneous Fee (₱)", min_value=0.0, key="misc_fee")
    with col3:
        tuition_fee = st.number_input("Monthly Tuition Fee (₱)", min_value=0.0, key="tuition_fee")
    
    # Financial Report Upload
    financial_report = st.file_uploader("Upload Financial Statements", type=['pdf', 'xlsx', 'xls'], key="financial_upload")

elif report_section == "Grade Schools":
    st.markdown('<div class="section-header">📚 Grade Schools Report</div>', unsafe_allow_html=True)
    
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
    edited_grade = st.data_editor(grade_df, num_rows="dynamic", use_container_width=True, key="grade_editor")
    
    # Store in session state
    st.session_state.grade_df = edited_grade
    
    # Summary Statistics
    total_enrolled = edited_grade['Enrolled at Start'].sum()
    total_current = edited_grade['Current Enrollment'].sum()
    total_graduates = edited_grade['Number of Graduates'].sum()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Enrolled", total_enrolled)
    with col2:
        st.metric("Current Enrollment", total_current)
    with col3:
        st.metric("Total Graduates", total_graduates)

elif report_section == "Church Workers":
    st.markdown('<div class="section-header">👨‍💼 Church Workers Report</div>', unsafe_allow_html=True)
    
    # Pastor Report
    st.markdown('<div class="subsection-header">Pastor Report</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        church_membership = st.number_input("Total Church Membership", min_value=0, key="membership")
        pastor_support = st.number_input("Actual Support Received (Monthly ₱)", min_value=0.0, key="pastor_support")
    
    with col2:
        nature_of_work = st.text_area("Nature of Work", height=100, key="pastor_work")
        additional_info = st.text_area("Additional Information", height=100, key="pastor_additional")
    
    # Deaconess Report
    st.markdown('<div class="subsection-header">Deaconess Report</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        deaconess_work = st.text_area("Nature of Work", height=100, key="deaconess_work")
    with col2:
        deaconess_support = st.number_input("Actual Support Received (Monthly ₱)", min_value=0.0, key="deaconess_support")
    
    # Church Workers Relationships
    st.markdown('<div class="subsection-header">Church Workers Relationships</div>', unsafe_allow_html=True)
    workers_relationship = st.text_area("State the relationship between church workers", height=100, key="workers_relationship")
    
    # Church Workers Situation
    st.markdown('<div class="subsection-header">Church Workers Situation</div>', unsafe_allow_html=True)
    
    housing_situation = st.selectbox("Housing Situation", 
                                    ["Provided by Church", "Rented with Allowance", "Own House", "Other"],
                                    key="housing")
    support_situation = st.text_area("Support received (cash/in-kind) as mandated by Annual Conference", 
                                   height=100, key="support_situation")
    
    # Recommendations
    st.markdown('<div class="subsection-header">Recommendations</div>', unsafe_allow_html=True)
    
    ministry_entrants = st.text_area("Recommend those who want to enter ministry (Pastor, Deaconess, Lay Minister)", 
                                    height=100, key="ministry_entrants")
    
    lay_servants = st.text_area("Recommend those who want to be added as Lay Servant Ministers", 
                               height=100, key="lay_servants")
    
    worker_benefits = st.text_area("Recommend church workers support and other benefits", 
                                  height=100, key="worker_benefits")

elif report_section == "Leadership":
    st.markdown('<div class="section-header">👑 Leadership 2026-2027</div>', unsafe_allow_html=True)
    
    # Church Council Officers
    st.markdown('<div class="subsection-header">Church Council Officers (CY 2026-2027)</div>', unsafe_allow_html=True)
    
    edited_leadership = st.data_editor(
        st.session_state.leadership_df,
        num_rows="dynamic",
        use_container_width=True,
        key="leadership_editor"
    )
    st.session_state.leadership_df = edited_leadership
    
    # Committee Members
    st.markdown('<div class="subsection-header">Committee Chairpersons & Members</div>', unsafe_allow_html=True)
    
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
    edited_committee = st.data_editor(committee_df, num_rows="dynamic", use_container_width=True, key="committee_editor")
    st.session_state.committee_df = edited_committee

elif report_section == "Youth Ministry":
    st.markdown('<div class="section-header">🙋 Youth Ministry Report</div>', unsafe_allow_html=True)
    
    # Youth Group Information
    col1, col2 = st.columns(2)
    with col1:
        youth_president = st.text_input("Youth President", key="youth_president")
        youth_contact = st.text_input("Contact Number", key="youth_contact")
        total_youth = st.number_input("Total Youth Members", min_value=0, key="total_youth")
    
    with col2:
        active_youth = st.number_input("Active Youth Members", min_value=0, key="active_youth")
        regular_meetings = st.text_input("Regular Meeting Schedule", key="youth_meetings")
        average_attendance = st.number_input("Average Attendance", min_value=0, key="youth_attendance")
    
    # Youth Programs
    st.markdown('<div class="subsection-header">Youth Ministry Programs & Activities</div>', unsafe_allow_html=True)
    youth_programs = st.text_area("List all youth programs and activities", height=150, key="youth_programs")
    
    # Ministry Involvement
    st.markdown('<div class="subsection-header">Youth Involvement in Church Ministry</div>', unsafe_allow_html=True)
    ministry_involvement = st.text_area("Describe youth involvement in church ministry (Paragraphs 266-268)", 
                                      height=150, key="ministry_involvement")

elif report_section == "Appendices":
    st.markdown('<div class="section-header">📎 Appendices</div>', unsafe_allow_html=True)
    
    # Lay Organization Officers with Contacts
    st.markdown('<div class="subsection-header">Lay Organization Officers Contact List</div>', unsafe_allow_html=True)
    
    edited_appendix = st.data_editor(
        st.session_state.appendix_df,
        num_rows="dynamic",
        use_container_width=True,
        key="appendix_editor"
    )
    st.session_state.appendix_df = edited_appendix
    
    # Membership Statistics
    st.markdown('<div class="subsection-header">Membership Statistics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        professing = st.number_input("Professing Members", min_value=0, key="professing")
    with col2:
        baptized = st.number_input("Baptized Members", min_value=0, key="baptized")
    with col3:
        affiliate = st.number_input("Affiliate Members", min_value=0, key="affiliate")
    with col4:
        associate = st.number_input("Associate Members", min_value=0, key="associate")
    with col5:
        constituency = st.number_input("Constituency", min_value=0, key="constituency")
    
    # Audit Confirmation
    st.markdown('<div class="subsection-header">Audit Confirmation</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        audit_completed = st.radio("Has the membership been audited?", ["Yes", "No"], key="audit")
    with col2:
        audit_date = st.date_input("Audit Completion Date", key="audit_date")
    with col3:
        auditor_name = st.text_input("Auditor Name", key="auditor_name")
    
    # Signatures
    st.markdown('<div class="subsection-header">Signatures</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="signature-area">Church Council Chairperson</div>', unsafe_allow_html=True)
        council_signature = st.text_input("Name", key="council_signature", label_visibility="collapsed")
        council_date = st.date_input("Date", key="council_date", label_visibility="collapsed")
        
    with col2:
        st.markdown('<div class="signature-area">Administrative Pastor</div>', unsafe_allow_html=True)
        pastor_signature = st.text_input("Name", key="pastor_signature", label_visibility="collapsed")
        pastor_date = st.date_input("Date", key="pastor_date", label_visibility="collapsed")
        
    with col3:
        st.markdown('<div class="signature-area">Secretary</div>', unsafe_allow_html=True)
        secretary_signature = st.text_input("Name", key="secretary_signature", label_visibility="collapsed")
        secretary_date = st.date_input("Date", key="secretary_date", label_visibility="collapsed")

# Report Preview Section
if st.session_state.get('show_preview', False):
    st.markdown("---")
    st.markdown('<div class="section-header">📄 Report Preview</div>', unsafe_allow_html=True)
    
    # Generate and show preview
    _, report_content = create_downloadable_report()
    
    # Show in expandable preview
    with st.expander("Click to view full report preview", expanded=True):
        st.text_area("Report Preview", report_content, height=400)
    
    # Option to close preview
    if st.button("Close Preview"):
        st.session_state.show_preview = False
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>⛪ Church Annual Report System | All reports must be computerized or type written</p>
    <p><strong>Note:</strong> Committee and board chairpersons and members should sign all reports</p>
    <p>Reports should be fastened in one folder including workers' reports</p>
    <p style="color: #dc3545;"><strong>Important:</strong> Product of the Pre-Charge conference is a must.</p>
</div>
""", unsafe_allow_html=True)

# Information message at the bottom
st.info("💡 **Tip:** Navigate through all sections using the sidebar, fill in the required information, then download your complete report using the download button in the sidebar.")
