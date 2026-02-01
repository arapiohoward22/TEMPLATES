import streamlit as st
import pandas as pd
from datetime import datetime
import io
import base64
import sqlite3
import hashlib
import json
from typing import Dict, List, Optional, Tuple
import os

# Database setup
DB_NAME = "church_reports.db"

def init_database():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Users table for authentication
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            church_name TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Reports table
    c.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            report_name TEXT NOT NULL,
            church_name TEXT,
            reporting_year TEXT,
            completion_percentage REAL DEFAULT 0,
            data_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_archived BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Templates table
    c.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            data_json TEXT NOT NULL,
            created_by INTEGER,
            is_public BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Insert default admin user if not exists
    c.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if c.fetchone()[0] == 0:
        admin_hash = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute('''
            INSERT INTO users (username, email, password_hash, full_name, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@churchreports.com', admin_hash, 'System Administrator', 'admin'))
    
    # Insert default template if not exists
    c.execute("SELECT COUNT(*) FROM templates WHERE name = 'Default Template'")
    if c.fetchone()[0] == 0:
        default_data = {
            'strategic_df': pd.DataFrame({
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
            }).to_dict(),
            'lay_df': pd.DataFrame({
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
            }).to_dict(),
            'trustee_df': pd.DataFrame({
                'Property Description': [''] * 3,
                'Date Acquired': [''] * 3,
                'Specific Project': [''] * 3,
                'Funding Source': [''] * 3,
                'Cost of CT (₱)': [0] * 3,
                'Total Cost (₱)': [0] * 3,
                'Remarks': [''] * 3
            }).to_dict(),
            'leadership_df': pd.DataFrame({
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
            }).to_dict(),
            'appendix_df': pd.DataFrame({
                'Organization': [''] * 5,
                'Position': [''] * 5,
                'Name': [''] * 5,
                'Cell Phone Number': [''] * 5,
                'Facebook Account': [''] * 5,
                'Email': [''] * 5
            }).to_dict()
        }
        c.execute('''
            INSERT INTO templates (name, description, data_json, created_by, is_public)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Default Template', 'Standard church reporting template', json.dumps(default_data), 1, 1))
    
    conn.commit()
    conn.close()

# Initialize database
init_database()

# Authentication functions
def hash_password(password: str) -> str:
    """Hash password for storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username: str, password: str) -> Optional[Tuple]:
    """Authenticate user and return user data"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    password_hash = hash_password(password)
    c.execute('''
        SELECT id, username, email, full_name, church_name, role 
        FROM users 
        WHERE username = ? AND password_hash = ?
    ''', (username, password_hash))
    
    user = c.fetchone()
    conn.close()
    
    if user:
        # Update last login
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user[0],))
        conn.commit()
        conn.close()
    
    return user

def create_user(username: str, password: str, email: str = None, full_name: str = None, church_name: str = None) -> bool:
    """Create a new user account"""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        password_hash = hash_password(password)
        c.execute('''
            INSERT INTO users (username, email, password_hash, full_name, church_name)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, password_hash, full_name, church_name))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def get_user_reports(user_id: int) -> List[Dict]:
    """Get all reports for a specific user"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('''
        SELECT id, report_name, church_name, reporting_year, 
               completion_percentage, created_at, updated_at, is_archived
        FROM reports 
        WHERE user_id = ? AND is_archived = 0
        ORDER BY updated_at DESC
    ''', (user_id,))
    
    reports = []
    for row in c.fetchall():
        reports.append({
            'id': row[0],
            'report_name': row[1],
            'church_name': row[2],
            'reporting_year': row[3],
            'completion_percentage': row[4],
            'created_at': row[5],
            'updated_at': row[6],
            'is_archived': row[7]
        })
    
    conn.close()
    return reports

def save_report(user_id: int, report_name: str, church_name: str, data_dict: Dict) -> int:
    """Save report to database and return report ID"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Convert dataframes to dict for JSON serialization
    serializable_data = {}
    for key, value in data_dict.items():
        if isinstance(value, pd.DataFrame):
            serializable_data[key] = value.to_dict()
        else:
            serializable_data[key] = value
    
    data_json = json.dumps(serializable_data)
    
    # Check if report with same name exists for this user
    c.execute('SELECT id FROM reports WHERE user_id = ? AND report_name = ?', (user_id, report_name))
    existing_report = c.fetchone()
    
    if existing_report:
        # Update existing report
        c.execute('''
            UPDATE reports 
            SET church_name = ?, data_json = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (church_name, data_json, existing_report[0]))
        report_id = existing_report[0]
    else:
        # Create new report
        reporting_year = f"{datetime.now().year}-{datetime.now().year + 1}"
        completion_percentage = data_dict.get('completion_percentage', 0)
        
        c.execute('''
            INSERT INTO reports (user_id, report_name, church_name, reporting_year, completion_percentage, data_json)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, report_name, church_name, reporting_year, completion_percentage, data_json))
        
        report_id = c.lastrowid
    
    conn.commit()
    conn.close()
    return report_id

def load_report(report_id: int, user_id: int = None) -> Optional[Dict]:
    """Load report from database"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    if user_id:
        c.execute('SELECT data_json FROM reports WHERE id = ? AND user_id = ?', (report_id, user_id))
    else:
        c.execute('SELECT data_json FROM reports WHERE id = ?', (report_id,))
    
    result = c.fetchone()
    conn.close()
    
    if result:
        data = json.loads(result[0])
        
        # Convert dicts back to dataframes
        for key in ['strategic_df', 'lay_df', 'trustee_df', 'leadership_df', 'appendix_df']:
            if key in data and isinstance(data[key], dict):
                data[key] = pd.DataFrame(data[key])
        
        return data
    
    return None

def delete_report(report_id: int, user_id: int) -> bool:
    """Soft delete (archive) a report"""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        c.execute('UPDATE reports SET is_archived = 1 WHERE id = ? AND user_id = ?', (report_id, user_id))
        
        conn.commit()
        conn.close()
        return True
    except:
        return False

def get_templates() -> List[Dict]:
    """Get available templates"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('''
        SELECT id, name, description, created_by, created_at 
        FROM templates 
        WHERE is_public = 1
        ORDER BY name
    ''')
    
    templates = []
    for row in c.fetchall():
        templates.append({
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'created_by': row[3],
            'created_at': row[4]
        })
    
    conn.close()
    return templates

def load_template(template_id: int) -> Optional[Dict]:
    """Load template data"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('SELECT data_json FROM templates WHERE id = ?', (template_id,))
    result = c.fetchone()
    conn.close()
    
    if result:
        data = json.loads(result[0])
        
        # Convert dicts back to dataframes
        for key in ['strategic_df', 'lay_df', 'trustee_df', 'leadership_df', 'appendix_df']:
            if key in data and isinstance(data[key], dict):
                data[key] = pd.DataFrame(data[key])
        
        return data
    
    return None

# Page configuration
st.set_page_config(
    page_title="Church Reporting System",
    page_icon="⛪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimalist CSS with OS theme sync
st.markdown("""
<style>
    :root {
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
    
    .stApp {
        background-color: var(--bg-primary);
        color: var(--text-primary);
        transition: background-color 0.3s ease, color 0.3s ease;
    }
    
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
    
    .section-header {
        font-size: 1.5rem;
        font-weight: 500;
        color: var(--text-primary);
        padding: 0.75rem 0;
        margin: 2rem 0 1rem 0;
        border-bottom: 2px solid var(--border-color);
    }
    
    .subsection-header {
        font-size: 1.1rem;
        font-weight: 500;
        color: var(--text-primary);
        padding: 0.5rem 0;
        margin: 1.5rem 0 1rem 0;
    }
    
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
    
    .custom-divider {
        height: 1px;
        background-color: var(--border-color);
        margin: 1.5rem 0;
    }
    
    section[data-testid="stSidebar"] {
        background-color: var(--bg-secondary);
    }
    
    .footer {
        background-color: var(--bg-secondary);
        color: var(--text-secondary);
        padding: 1.5rem;
        margin-top: 3rem;
        border-top: 1px solid var(--border-color);
        font-size: 0.875rem;
    }
    
    .info-box {
        background-color: var(--bg-secondary);
        border-left: 3px solid var(--border-color);
        padding: 1rem;
        margin: 1rem 0;
        color: var(--text-secondary);
    }
    
    .login-container {
        max-width: 400px;
        margin: 4rem auto;
        padding: 2rem;
        background-color: var(--bg-secondary);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-color);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.user_role = None

if 'current_report_id' not in st.session_state:
    st.session_state.current_report_id = None
    st.session_state.current_report_name = None

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
def initialize_dataframes():
    """Initialize or reset dataframes in session state"""
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

    st.session_state.trustee_df = pd.DataFrame({
        'Property Description': [''] * 3,
        'Date Acquired': [''] * 3,
        'Specific Project': [''] * 3,
        'Funding Source': [''] * 3,
        'Cost of CT (₱)': [0] * 3,
        'Total Cost (₱)': [0] * 3,
        'Remarks': [''] * 3
    })

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

    st.session_state.appendix_df = pd.DataFrame({
        'Organization': [''] * 5,
        'Position': [''] * 5,
        'Name': [''] * 5,
        'Cell Phone Number': [''] * 5,
        'Facebook Account': [''] * 5,
        'Email': [''] * 5
    })

if 'strategic_df' not in st.session_state:
    initialize_dataframes()

# Authentication functions for UI
def login():
    """Handle user login"""
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; margin-bottom: 2rem;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 1.5rem; font-weight: 500; color: var(--text-primary);">Church Reporting System</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Sign in to access your reports</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Sign In")
        
        if submit:
            if username and password:
                user = authenticate_user(username, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user_id = user[0]
                    st.session_state.username = user[1]
                    st.session_state.user_email = user[2]
                    st.session_state.user_full_name = user[3]
                    st.session_state.user_church_name = user[4]
                    st.session_state.user_role = user[5]
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.warning("Please enter both username and password")
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Create new account
    with st.expander("Create New Account"):
        with st.form("register_form"):
            new_username = st.text_input("Choose Username")
            new_password = st.text_input("Choose Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            new_email = st.text_input("Email (optional)")
            new_full_name = st.text_input("Full Name (optional)")
            new_church = st.text_input("Church Name (optional)")
            register = st.form_submit_button("Create Account")
            
            if register:
                if new_username and new_password:
                    if new_password == confirm_password:
                        if create_user(new_username, new_password, new_email, new_full_name, new_church):
                            st.success("Account created successfully! Please sign in.")
                        else:
                            st.error("Username already exists. Please choose another.")
                    else:
                        st.error("Passwords do not match")
                else:
                    st.warning("Please enter username and password")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Demo credentials
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem; color: var(--text-tertiary); font-size: 0.75rem;">
        Demo credentials: admin / admin123
    </div>
    """, unsafe_allow_html=True)

def logout():
    """Handle user logout"""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.user_role = None
    st.session_state.current_report_id = None
    st.session_state.current_report_name = None
    initialize_dataframes()
    st.rerun()

# Report management functions
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
    report_content.append(f"Church: {st.session_state.get('church_name', 'Not Provided')}")
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

def save_current_report():
    """Save current report to database"""
    if not st.session_state.authenticated:
        st.error("Please log in to save reports")
        return False
    
    # Get current data
    data_to_save = {}
    
    # Collect all session state data
    for key in st.session_state:
        if key not in ['_last_hash', 'authenticated', 'user', 'user_id', 'username', 'user_role', 
                       'current_report_id', 'current_report_name', 'reports', 'completion_status',
                       'show_preview', 'generate_report']:
            data_to_save[key] = st.session_state[key]
    
    # Add completion status
    completed_sections = sum(st.session_state.completion_status.values())
    total_sections = len(st.session_state.completion_status)
    completion_percentage = (completed_sections / total_sections) * 100
    data_to_save['completion_percentage'] = completion_percentage
    
    # Get report name
    report_name = st.session_state.get('church_name', 'Untitled Report')
    if st.session_state.current_report_name:
        report_name = st.session_state.current_report_name
    
    # Save to database
    report_id = save_report(
        st.session_state.user_id,
        report_name,
        st.session_state.get('church_name', ''),
        data_to_save
    )
    
    st.session_state.current_report_id = report_id
    st.session_state.current_report_name = report_name
    
    return True

def load_selected_report(report_id: int):
    """Load a report from database into session state"""
    report_data = load_report(report_id, st.session_state.user_id)
    
    if report_data:
        # Clear current session state except authentication
        auth_state = {
            'authenticated': st.session_state.authenticated,
            'user_id': st.session_state.user_id,
            'username': st.session_state.username,
            'user_role': st.session_state.user_role,
            'current_report_id': report_id
        }
        
        # Get report name
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT report_name FROM reports WHERE id = ?', (report_id,))
        report_name = c.fetchone()[0]
        conn.close()
        
        st.session_state.current_report_name = report_name
        
        # Clear session state
        for key in list(st.session_state.keys()):
            if key not in auth_state:
                del st.session_state[key]
        
        # Restore authentication state
        for key, value in auth_state.items():
            st.session_state[key] = value
        
        # Load report data
        for key, value in report_data.items():
            st.session_state[key] = value
        
        # Initialize completion status if not in loaded data
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
        
        st.success(f"Report '{report_name}' loaded successfully!")
        st.rerun()
    else:
        st.error("Failed to load report")

# Update completion status function
def update_completion_status(section, is_complete):
    st.session_state.completion_status[section] = is_complete

# Main app logic
if not st.session_state.authenticated:
    login()
else:
    # Main header with user info
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        st.markdown(f"""
        <div class="main-header">
            <strong>Church</strong> Annual Report System
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="text-align: right; padding-top: 1rem; color: var(--text-secondary);">
            <div style="font-size: 0.875rem;">Logged in as</div>
            <div style="font-weight: 500; color: var(--text-primary);">{st.session_state.username}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        if st.button("Logout", type="secondary"):
            logout()
    
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
    
    # Sidebar with report management
    with st.sidebar:
        # User info
        st.markdown(f"""
        <div style="padding: 1.5rem 0; border-bottom: 1px solid var(--border-color);">
            <div style="font-size: 1rem; font-weight: 500; color: var(--text-primary);">
                {st.session_state.user_full_name or st.session_state.username}
            </div>
            <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.25rem;">
                {st.session_state.user_church_name or 'No church specified'}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Report Management
        st.markdown('<div style="font-size: 0.875rem; color: var(--text-secondary); margin: 1.5rem 0 0.75rem 0;">REPORT MANAGEMENT</div>', unsafe_allow_html=True)
        
        # New Report
        if st.button("📝 New Report", use_container_width=True):
            st.session_state.current_report_id = None
            st.session_state.current_report_name = None
            initialize_dataframes()
            for key in ['church_name', 'district', 'annual_conference', 'pastor_name', 'council_chairperson']:
                if key in st.session_state:
                    del st.session_state[key]
            st.success("Started new report")
            st.rerun()
        
        # Save Report
        if st.button("💾 Save Report", use_container_width=True):
            if save_current_report():
                st.success("Report saved successfully!")
        
        # Load Templates
        st.markdown('<div style="font-size: 0.875rem; color: var(--text-secondary); margin: 1.5rem 0 0.75rem 0;">TEMPLATES</div>', unsafe_allow_html=True)
        
        templates = get_templates()
        template_names = ["Select Template"] + [f"{t['name']}" for t in templates]
        selected_template = st.selectbox("", template_names, label_visibility="collapsed")
        
        if selected_template != "Select Template":
            template_id = [t['id'] for t in templates if f"{t['name']}" == selected_template][0]
            template_data = load_template(template_id)
            
            if template_data:
                for key in ['strategic_df', 'lay_df', 'trustee_df', 'leadership_df', 'appendix_df']:
                    if key in template_data:
                        st.session_state[key] = template_data[key]
                st.success("Template loaded successfully!")
                st.rerun()
        
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        
        # My Reports
        st.markdown('<div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.75rem;">MY REPORTS</div>', unsafe_allow_html=True)
        
        user_reports = get_user_reports(st.session_state.user_id)
        
        if user_reports:
            report_options = ["Select Report"] + [f"{r['report_name']} ({r['completion_percentage']:.0f}%)" for r in user_reports]
            selected_report = st.selectbox("", report_options, label_visibility="collapsed", key="report_select")
            
            if selected_report != "Select Report":
                report_index = report_options.index(selected_report) - 1
                selected_report_id = user_reports[report_index]['id']
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📂 Load", use_container_width=True):
                        load_selected_report(selected_report_id)
                with col2:
                    if st.button("🗑️ Delete", use_container_width=True):
                        if delete_report(selected_report_id, st.session_state.user_id):
                            st.success("Report deleted successfully!")
                            st.rerun()
        else:
            st.markdown('<div style="color: var(--text-tertiary); font-size: 0.875rem; text-align: center; padding: 1rem;">No saved reports</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        
        # Current Report Info
        current_report_name = st.session_state.get('current_report_name', 'Unsaved Report')
        st.markdown(f"""
        <div style="padding: 1rem; background-color: var(--bg-tertiary); border-radius: var(--radius-sm);">
            <div style="font-size: 0.875rem; color: var(--text-secondary);">Current Report</div>
            <div style="font-size: 1rem; color: var(--text-primary); font-weight: 500; margin-top: 0.25rem; overflow: hidden; text-overflow: ellipsis;">
                {current_report_name}
            </div>
            <div style="font-size: 0.75rem; color: var(--text-tertiary); margin-top: 0.25rem;">
                {completion_percentage:.1f}% complete
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        
        # Navigation
        st.markdown('<div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.75rem;">NAVIGATION</div>', unsafe_allow_html=True)
        
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
            format_func=lambda x: f"{[icon for icon, name, _ in section_options if name == x][0]} {x}",
            key="nav_select"
        )
        
        # Get selected key
        selected_key = [key for _, name, key in section_options if name == selected_section][0]
        
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        
        # Export Section
        st.markdown('<div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.75rem;">EXPORT</div>', unsafe_allow_html=True)
        
        if st.button("Generate Report", use_container_width=True, type="primary"):
            st.session_state.show_preview = True
        
        b64, filename, report_content, completion_percentage = create_downloadable_report()
        href = f'<a href="data:file/txt;base64,{b64}" download="{filename}" class="primary-button" style="display: block; text-align: center; margin-top: 0.75rem;">Download Report</a>'
        st.markdown(href, unsafe_allow_html=True)
        
        # Theme Indicator
        st.markdown('<div class="theme-indicator">Theme: System • Database Active</div>', unsafe_allow_html=True)
    
    # Main content based on selected section
    if selected_section == "Church Information":
        st.markdown('<div class="section-header">Church Information</div>', unsafe_allow_html=True)
        
        # Auto-save on change
        def check_church_info_completion():
            required_fields = ['church_name', 'district', 'annual_conference', 'pastor_name', 'council_chairperson']
            is_complete = all(st.session_state.get(field, '') != '' for field in required_fields)
            update_completion_status('church_info', is_complete)
            # Auto-save
            if st.session_state.authenticated and any(st.session_state.get(field, '') for field in required_fields):
                save_current_report()
        
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
                key="strategic_editor",
                on_change=lambda: save_current_report() if st.session_state.authenticated else None
            )
            st.session_state.strategic_df = edited_strategic
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Meetings Information
        col1, col2 = st.columns(2)
        with col1:
            with st.container():
                st.markdown('<div class="input-card">', unsafe_allow_html=True)
                st.markdown('<div class="subsection-header">Meetings</div>', unsafe_allow_html=True)
                num_regular_meetings = st.number_input("Regular Meetings", min_value=0, value=12, key="num_meetings", 
                                                      on_change=lambda: save_current_report() if st.session_state.authenticated else None)
                num_special_meetings = st.number_input("Special Meetings", min_value=0, value=0, key="num_special",
                                                      on_change=lambda: save_current_report() if st.session_state.authenticated else None)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            with st.container():
                st.markdown('<div class="input-card">', unsafe_allow_html=True)
                st.markdown('<div class="subsection-header">Attendance</div>', unsafe_allow_html=True)
                average_attendance = st.number_input("Average Attendance (%)", min_value=0, max_value=100, value=85, key="avg_attendance",
                                                    on_change=lambda: save_current_report() if st.session_state.authenticated else None)
                quorum_achieved = st.selectbox("Quorum Achieved", ["Always", "Mostly", "Sometimes", "Rarely"], key="quorum",
                                              on_change=lambda: save_current_report() if st.session_state.authenticated else None)
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Key Decisions
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown('<div class="subsection-header">Key Decisions</div>', unsafe_allow_html=True)
            key_decisions = st.text_area("", height=150, key="key_decisions", placeholder="Enter key decisions and resolutions...",
                                       on_change=lambda: save_current_report() if st.session_state.authenticated else None)
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
                key="lay_editor",
                on_change=lambda: save_current_report() if st.session_state.authenticated else None
            )
            st.session_state.lay_df = edited_lay
            st.markdown('</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown('<div class="subsection-header">Programs Summary</div>', unsafe_allow_html=True)
            programs_summary = st.text_area("", height=150, key="programs_summary", placeholder="Summarize programs and activities...",
                                          on_change=lambda: save_current_report() if st.session_state.authenticated else None)
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
                key="trustee_editor",
                on_change=lambda: save_current_report() if st.session_state.authenticated else None
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
                nursery_enrolled = st.number_input("Enrolled", min_value=0, key="nursery_enrolled", 
                                                  on_change=lambda: save_current_report() if st.session_state.authenticated else None)
                nursery_current = st.number_input("Current", min_value=0, key="nursery_current",
                                                 on_change=lambda: save_current_report() if st.session_state.authenticated else None)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            with st.container():
                st.markdown('<div class="input-card">', unsafe_allow_html=True)
                st.markdown('<div class="subsection-header">Kindergarten</div>', unsafe_allow_html=True)
                kinder_enrolled = st.number_input("Enrolled", min_value=0, key="kinder_enrolled",
                                                 on_change=lambda: save_current_report() if st.session_state.authenticated else None)
                kinder_current = st.number_input("Current", min_value=0, key="kinder_current",
                                                on_change=lambda: save_current_report() if st.session_state.authenticated else None)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            with st.container():
                st.markdown('<div class="input-card">', unsafe_allow_html=True)
                st.markdown('<div class="subsection-header">Administrative</div>', unsafe_allow_html=True)
                status = st.selectbox("Status", ["Registered", "Recognized", "Permit to Operate", "Pending"], key="school_status",
                                    on_change=lambda: save_current_report() if st.session_state.authenticated else None)
                has_scholarships = st.radio("Scholarships", ["Yes", "No"], key="scholarships", horizontal=True,
                                          on_change=lambda: save_current_report() if st.session_state.authenticated else None)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown('<div class="subsection-header">School Programs</div>', unsafe_allow_html=True)
            school_programs = st.text_area("", height=100, key="school_programs", placeholder="List programs and activities...",
                                         on_change=lambda: save_current_report() if st.session_state.authenticated else None)
            st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            with st.container():
                st.markdown('<div class="input-card">', unsafe_allow_html=True)
                st.markdown('<div class="subsection-header">Registration Fee</div>', unsafe_allow_html=True)
                reg_fee = st.number_input("Amount (₱)", min_value=0.0, key="reg_fee", label_visibility="collapsed",
                                        on_change=lambda: save_current_report() if st.session_state.authenticated else None)
                st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            with st.container():
                st.markdown('<div class="input-card">', unsafe_allow_html=True)
                st.markdown('<div class="subsection-header">Miscellaneous</div>', unsafe_allow_html=True)
                misc_fee = st.number_input("Amount (₱)", min_value=0.0, key="misc_fee", label_visibility="collapsed",
                                         on_change=lambda: save_current_report() if st.session_state.authenticated else None)
                st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            with st.container():
                st.markdown('<div class="input-card">', unsafe_allow_html=True)
                st.markdown('<div class="subsection-header">Tuition Fee</div>', unsafe_allow_html=True)
                tuition_fee = st.number_input("Monthly (₱)", min_value=0.0, key="tuition_fee", label_visibility="collapsed",
                                            on_change=lambda: save_current_report() if st.session_state.authenticated else None)
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
        
        if 'grade_df' in st.session_state:
            grade_df = st.session_state.grade_df
        
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            edited_grade = st.data_editor(grade_df, num_rows="dynamic", use_container_width=True, key="grade_editor",
                                        on_change=lambda: save_current_report() if st.session_state.authenticated else None)
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
                church_membership = st.number_input("Total Membership", min_value=0, key="membership",
                                                  on_change=lambda: save_current_report() if st.session_state.authenticated else None)
                pastor_support = st.number_input("Monthly Support (₱)", min_value=0.0, key="pastor_support",
                                               on_change=lambda: save_current_report() if st.session_state.authenticated else None)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            with st.container():
                st.markdown('<div class="input-card">', unsafe_allow_html=True)
                st.markdown('<div class="subsection-header">Deaconess</div>', unsafe_allow_html=True)
                deaconess_work = st.text_area("Nature of Work", height=100, key="deaconess_work",
                                            on_change=lambda: save_current_report() if st.session_state.authenticated else None)
                deaconess_support = st.number_input("Monthly Support (₱)", min_value=0.0, key="deaconess_support",
                                                  on_change=lambda: save_current_report() if st.session_state.authenticated else None)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown('<div class="subsection-header">Relationships & Situation</div>', unsafe_allow_html=True)
            workers_relationship = st.text_area("Worker Relationships", height=100, key="workers_relationship",
                                              on_change=lambda: save_current_report() if st.session_state.authenticated else None)
            housing_situation = st.selectbox("Housing Situation", ["Provided by Church", "Rented", "Own House", "Other"], key="housing",
                                           on_change=lambda: save_current_report() if st.session_state.authenticated else None)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown('<div class="subsection-header">Recommendations</div>', unsafe_allow_html=True)
            ministry_entrants = st.text_area("Ministry Entrants", height=100, key="ministry_entrants",
                                           on_change=lambda: save_current_report() if st.session_state.authenticated else None)
            worker_benefits = st.text_area("Support Recommendations", height=100, key="worker_benefits",
                                         on_change=lambda: save_current_report() if st.session_state.authenticated else None)
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
                key="leadership_editor",
                on_change=lambda: save_current_report() if st.session_state.authenticated else None
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
        
        if 'committee_df' in st.session_state:
            committee_df = st.session_state.committee_df
        
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown('<div class="subsection-header">Committees</div>', unsafe_allow_html=True)
            edited_committee = st.data_editor(committee_df, num_rows="dynamic", use_container_width=True, key="committee_editor",
                                            on_change=lambda: save_current_report() if st.session_state.authenticated else None)
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
                key="appendix_editor",
                on_change=lambda: save_current_report() if st.session_state.authenticated else None
            )
            st.session_state.appendix_df = edited_appendix
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="subsection-header">Membership Statistics</div>', unsafe_allow_html=True)
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            professing = st.number_input("Professing", min_value=0, key="professing", label_visibility="collapsed",
                                       on_change=lambda: save_current_report() if st.session_state.authenticated else None)
            st.markdown('<div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Professing</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            baptized = st.number_input("Baptized", min_value=0, key="baptized", label_visibility="collapsed",
                                     on_change=lambda: save_current_report() if st.session_state.authenticated else None)
            st.markdown('<div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Baptized</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            affiliate = st.number_input("Affiliate", min_value=0, key="affiliate", label_visibility="collapsed",
                                      on_change=lambda: save_current_report() if st.session_state.authenticated else None)
            st.markdown('<div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Affiliate</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            associate = st.number_input("Associate", min_value=0, key="associate", label_visibility="collapsed",
                                      on_change=lambda: save_current_report() if st.session_state.authenticated else None)
            st.markdown('<div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Associate</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col5:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            constituency = st.number_input("Constituency", min_value=0, key="constituency", label_visibility="collapsed",
                                         on_change=lambda: save_current_report() if st.session_state.authenticated else None)
            st.markdown('<div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Constituency</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            with st.container():
                st.markdown('<div class="input-card">', unsafe_allow_html=True)
                st.markdown('<div class="subsection-header">Audit</div>', unsafe_allow_html=True)
                audit_completed = st.radio("Audit Completed", ["Yes", "No"], key="audit", horizontal=True,
                                         on_change=lambda: save_current_report() if st.session_state.authenticated else None)
                audit_date = st.date_input("Completion Date", key="audit_date",
                                         on_change=lambda: save_current_report() if st.session_state.authenticated else None)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            with st.container():
                st.markdown('<div class="input-card">', unsafe_allow_html=True)
                st.markdown('<div class="subsection-header">Auditor</div>', unsafe_allow_html=True)
                auditor_name = st.text_input("Auditor Name", key="auditor_name",
                                           on_change=lambda: save_current_report() if st.session_state.authenticated else None)
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="subsection-header">Signatures</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="signature-area">', unsafe_allow_html=True)
            st.markdown('<div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Council Chairperson</div>', unsafe_allow_html=True)
            council_signature = st.text_input("", key="council_signature", label_visibility="collapsed", placeholder="Name",
                                            on_change=lambda: save_current_report() if st.session_state.authenticated else None)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="signature-area">', unsafe_allow_html=True)
            st.markdown('<div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Pastor</div>', unsafe_allow_html=True)
            pastor_signature = st.text_input("", key="pastor_signature", label_visibility="collapsed", placeholder="Name",
                                           on_change=lambda: save_current_report() if st.session_state.authenticated else None)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="signature-area">', unsafe_allow_html=True)
            st.markdown('<div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Secretary</div>', unsafe_allow_html=True)
            secretary_signature = st.text_input("", key="secretary_signature", label_visibility="collapsed", placeholder="Name",
                                              on_change=lambda: save_current_report() if st.session_state.authenticated else None)
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
    
    # Database status indicator
    st.markdown(f"""
    <div class="footer">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem;">
            <div>
                <div style="font-weight: 500; color: var(--text-primary); margin-bottom: 0.5rem;">Database Status</div>
                <div style="font-size: 0.875rem; color: var(--text-secondary); line-height: 1.5;">
                    • Connected to SQLite<br>
                    • User: {st.session_state.username}<br>
                    • Auto-save: Active
                </div>
            </div>
            <div>
                <div style="font-weight: 500; color: var(--text-primary); margin-bottom: 0.5rem;">Current Report</div>
                <div style="font-size: 0.875rem; color: var(--text-secondary); line-height: 1.5;">
                    • Name: {st.session_state.get('current_report_name', 'Unsaved')}<br>
                    • Completion: {completion_percentage:.1f}%<br>
                    • Last save: {datetime.now().strftime('%H:%M')}
                </div>
            </div>
            <div>
                <div style="font-weight: 500; color: var(--text-primary); margin-bottom: 0.5rem;">System</div>
                <div style="font-size: 0.875rem; color: var(--text-secondary); line-height: 1.5;">
                    Church Annual Report System<br>
                    Version 3.0 • {datetime.now().year}<br>
                    Database Active • Theme: System
                </div>
            </div>
        </div>
        <div class="custom-divider" style="margin: 1.5rem 0;"></div>
        <div style="text-align: center; color: var(--text-tertiary); font-size: 0.75rem;">
            SQLite Database • User Authentication • Auto-save • Report Management
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Completion reminder
    if completion_percentage < 100:
        st.markdown(f"""
        <div class="info-box">
            <strong>Note:</strong> Report is {completion_percentage:.1f}% complete. 
            Changes are auto-saved to the database.
        </div>
        """, unsafe_allow_html=True)
