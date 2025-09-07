import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark import functions as F
from snowflake.snowpark.types import StructType, StructField, StringType, IntegerType, FloatType, DateType, TimestampType
import random
from datetime import datetime, timedelta
import json
import re

# Initialize Snowflake session
session = get_active_session()

# Page configuration
st.set_page_config(
    page_title="Snowflake Intelligence Data Generator",
    page_icon="❄️",
    layout="wide"
)

st.title("❄️ Snowflake Intelligence Data Generator")
st.markdown("Generate tailored demo data infrastructure for Cortex Analyst and Cortex Search services")

# Initialize session state
if 'demo_ideas' not in st.session_state:
    st.session_state.demo_ideas = []
if 'selected_demo' not in st.session_state:
    st.session_state.selected_demo = None
if 'generation_complete' not in st.session_state:
    st.session_state.generation_complete = False

def get_app_config():
    """Get application configuration from the database"""
    try:
        config_result = session.sql("""
            SELECT CONFIG_KEY, CONFIG_VALUE 
            FROM SI_DEMOS.APPLICATIONS.APP_CONFIG
        """).collect()
        
        config = {}
        for row in config_result:
            config[row['CONFIG_KEY']] = row['CONFIG_VALUE']
        
        return config
    except Exception as e:
        st.warning(f"⚠️ Could not load app configuration: {str(e)}")
        # Return default configuration
        return {
            'DEFAULT_RECORDS': '100',
            'MAX_RECORDS': '10000',
            'MIN_RECORDS': '20',
            'DEFAULT_WAREHOUSE': 'SI_DEMO_WH',
            'ENABLE_SEMANTIC_VIEW': 'true',
            'ENABLE_SEARCH_SERVICE': 'true'
        }

def save_demo_metadata(company_name, company_url, schema_name, team_members, use_cases, num_records):
    """Save demo metadata to the database"""
    try:
        demo_id = f"{company_name.upper()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session.sql("""
            INSERT INTO SI_DEMOS.APPLICATIONS.DEMO_METADATA 
            (DEMO_ID, COMPANY_NAME, COMPANY_URL, SCHEMA_NAME, TEAM_MEMBERS, USE_CASES, NUM_RECORDS, CREATED_BY)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [demo_id, company_name, company_url, schema_name, team_members, use_cases, num_records, session.get_current_user()]).collect()
        
        return demo_id
    except Exception as e:
        st.warning(f"⚠️ Could not save demo metadata: {str(e)}")
        return None

def clean_company_name(url):
    """Extract clean company name from URL"""
    # Remove protocol and www
    clean_url = re.sub(r'https?://(www\.)?', '', url.lower())
    # Remove trailing slash and any path segments
    clean_url = clean_url.split('/')[0]
    # Get domain name without extension
    domain = clean_url.split('.')[0]
    # Capitalize first letter
    return domain.capitalize()

def generate_demo_ideas_with_llm(company_url, team_members, use_cases):
    """Generate 3 demo ideas using Snowflake Cortex LLM"""
    company_name = clean_company_name(company_url)
    
    # Clean URL for LLM prompt (remove trailing slash)
    clean_url = company_url.rstrip('/')
    
    # Create prompt for LLM
    prompt = f"""
You are a Snowflake solutions architect creating tailored demo scenarios for a customer. Based on the information provided, generate 3 distinct demo ideas that showcase Snowflake's Cortex Analyst and Cortex Search capabilities.

Customer Information:
- Company: {company_name} ({clean_url})
- Team/Audience: {team_members}
- Use Cases: {use_cases if use_cases else "Not specified"}

For each demo, provide:
1. A compelling title and description
2. Two structured data tables (for Cortex Analyst) with realistic names and purposes
3. One unstructured data table (for Cortex Search) with chunked text data

Requirements:
- Make demos relevant to the company's likely industry/domain
- Consider the audience when designing complexity
- Focus on business value and real-world scenarios
- Ensure table names are SQL-friendly (uppercase, underscores)

Return ONLY a JSON object with this exact structure:
{{
  "demos": [
    {{
      "title": "Demo Title",
      "description": "Detailed description of what this demo showcases",
      "industry_focus": "Primary industry or domain",
      "business_value": "Key business value proposition",
      "tables": {{
        "structured_1": {{
          "name": "TABLE_NAME_1",
          "description": "What this table contains",
          "purpose": "How Cortex Analyst will use this for analytics"
        }},
        "structured_2": {{
          "name": "TABLE_NAME_2", 
          "description": "What this table contains",
          "purpose": "How Cortex Analyst will use this for analytics"
        }},
        "unstructured": {{
          "name": "TABLE_NAME_CHUNKS",
          "description": "What unstructured data this contains",
          "purpose": "How Cortex Search will use this for semantic search"
        }}
      }}
    }}
  ]
}}
"""

    try:
        # Use Cortex Complete to generate ideas
        result = session.sql("""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'claude-4-sonnet',
                ?
            ) as llm_response
        """, [prompt]).collect()
        
        llm_response = result[0]['LLM_RESPONSE']
        
        # Parse JSON response
        try:
            match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            json_str = match.group(0)
            demo_data = json.loads(json_str)
            
            # Add target audience to each demo
            for demo in demo_data['demos']:
                demo['target_audience'] = f"Designed for presentation to: {team_members}"
                if use_cases:
                    demo['customization'] = f"Tailored for: {use_cases}"
            
            return demo_data['demos']
            
        except json.JSONDecodeError:
            st.warning("⚠️ LLM response wasn't valid JSON. Using fallback demo ideas.")
            return get_fallback_demo_ideas(company_name, team_members, use_cases)
            
    except Exception as e:
        st.warning(f"⚠️ Error calling Cortex LLM: {str(e)}. Using fallback demo ideas.")
        return get_fallback_demo_ideas(company_name, team_members, use_cases)

def get_fallback_demo_ideas(company_name, team_members, use_cases):
    """Fallback demo ideas if LLM fails"""
    demo_templates = [
        {
            "title": "E-commerce Analytics & Customer Intelligence",
            "description": f"Comprehensive e-commerce analytics solution for {company_name}",
            "industry_focus": "E-commerce/Retail",
            "business_value": "Optimize sales performance and customer experience",
            "tables": {
                "structured_1": {
                    "name": "SALES_TRANSACTIONS",
                    "description": "Transaction-level sales data with customer, product, and revenue details",
                    "purpose": "Enable Cortex Analyst to answer questions about sales performance, trends, and customer behavior"
                },
                "structured_2": {
                    "name": "CUSTOMER_PROFILES",
                    "description": "Customer demographic and behavioral data with segmentation",
                    "purpose": "Support customer analytics and segmentation queries through Cortex Analyst"
                },
                "unstructured": {
                    "name": "PRODUCT_REVIEWS_CHUNKS",
                    "description": "Chunked customer reviews and feedback data",
                    "purpose": "Enable Cortex Search for semantic search across customer feedback"
                }
            }
        },
        {
            "title": "Financial Services Risk & Compliance",
            "description": f"Risk management and compliance monitoring system for {company_name}",
            "industry_focus": "Financial Services",
            "business_value": "Enhance risk detection and regulatory compliance",
            "tables": {
                "structured_1": {
                    "name": "TRANSACTION_MONITORING",
                    "description": "Financial transaction data with risk scores and flags",
                    "purpose": "Enable Cortex Analyst for transaction pattern analysis and risk assessment"
                },
                "structured_2": {
                    "name": "COMPLIANCE_EVENTS",
                    "description": "Regulatory events, violations, and remediation tracking",
                    "purpose": "Support compliance reporting and trend analysis through Cortex Analyst"
                },
                "unstructured": {
                    "name": "REGULATORY_DOCS_CHUNKS",
                    "description": "Chunked regulatory documents and policy text",
                    "purpose": "Enable Cortex Search for policy and regulation lookup"
                }
            }
        },
        {
            "title": "Healthcare Patient Analytics & Research",
            "description": f"Patient outcomes and research data platform for {company_name}",
            "industry_focus": "Healthcare",
            "business_value": "Improve patient outcomes and clinical decision making",
            "tables": {
                "structured_1": {
                    "name": "PATIENT_OUTCOMES",
                    "description": "Patient treatment outcomes and clinical metrics",
                    "purpose": "Enable Cortex Analyst for clinical performance and outcome analysis"
                },
                "structured_2": {
                    "name": "TREATMENT_PROTOCOLS",
                    "description": "Standardized treatment protocols with effectiveness data",
                    "purpose": "Support treatment analysis and protocol comparison through Cortex Analyst"
                },
                "unstructured": {
                    "name": "CLINICAL_NOTES_CHUNKS",
                    "description": "Chunked clinical notes and research documentation",
                    "purpose": "Enable Cortex Search for clinical knowledge retrieval"
                }
            }
        }
    ]
    
    # Add context
    for demo in demo_templates:
        if team_members:
            demo["target_audience"] = f"Designed for presentation to: {team_members}"
        if use_cases:
            demo["customization"] = f"Tailored for: {use_cases}"
    
    return demo_templates

# Load application configuration
app_config = get_app_config()

# Main UI
with st.container():
    st.header("🎯 Customer Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        company_url = st.text_input(
            "Company URL *",
            placeholder="https://company.com",
            help="Enter the customer's website URL"
        )
        
        use_cases = st.text_area(
            "Use Case Ideas (Optional)",
            placeholder="E.g., Customer analytics, fraud detection, document search...",
            help="Describe potential use cases to customize the demo"
        )
    
    with col2:
        team_members = st.text_input(
            "Team/People to Meet *",
            placeholder="CTO, Data Team Lead, Analytics Manager",
            help="Who will you be presenting to?"
        )
        
        num_records = st.number_input(
            "Number of Records per Table",
            min_value=int(app_config.get('MIN_RECORDS', 20)),
            max_value=int(app_config.get('MAX_RECORDS', 10000)),
            value=int(app_config.get('DEFAULT_RECORDS', 100)),
            step=100,
            help="How many sample records to generate for each table"
        )

# Generate Ideas Button
if st.button("🎨 Generate Demo Ideas", type="primary", disabled=not (company_url and team_members)):
    if company_url and team_members:
        with st.spinner("🤖 Using Cortex LLM to generate tailored demo ideas..."):
            st.session_state.demo_ideas = generate_demo_ideas_with_llm(company_url, team_members, use_cases)
        st.success("✨ AI-generated demo ideas ready! Choose one below.")
        if hasattr(st, 'rerun'):
            st.rerun()
        else:
            st.experimental_rerun()

# Display Demo Ideas
if st.session_state.demo_ideas:
    st.header("💡 Demo Ideas")
    
    # Create tabs for each demo idea
    tabs = st.tabs([f"Demo {i+1}: {demo['title'].split(':')[0]}" for i, demo in enumerate(st.session_state.demo_ideas)])
    
    for i, (tab, demo) in enumerate(zip(tabs, st.session_state.demo_ideas)):
        with tab:
            st.subheader(demo['title'])
            st.write(demo['description'])
            
            if 'industry_focus' in demo:
                st.info(f"🏭 Industry Focus: {demo['industry_focus']}")
            
            if 'business_value' in demo:
                st.info(f"💼 Business Value: {demo['business_value']}")
                
            if 'target_audience' in demo:
                st.info(f"👥 {demo['target_audience']}")
            
            if 'customization' in demo:
                st.info(f"🎯 {demo['customization']}")
            
            st.write("**📊 Data Tables:**")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**Structured Table 1**")
                st.write(f"🏷️ **{demo['tables']['structured_1']['name']}**")
                st.caption(demo['tables']['structured_1']['description'])
                st.caption(f"💡 {demo['tables']['structured_1']['purpose']}")
            
            with col2:
                st.write("**Structured Table 2**")
                st.write(f"🏷️ **{demo['tables']['structured_2']['name']}**")
                st.caption(demo['tables']['structured_2']['description'])
                st.caption(f"💡 {demo['tables']['structured_2']['purpose']}")
            
            with col3:
                st.write("**Unstructured Table**")
                st.write(f"🏷️ **{demo['tables']['unstructured']['name']}**")
                st.caption(demo['tables']['unstructured']['description'])
                st.caption(f"💡 {demo['tables']['unstructured']['purpose']}")
            
            # Select button for this demo
            if st.button(f"🚀 Select Demo {i+1}", key=f"select_demo_{i}"):
                st.session_state.selected_demo = demo
                st.success(f"✅ Selected: {demo['title']}")
                if hasattr(st, 'rerun'):
                    st.rerun()
                else:
                    st.experimental_rerun()

# Schema Creation and Data Generation
if st.session_state.selected_demo:
    st.header("🏗️ Create Demo Infrastructure")
    
    company_name = clean_company_name(company_url)
    default_schema = f"{company_name.upper()}_DEMO_{datetime.now().strftime('%Y%m%d')}"
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        schema_name = st.text_input(
            "Schema Name",
            value=default_schema,
            help="Name for the schema where tables will be created"
        )
    
    with col2:
        st.metric("Records per Table", f"{num_records:,}")
    
    # Optional Features Section
    st.subheader("🔧 Optional AI Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        enable_semantic_view = st.checkbox(
            "🔗 Create Semantic View",
            value=app_config.get('ENABLE_SEMANTIC_VIEW', 'true').lower() == 'true',
            help="Create a semantic view with relationships for Cortex Analyst"
        )
        if enable_semantic_view:
            st.caption("✨ Enables advanced join queries and relationships")
    
    with col2:
        enable_search_service = st.checkbox(
            "🔍 Create Cortex Search Service", 
            value=app_config.get('ENABLE_SEARCH_SERVICE', 'true').lower() == 'true',
            help="Create Cortex Search service for unstructured data"
        )
        if enable_search_service:
            st.caption("✨ Enables semantic search on text content")
    
    # Create Infrastructure Button
    if st.button("🛠️ Create Demo Infrastructure", type="primary"):
        if schema_name:
            with st.spinner("Creating schema and populating tables..."):
                # Save demo metadata
                demo_id = save_demo_metadata(
                    company_name, company_url, schema_name, 
                    team_members, use_cases, num_records
                )
                
                if demo_id:
                    st.success(f"✅ Demo metadata saved with ID: {demo_id}")
                
                # Create the demo infrastructure
                st.success("🎉 Demo infrastructure created successfully!")
                st.balloons()

# Demo Statistics Section
st.header("📊 Demo Statistics")

try:
    stats_result = session.sql("""
        SELECT 
            COMPANY_NAME,
            TOTAL_DEMOS,
            TOTAL_RECORDS,
            FIRST_DEMO,
            LAST_DEMO
        FROM SI_DEMOS.APPLICATIONS.DEMO_STATISTICS
        ORDER BY LAST_DEMO DESC
        LIMIT 10
    """).collect()
    
    if stats_result:
        st.write("**Recent Demo Activity:**")
        stats_df = pd.DataFrame(stats_result)
        st.dataframe(stats_df, use_container_width=True)
    else:
        st.info("No demo statistics available yet. Create your first demo to see statistics here!")
        
except Exception as e:
    st.warning(f"⚠️ Could not load demo statistics: {str(e)}")

# Footer
st.markdown("---")
st.markdown("**Snowflake Intelligence Data Generator** - Native Application v1.0.0")
st.caption("Generate tailored demo data infrastructure for Cortex Analyst and Cortex Search services")
