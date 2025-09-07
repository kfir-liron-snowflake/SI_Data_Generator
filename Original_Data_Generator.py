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
    page_title="Snowflake Agent Demo Data Generator",
    page_icon="❄️",
    layout="wide"
)

st.title("❄️ Snowflake Agent Demo Data Generator")
st.markdown("Generate tailored demo data infrastructure for Cortex Analyst and Cortex Search services")

# Initialize session state
if 'demo_ideas' not in st.session_state:
    st.session_state.demo_ideas = []
if 'selected_demo' not in st.session_state:
    st.session_state.selected_demo = None
if 'generation_complete' not in st.session_state:
    st.session_state.generation_complete = False

def clean_company_name(url):
    """Extract clean company name from URL"""
    # Remove protocol and www
    clean_url = re.sub(r'https?://(www\.)?', '', url.lower())
    # Get domain name without extension
    domain = clean_url.split('.')[0]
    # Capitalize first letter
    return domain.capitalize()

def generate_demo_ideas_with_llm(company_url, team_members, use_cases):
    """Generate 3 demo ideas using Snowflake Cortex LLM"""
    company_name = clean_company_name(company_url)
    
    # Create prompt for LLM
    prompt = f"""
You are a Snowflake solutions architect creating tailored demo scenarios for a customer. Based on the information provided, generate 3 distinct demo ideas that showcase Snowflake's Cortex Analyst and Cortex Search capabilities.

Customer Information:
- Company: {company_name} ({company_url})
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

def generate_realistic_content_with_llm(table_info, num_records, company_name, is_structured_table=True, join_key_values=None):
    """Generate realistic table schema and content using LLM"""
    #st.write('generate_realistic_content - start')
    
    # Add join key instruction for structured tables
    join_key_instruction = ""
    if is_structured_table and join_key_values is not None:
        join_key_instruction = f"""
IMPORTANT: This is a structured table that needs to be joinable with other tables. 
- Include an 'ENTITY_ID' column as the first column with type 'NUMBER'
- This will be the primary key for joining with other tables
- Make it the first column in your schema
"""
    
    # Create schema generation prompt
    schema_prompt = f"""
You are a data architect creating realistic table schemas and sample data for a Snowflake demo.

Table Information:
- Name: {table_info['name']}
- Description: {table_info['description']}
- Purpose: {table_info['purpose']}
- Company: {company_name}

{join_key_instruction}

Generate a realistic table schema with 6-10 columns that would be appropriate for this table. Consider:
- Primary keys and foreign keys
- Appropriate data types (STRING, NUMBER, FLOAT, DATE, TIMESTAMP, BOOLEAN)
- Business-relevant column names
- Realistic constraints and relationships

Return ONLY a JSON object with this structure with no additional text before and after so I can create automation based on it:
{{
  "columns": [
    {{
      "name": "COLUMN_NAME",
      "type": "DATA_TYPE", 
      "description": "What this column represents",
      "sample_values": ["example1", "example2", "example3"]
    }}
  ]
}}
"""

    try:
        #st.write(schema_prompt)
        # Get schema from LLM
        schema_result = session.sql("""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'claude-4-sonnet',
                ?
            ) as llm_response
        """, [schema_prompt]).collect()
        
        schema_response = schema_result[0]['LLM_RESPONSE']
        
        try:
            # First clean up the response string
            match = re.search(r'\{.*\}', schema_response, re.DOTALL)
            json_str = match.group(0)
            schema_data = json.loads(json_str)
            return generate_data_from_schema(schema_data, num_records, table_info, company_name, join_key_values)
        
        except json.JSONDecodeError:
            st.warning(f"⚠️ Could not parse schema for {table_info['name']}, using fallback")
            return generate_fallback_data(table_info['name'], num_records, company_name, join_key_values)
            
    except Exception as e:
        st.warning(f"⚠️ Error generating schema for {table_info['name']}: {str(e)}")
        return generate_fallback_data(table_info['name'], num_records, company_name, join_key_values)

def generate_unstructured_content_with_llm(table_info, num_records, company_name):
    """Generate realistic unstructured text chunks using LLM"""
    capped_num_records = min(num_records, 200)

    # Create content generation prompt
    content_prompt = f"""
You are creating realistic unstructured text content for a Snowflake Cortex Search demo.

Table Information:
- Name: {table_info['name']}
- Description: {table_info['description']}
- Purpose: {table_info['purpose']}
- Company: {company_name}

Generate {capped_num_records} different realistic text samples that would be found in this type of data. Each should be 2-4 sentences long and relevant to the business context.

Examples should be:
- Realistic business content
- Varied in tone and style
- Relevant to the table's purpose
- Appropriate for semantic search
- Professional but natural

Return ONLY a JSON array of text strings:
["text sample 1", "text sample 2", ...]
"""

    try:
        # Get content from LLM
        content_result = session.sql("""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'claude-4-sonnet',
                ?
            ) as llm_response
        """, [content_prompt]).collect()
        
        content_response = content_result[0]['LLM_RESPONSE']
        try:
            import json
            match = re.search(r'\[.*\]', content_response, re.DOTALL)
            json_str = match.group(0)
            text_samples = json.loads(json_str)
            return generate_chunked_data_from_samples(text_samples, num_records, table_info, company_name)
        
        except json.JSONDecodeError:
            st.warning(f"⚠️ Could not parse content for {table_info['name']}, using fallback")
            return generate_fallback_unstructured_data(table_info['name'], num_records, company_name)
            
    except Exception as e:
        st.warning(f"⚠️ Error generating content for {table_info['name']}: {str(e)}")
        return generate_fallback_unstructured_data(table_info['name'], num_records, company_name)

def generate_data_from_schema(schema_data, num_records, table_info, company_name, join_key_values=None):
    """Generate realistic data based on LLM-provided schema"""
    data = []
    #st.write("generate_data_from_schema - start")
    
    for i in range(num_records):
        record = {}
        
        for col in schema_data['columns']:
            col_name = col['name']
            col_type = col['type'].upper()
            sample_values = col.get('sample_values', [])
            
            # Handle ENTITY_ID specially if join key values are provided
            if col_name == 'ENTITY_ID' and join_key_values is not None:
                # Use sequential assignment to ensure uniqueness within the table
                record[col_name] = join_key_values[i]
                continue
            
            # Generate values based on type and samples
            if col_type in ['STRING', 'VARCHAR', 'TEXT']:
                if sample_values:
                    record[col_name] = random.choice(sample_values)
                else:
                    record[col_name] = f"Sample_{i+1}"
                    
            elif col_type in ['NUMBER', 'INTEGER', 'INT']:
                if 'ID' in col_name.upper() and col_name != 'ENTITY_ID':
                    record[col_name] = i + 1
                elif sample_values:
                    record[col_name] = random.choice([int(x) for x in sample_values if str(x).isdigit()])
                else:
                    record[col_name] = random.randint(1, 1000)
                    
            elif col_type in ['FLOAT', 'DECIMAL', 'DOUBLE']:
                if sample_values:
                    record[col_name] = float(random.choice(sample_values))
                else:
                    record[col_name] = round(random.uniform(0, 1000), 2)
                    
            elif col_type in ['DATE']:
                record[col_name] = (datetime.now() - timedelta(days=random.randint(1, 365))).date()
                
            elif col_type in ['TIMESTAMP', 'DATETIME']:
                record[col_name] = datetime.now() - timedelta(days=random.randint(1, 365), hours=random.randint(0, 23))
                
            elif col_type in ['BOOLEAN']:
                record[col_name] = random.choice([True, False])
                
            else:
                # Default to string
                if sample_values:
                    record[col_name] = random.choice(sample_values)
                else:
                    record[col_name] = f"Value_{i+1}"
        
        data.append(record)
    #st.write("generate_data_from_schema - finished")
    return data

def create_cortex_search_service(schema_name, table_name, search_column="CHUNK_TEXT"):
    """Create Cortex Search service for unstructured data"""
    try:
        service_name = f"{table_name}_SEARCH_SERVICE"
        full_table_name = f"SI_DEMOS.{schema_name}.{table_name}"
        
        # Create the search service
        create_service_sql = f"""
        CREATE OR REPLACE CORTEX SEARCH SERVICE SI_DEMOS.{schema_name}.{service_name}
        ON {search_column}
        ATTRIBUTES CHUNK_ID, DOCUMENT_ID, DOCUMENT_TYPE, SOURCE_SYSTEM
        WAREHOUSE = COMPUTE_WH
        TARGET_LAG = '1 minute'
        AS (
            SELECT 
                CHUNK_ID,
                DOCUMENT_ID, 
                DOCUMENT_TYPE,
                SOURCE_SYSTEM,
                {search_column}
            FROM {full_table_name}
        );
        """
        
        session.sql(create_service_sql).collect()
        st.success(f"✅ Cortex Search Service '{service_name}' created successfully")
        
        return service_name
        
    except Exception as e:
        st.error(f"❌ Error creating Cortex Search service: {str(e)}")
        return None

def create_semantic_view(schema_name, table1_info, table2_info, demo_data, company_name):
    """Create comprehensive semantic view with facts, dimensions, synonyms, and CA extension"""
    try:
        # Clean view name to remove invalid characters
        clean_company_name = company_name.replace('-', '_').replace(' ', '_').upper()
        view_name = f"{clean_company_name}_SEMANTIC_VIEW"
        
        # Use original table names (not cleaned) - these are what were actually created
        table1_name = table1_info['name']
        table2_name = table2_info['name']
        join_key = "ENTITY_ID"
        
        # Debug: Show what tables exist in the schema
        st.info(f"🔍 Checking for tables in schema SI_DEMOS.{schema_name}")
        show_existing_tables(schema_name)
        
        # Verify tables exist before creating semantic view
        st.info(f"🔍 Verifying table existence:")
        st.info(f"   - Looking for: SI_DEMOS.{schema_name}.{table1_name}")
        st.info(f"   - Looking for: SI_DEMOS.{schema_name}.{table2_name}")
        
        # Test table accessibility
        try:
            test_query1 = session.sql(f"SELECT COUNT(*) FROM SI_DEMOS.{schema_name}.{table1_name}").collect()
            st.success(f"✅ {table1_name} is accessible with {test_query1[0][0]} records")
        except Exception as e:
            st.error(f"❌ Cannot access {table1_name}: {str(e)}")
            
        try:
            test_query2 = session.sql(f"SELECT COUNT(*) FROM SI_DEMOS.{schema_name}.{table2_name}").collect()
            st.success(f"✅ {table2_name} is accessible with {test_query2[0][0]} records")
        except Exception as e:
            st.error(f"❌ Cannot access {table2_name}: {str(e)}")
        
        # Generate semantic view description
        view_description = f"Semantic view for {demo_data['title']} combining {table1_name} and {table2_name} data"
        # Clean description for SQL
        view_description = view_description.replace("'", "''")
        
        # Get actual table schemas using full paths
        table1_schema = get_table_schema(schema_name, table1_name)
        table2_schema = get_table_schema(schema_name, table2_name)
        
        # Verify tables exist and have columns
        if not table1_schema or not table2_schema:
            st.error(f"❌ Could not retrieve schema for tables {table1_name} or {table2_name}")
            st.error(f"❌ Tables must exist before creating semantic view!")
            st.error(f"❌ Expected: SI_DEMOS.{schema_name}.{table1_name}")
            st.error(f"❌ Expected: SI_DEMOS.{schema_name}.{table2_name}")
            return None
        
        # Generate facts, dimensions, and CA extension
        facts_sql, dimensions_sql, ca_extension = generate_semantic_elements_with_schema(
            schema_name, table1_name, table1_schema, table2_name, table2_schema, demo_data, company_name
        )
        
        # Generate example queries
        example_queries = generate_semantic_view_queries(demo_data, table1_name, table2_name, company_name)
        
        # Use fully qualified table names in TABLES section (no schema context needed)
        create_view_sql = f"""CREATE OR REPLACE SEMANTIC VIEW SI_DEMOS.{schema_name}.{view_name}
TABLES (
    SI_DEMOS.{schema_name}.{table1_name} PRIMARY KEY ({join_key}),
    SI_DEMOS.{schema_name}.{table2_name} PRIMARY KEY ({join_key})
)
RELATIONSHIPS (
    ENTITY_LINK AS {table1_name}({join_key}) REFERENCES {table2_name}({join_key})
)
FACTS (
{facts_sql}
)
DIMENSIONS (
{dimensions_sql}
)
COMMENT = '{view_description}'
WITH EXTENSION (CA='{ca_extension}')"""
        
        # Note: Schema context changes not supported in this environment
        # Using fully qualified table names in TABLES section instead
        st.info(f"🔄 Creating semantic view with fully qualified table names (no schema context needed)")
        
        # Show the generated SQL for debugging
        with st.expander("🔍 Debug: Generated Semantic View SQL", expanded=False):
            st.code(create_view_sql, language='sql')
        
        session.sql(create_view_sql).collect()
        st.success(f"✅ Comprehensive Semantic View '{view_name}' created successfully")
        
        return {
            'view_name': view_name,
            'example_queries': example_queries,
            'join_key': join_key
        }
        
    except Exception as e:
        st.error(f"❌ Error creating semantic view: {str(e)}")
        st.warning("⚠️ Semantic view creation failed. You can still use the regular tables for demos.")
        # Let's also show the SQL that failed for debugging
        if 'create_view_sql' in locals():
            with st.expander("🔍 Debug: SQL that failed"):
                st.code(create_view_sql, language='sql')
        return None

def show_existing_tables(schema_name):
    """Show what tables exist in the schema for debugging"""
    try:
        result = session.sql(f"""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = '{schema_name.upper()}'
            AND TABLE_CATALOG = 'SI_DEMOS'
            ORDER BY TABLE_NAME
        """).collect()
        
        if result:
            table_names = [row['TABLE_NAME'] for row in result]
            st.info(f"📋 Found {len(table_names)} tables in SI_DEMOS.{schema_name}: {', '.join(table_names)}")
        else:
            st.warning(f"⚠️ No tables found in schema SI_DEMOS.{schema_name}")
            
    except Exception as e:
        st.warning(f"⚠️ Could not list tables in schema: {str(e)}")

def get_table_schema(schema_name, table_name):
    """Get the schema information for a table using proper error handling"""
    try:
        # Get column information from Snowflake using proper quoting
        result = session.sql(f"""
            SELECT COLUMN_NAME, DATA_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = '{schema_name.upper()}' 
            AND TABLE_NAME = '{table_name.upper()}'
            ORDER BY ORDINAL_POSITION
        """).collect()
        
        if not result:
            st.warning(f"⚠️ No columns found for table {schema_name}.{table_name}")
            # Try alternative query
            try:
                result = session.sql(f"DESCRIBE TABLE SI_DEMOS.{schema_name}.{table_name}").collect()
                columns = []
                for row in result:
                    columns.append({
                        'name': row['name'],
                        'type': row['type']
                    })
                return columns
            except Exception as e2:
                st.warning(f"⚠️ DESCRIBE TABLE also failed: {str(e2)}")
                return []
        
        columns = []
        for row in result:
            columns.append({
                'name': row['COLUMN_NAME'],
                'type': row['DATA_TYPE']
            })
        
        st.info(f"📋 Found {len(columns)} columns for table {table_name}: {[col['name'] for col in columns]}")
        return columns
        
    except Exception as e:
        st.warning(f"⚠️ Could not get schema for {table_name}: {str(e)}")
        # Return empty list instead of fallback schema
        return []

def generate_semantic_elements(table1_name, table1_schema, table2_name, table2_schema, demo_data, company_name):
    """Generate facts, dimensions, and CA extension using LLM"""
    
    # Create prompt for generating semantic elements
    elements_prompt = f"""
You are creating a comprehensive Snowflake semantic view for a demo. Generate facts, dimensions, synonyms, comments, and CA extension.

Demo Context:
- Title: {demo_data['title']}
- Description: {demo_data['description']}
- Company: {company_name}
- Table 1: {table1_name} with columns: {[col['name'] + ' (' + col['type'] + ')' for col in table1_schema]}
- Table 2: {table2_name} with columns: {[col['name'] + ' (' + col['type'] + ')' for col in table2_schema]}

Generate semantic view elements with this structure:

FACTS: Numeric/measurable columns (NUMBER, FLOAT, INTEGER types)
DIMENSIONS: Categorical/descriptive columns (VARCHAR, DATE, BOOLEAN types)

For each fact/dimension, provide:
- Meaningful synonyms (5-8 alternatives)
- Business-relevant comment
- Table.column reference (use just TABLE_NAME.COLUMN_NAME, not full paths)

Return ONLY a JSON object with this structure:
{{
  "facts": [
    {{
      "table_column": "TABLE_NAME.COLUMN_NAME",
      "name": "SEMANTIC_NAME",
      "synonyms": ["synonym1", "synonym2", "synonym3", "synonym4", "synonym5"],
      "comment": "Business description of what this represents"
    }}
  ],
  "dimensions": [
    {{
      "table_column": "TABLE_NAME.COLUMN_NAME", 
      "name": "SEMANTIC_NAME",
      "synonyms": ["synonym1", "synonym2", "synonym3", "synonym4", "synonym5"],
      "comment": "Business description of what this represents"
    }}
  ],
  "sample_queries": [
    "What are the top performing categories by revenue?",
    "Show me trends over the last quarter",
    "Which segments have the highest conversion rates?"
  ]
}}
"""

    try:
        # Get semantic elements from LLM
        result = session.sql("""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'claude-4-sonnet',
                ?
            ) as llm_response
        """, [elements_prompt]).collect()
        
        response = result[0]['LLM_RESPONSE']
        
        # Parse JSON response
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            elements_data = json.loads(match.group(0))
            
            # Generate SQL for facts with full table paths
            facts_sql = ""
            for fact in elements_data.get('facts', []):
                # Convert TABLE_NAME.COLUMN to full path
                table_col_parts = fact['table_column'].split('.')
                if len(table_col_parts) == 2:
                    table_ref, column_ref = table_col_parts
                    # Use just the table name in the semantic view (not full path)
                    full_reference = f"{table_ref}.{column_ref}"
                else:
                    full_reference = fact['table_column']
                
                synonyms_str = "','".join(fact['synonyms'])
                # Escape single quotes in comment
                comment = fact['comment'].replace("'", "''")
                facts_sql += f"    {full_reference} as {fact['name']} with synonyms=('{synonyms_str}') comment='{comment}'"
                if fact != elements_data['facts'][-1]:  # Add comma if not last
                    facts_sql += ","
                facts_sql += "\n"
            
            # Generate SQL for dimensions with full table paths
            dimensions_sql = ""
            for dim in elements_data.get('dimensions', []):
                # Convert TABLE_NAME.COLUMN to full path
                table_col_parts = dim['table_column'].split('.')
                if len(table_col_parts) == 2:
                    table_ref, column_ref = table_col_parts
                    # Use just the table name in the semantic view (not full path)
                    full_reference = f"{table_ref}.{column_ref}"
                else:
                    full_reference = dim['table_column']
                
                synonyms_str = "','".join(dim['synonyms'])
                # Escape single quotes in comment
                comment = dim['comment'].replace("'", "''")
                dimensions_sql += f"    {full_reference} as {dim['name']} with synonyms=('{synonyms_str}') comment='{comment}'"
                if dim != elements_data['dimensions'][-1]:  # Add comma if not last
                    dimensions_sql += ","
                dimensions_sql += "\n"
            
            # Remove trailing newlines
            facts_sql = facts_sql.rstrip('\n')
            dimensions_sql = dimensions_sql.rstrip('\n')
            
            # Generate CA extension
            ca_extension = generate_ca_extension(table1_name, table1_schema, table2_name, table2_schema, elements_data)
            
            return facts_sql, dimensions_sql, ca_extension
            
        else:
            return generate_fallback_semantic_elements(table1_name, table1_schema, table2_name, table2_schema)
            
    except Exception as e:
        st.warning(f"⚠️ Could not generate semantic elements with LLM: {str(e)}")
        return generate_fallback_semantic_elements(table1_name, table1_schema, table2_name, table2_schema)

def generate_fallback_semantic_elements(table1_name, table1_schema, table2_name, table2_schema):
    """Generate basic semantic elements without schema paths when LLM fails"""
    
    # Generate basic facts from numeric columns using table names
    facts_sql = ""
    facts_list = []
    
    # Always include ENTITY_ID from both tables as facts
    facts_list.append(f"    {table1_name}.ENTITY_ID as ENTITY_ID with synonyms=('id','entity_key','record_id','unique_identifier','identifier') comment='Unique identifier for joining tables from {table1_name}'")
    facts_list.append(f"    {table2_name}.ENTITY_ID as ENTITY_ID with synonyms=('id','entity_key','record_id','unique_identifier','identifier') comment='Unique identifier for joining tables from {table2_name}'")
    
    # Add other numeric columns
    for table_name, schema in [(table1_name, table1_schema), (table2_name, table2_schema)]:
        if schema:  # Only process if schema is not empty
            for col in schema:
                if col['type'] in ['NUMBER', 'FLOAT', 'INTEGER', 'DECIMAL', 'DOUBLE'] and col['name'] != 'ENTITY_ID':
                    facts_list.append(f"    {table_name}.{col['name']} as {col['name']} with synonyms=('value','amount','quantity','measure','metric') comment='Numeric value from {table_name}'")
                    break  # Just take first non-ENTITY_ID numeric column per table
    
    facts_sql = ",\n".join(facts_list)
    
    # Generate basic dimensions from text/date columns using table names
    dimensions_sql = ""
    dimensions_list = []
    
    for table_name, schema in [(table1_name, table1_schema), (table2_name, table2_schema)]:
        if schema:  # Only process if schema is not empty
            for col in schema:
                if col['type'] in ['VARCHAR', 'TEXT', 'STRING', 'DATE', 'TIMESTAMP', 'BOOLEAN'] and col['name'] != 'ENTITY_ID':
                    if 'DATE' in col['type'] or 'TIME' in col['type']:
                        dimensions_list.append(f"    {table_name}.{col['name']} as {col['name']} with synonyms=('date','time','timestamp','when','period') comment='Date/time dimension from {table_name}'")
                    else:
                        dimensions_list.append(f"    {table_name}.{col['name']} as {col['name']} with synonyms=('name','title','label','description','category') comment='Text dimension from {table_name}'")
                    if len(dimensions_list) >= 3:  # Limit to 3 dimensions total
                        break
        if len(dimensions_list) >= 3:
            break
    
    # If no dimensions found, create basic ones using first non-ENTITY_ID column
    if not dimensions_list:
        dimensions_list.append(f"    {table1_name}.ENTITY_ID as ENTITY_ID with synonyms=('key','identifier','id','reference','index') comment='Entity key dimension'")
    
    dimensions_sql = ",\n".join(dimensions_list)
    
    # Simple CA extension
    ca_extension = json.dumps({
        "tables": [
            {"name": table1_name, "dimensions": [], "facts": []},
            {"name": table2_name, "dimensions": [], "facts": []}
        ],
        "verified_queries": [
            {
                "name": "Show all records",
                "question": "Show all records",
                "sql": f"SELECT * FROM {table1_name} LIMIT 10",
                "use_as_onboarding_question": False,
                "verified_by": "Demo Generator",
                "verified_at": int(datetime.now().timestamp())
            }
        ]
    }).replace('"', '\\"')
    
    return facts_sql, dimensions_sql, ca_extension

def generate_semantic_elements_with_schema(schema_name, table1_name, table1_schema, table2_name, table2_schema, demo_data, company_name):
    """Generate facts, dimensions, and CA extension using LLM with full table paths"""
    
    # Create prompt for generating semantic elements
    elements_prompt = f"""
You are creating a comprehensive Snowflake semantic view for a demo. Generate facts, dimensions, synonyms, comments, and CA extension.

Demo Context:
- Title: {demo_data['title']}
- Description: {demo_data['description']}
- Company: {company_name}
- Table 1: {table1_name} with columns: {[col['name'] + ' (' + col['type'] + ')' for col in table1_schema]}
- Table 2: {table2_name} with columns: {[col['name'] + ' (' + col['type'] + ')' for col in table2_schema]}

Generate semantic view elements with this structure:

FACTS: Numeric/measurable columns (NUMBER, FLOAT, INTEGER types)
DIMENSIONS: Categorical/descriptive columns (VARCHAR, DATE, BOOLEAN types)

For each fact/dimension, provide:
- Meaningful synonyms (5-8 alternatives using underscores instead of spaces)
- Business-relevant comment
- Table.column reference (use just TABLE_NAME.COLUMN_NAME)
- IMPORTANT: The "name" field should be the same as the COLUMN_NAME (not a different semantic name)
- IMPORTANT: Always include ENTITY_ID from each table as a fact

Return ONLY a JSON object with this structure:
{{
  "facts": [
    {{
      "table_column": "TABLE_NAME.COLUMN_NAME",
      "name": "COLUMN_NAME",
      "synonyms": ["synonym_1", "synonym_2", "synonym_3", "synonym_4", "synonym_5"],
      "comment": "Business description of what this represents"
    }}
  ],
  "dimensions": [
    {{
      "table_column": "TABLE_NAME.COLUMN_NAME", 
      "name": "COLUMN_NAME",
      "synonyms": ["synonym_1", "synonym_2", "synonym_3", "synonym_4", "synonym_5"],
      "comment": "Business description of what this represents"
    }}
  ],
  "sample_queries": [
    "What are the top performing categories by revenue?",
    "Show me trends over the last quarter",
    "Which segments have the highest conversion rates?"
  ]
}}
"""

    try:
        # Get semantic elements from LLM
        result = session.sql("""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'claude-4-sonnet',
                ?
            ) as llm_response
        """, [elements_prompt]).collect()
        
        response = result[0]['LLM_RESPONSE']
        
        # Parse JSON response
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            elements_data = json.loads(match.group(0))
            
            # Generate SQL for facts using full table names
            facts_sql = ""
            facts_list = elements_data.get('facts', [])
            
            # Always ensure ENTITY_ID from both tables is included as facts
            entity_ids_added = set()
            for fact in facts_list:
                table_col_parts = fact['table_column'].split('.')
                if len(table_col_parts) == 2:
                    table_ref, column_ref = table_col_parts
                    if column_ref == 'ENTITY_ID':
                        entity_ids_added.add(table_ref)
            
            # Add missing ENTITY_ID facts
            for table_name in [table1_name, table2_name]:
                if table_name not in entity_ids_added:
                    facts_list.append({
                        'table_column': f"{table_name}.ENTITY_ID",
                        'name': 'ENTITY_ID',
                        'synonyms': ['id', 'entity_key', 'record_id', 'unique_identifier', 'identifier'],
                        'comment': f'Unique identifier for joining tables from {table_name}'
                    })
            
            for i, fact in enumerate(facts_list):
                # Use TABLE_NAME.COLUMN format directly
                table_col_parts = fact['table_column'].split('.')
                if len(table_col_parts) == 2:
                    table_ref, column_ref = table_col_parts
                    full_reference = f"{table_ref}.{column_ref}"
                else:
                    full_reference = f"{table1_name}.{fact['table_column']}"
                
                # Replace spaces with underscores in synonyms
                synonyms_clean = [syn.replace(' ', '_').replace('-', '_') for syn in fact['synonyms']]
                synonyms_str = "','".join(synonyms_clean)
                # Escape single quotes in comment
                comment = fact['comment'].replace("'", "''")
                facts_sql += f"    {full_reference} as {fact['name']} with synonyms=('{synonyms_str}') comment='{comment}'"
                if i < len(facts_list) - 1:  # Add comma if not last
                    facts_sql += ","
                facts_sql += "\n"
            
            # Generate SQL for dimensions using full table names
            dimensions_sql = ""
            dimensions_list = elements_data.get('dimensions', [])
            
            for i, dim in enumerate(dimensions_list):
                # Use TABLE_NAME.COLUMN format directly
                table_col_parts = dim['table_column'].split('.')
                if len(table_col_parts) == 2:
                    table_ref, column_ref = table_col_parts
                    full_reference = f"{table_ref}.{column_ref}"
                else:
                    full_reference = f"{table1_name}.{dim['table_column']}"
                
                # Replace spaces with underscores in synonyms
                synonyms_clean = [syn.replace(' ', '_').replace('-', '_') for syn in dim['synonyms']]
                synonyms_str = "','".join(synonyms_clean)
                # Escape single quotes in comment
                comment = dim['comment'].replace("'", "''")
                dimensions_sql += f"    {full_reference} as {dim['name']} with synonyms=('{synonyms_str}') comment='{comment}'"
                if i < len(dimensions_list) - 1:  # Add comma if not last
                    dimensions_sql += ","
                dimensions_sql += "\n"
            
            # Remove trailing newlines
            facts_sql = facts_sql.rstrip('\n')
            dimensions_sql = dimensions_sql.rstrip('\n')
            
            # Generate CA extension
            ca_extension = generate_ca_extension(table1_name, table1_schema, table2_name, table2_schema, elements_data)
            
            return facts_sql, dimensions_sql, ca_extension
            
        else:
            return generate_fallback_semantic_elements_with_schema(schema_name, table1_name, table1_schema, table2_name, table2_schema)
            
    except Exception as e:
        st.warning(f"⚠️ Could not generate semantic elements with LLM: {str(e)}")
        return generate_fallback_semantic_elements_with_schema(schema_name, table1_name, table1_schema, table2_name, table2_schema)

def generate_fallback_semantic_elements_with_schema(schema_name, table1_name, table1_schema, table2_name, table2_schema):
    """Generate basic semantic elements when LLM fails or schema is incomplete"""
    
    # Generate basic facts from numeric columns using table names
    facts_sql = ""
    facts_found = False
    
    for table_name, schema in [(table1_name, table1_schema), (table2_name, table2_schema)]:
        if schema:  # Only process if schema is not empty
            for col in schema:
                if col['type'] in ['NUMBER', 'FLOAT', 'INTEGER', 'DECIMAL', 'DOUBLE']:
                    if facts_found:
                        facts_sql += ",\n"
                    facts_sql += f"    {table_name}.{col['name']} as {col['name']} with synonyms=('value','amount','quantity','measure','metric') comment='Numeric value from {table_name}'"
                    facts_found = True
                    break  # Just take first numeric column per table
    
    # If no numeric columns found, use ENTITY_ID as fact
    if not facts_found:
        facts_sql = f"    {table1_name}.ENTITY_ID as ENTITY_ID with synonyms=('id','entity_key','record_id','unique_id','identifier') comment='Unique identifier for joining tables'"
    
    # Generate basic dimensions from text/date columns using table names
    dimensions_sql = ""
    dimensions_found = False
    
    for table_name, schema in [(table1_name, table1_schema), (table2_name, table2_schema)]:
        if schema:  # Only process if schema is not empty
            for col in schema:
                if col['type'] in ['VARCHAR', 'TEXT', 'STRING', 'DATE', 'TIMESTAMP', 'BOOLEAN'] and col['name'] != 'ENTITY_ID':
                    if dimensions_found:
                        dimensions_sql += ",\n"
                    if 'DATE' in col['type'] or 'TIME' in col['type']:
                        dimensions_sql += f"    {table_name}.{col['name']} as {col['name']} with synonyms=('date','time','timestamp','when','period') comment='Date/time dimension from {table_name}'"
                    else:
                        dimensions_sql += f"    {table_name}.{col['name']} as {col['name']} with synonyms=('name','title','label','description','category') comment='Text dimension from {table_name}'"
                    dimensions_found = True
                    if dimensions_sql.count('\n') >= 2:  # Limit to 3 dimensions total
                        break
        if dimensions_sql.count('\n') >= 2:
            break
    
    # If no dimensions found, create basic ones using ENTITY_ID
    if not dimensions_found:
        dimensions_sql = f"    {table1_name}.ENTITY_ID as ENTITY_KEY with synonyms=('key','identifier','id','reference','index') comment='Entity key dimension'"
    
    # Simple CA extension
    ca_extension = json.dumps({
        "tables": [
            {"name": table1_name, "dimensions": [], "facts": []},
            {"name": table2_name, "dimensions": [], "facts": []}
        ],
        "verified_queries": [
            {
                "name": "Show all records",
                "question": "Show all records",
                "sql": f"SELECT * FROM SI_DEMOS.{schema_name}.{table1_name} LIMIT 10",
                "use_as_onboarding_question": False,
                "verified_by": "Demo Generator",
                "verified_at": int(datetime.now().timestamp())
            }
        ]
    }).replace('"', '\\"')
    
    return facts_sql, dimensions_sql, ca_extension

def generate_ca_extension(table1_name, table1_schema, table2_name, table2_schema, elements_data):
    """Generate CA extension JSON with actual sample values from tables"""
    
    # Create sample CA extension structure
    ca_data = {
        "tables": [
            {
                "name": table1_name,
                "dimensions": [],
                "facts": [],
                "time_dimensions": []
            },
            {
                "name": table2_name, 
                "dimensions": [],
                "facts": [],
                "time_dimensions": []
            }
        ],
        "verified_queries": []
    }
    
    # Helper function to get realistic sample values based on column type and name
    def get_sample_values(col_name, col_type, table_name):
        col_name_upper = col_name.upper()
        
        if col_type in ['NUMBER', 'INTEGER', 'FLOAT', 'DECIMAL']:
            if 'ID' in col_name_upper:
                return [str(random.randint(1, 200)), str(random.randint(1, 200)), str(random.randint(1, 200))]
            elif 'COST' in col_name_upper or 'PRICE' in col_name_upper or 'REVENUE' in col_name_upper:
                return [str(round(random.uniform(100, 5000), 2)), str(round(random.uniform(100, 5000), 2)), str(round(random.uniform(100, 5000), 2))]
            elif 'PERCENTAGE' in col_name_upper or 'RATE' in col_name_upper:
                return [str(round(random.uniform(0, 100), 1)), str(round(random.uniform(0, 100), 1)), str(round(random.uniform(0, 100), 1))]
            else:
                return [str(round(random.uniform(1, 1000), 2)), str(round(random.uniform(1, 1000), 2)), str(round(random.uniform(1, 1000), 2))]
        elif col_type in ['VARCHAR', 'STRING', 'TEXT']:
            if 'ID' in col_name_upper:
                return [f"ID_{random.randint(1000, 9999)}", f"ID_{random.randint(1000, 9999)}", f"ID_{random.randint(1000, 9999)}"]
            elif 'NAME' in col_name_upper:
                return ["Alpha", "Beta", "Gamma"]
            elif 'STATUS' in col_name_upper:
                return ["Active", "Inactive", "Pending"]
            else:
                return ["Value_A", "Value_B", "Value_C"]
        elif col_type in ['DATE']:
            return ["2024-01-15", "2024-02-20", "2024-03-10"]
        elif col_type in ['TIMESTAMP', 'DATETIME']:
            return ["2024-01-15T10:30:00.000+0000", "2024-02-20T14:15:00.000+0000", "2024-03-10T09:45:00.000+0000"]
        elif col_type in ['BOOLEAN']:
            return ["TRUE", "FALSE", "TRUE"]
        else:
            return ["Sample_1", "Sample_2", "Sample_3"]
    
    # Add sample values for each element
    for dim in elements_data.get('dimensions', []):
        table_name = dim['table_column'].split('.')[0]
        col_name = dim['table_column'].split('.')[1]
        
        # Find column type from schema
        col_type = 'STRING'  # default
        for table_name_check, schema in [(table1_name, table1_schema), (table2_name, table2_schema)]:
            if table_name_check == table_name and schema:
                for col in schema:
                    if col['name'] == col_name:
                        col_type = col['type']
                        break
        
        # Find the right table in ca_data
        for table in ca_data['tables']:
            if table['name'] == table_name:
                if 'DATE' in col_name.upper() or 'TIME' in col_name.upper() or col_type in ['DATE', 'TIMESTAMP', 'DATETIME']:
                    table['time_dimensions'].append({
                        "name": col_name,
                        "sample_values": get_sample_values(col_name, col_type, table_name)
                    })
                else:
                    table['dimensions'].append({
                        "name": col_name,
                        "sample_values": get_sample_values(col_name, col_type, table_name)
                    })
    
    for fact in elements_data.get('facts', []):
        table_name = fact['table_column'].split('.')[0]
        col_name = fact['table_column'].split('.')[1]
        
        # Find column type from schema
        col_type = 'NUMBER'  # default for facts
        for table_name_check, schema in [(table1_name, table1_schema), (table2_name, table2_schema)]:
            if table_name_check == table_name and schema:
                for col in schema:
                    if col['name'] == col_name:
                        col_type = col['type']
                        break
        
        # Find the right table in ca_data
        for table in ca_data['tables']:
            if table['name'] == table_name:
                table['facts'].append({
                    "name": col_name,
                    "sample_values": get_sample_values(col_name, col_type, table_name)
                })
    
    # Add sample verified queries
    for query in elements_data.get('sample_queries', []):
        ca_data['verified_queries'].append({
            "name": query,
            "question": query,
            "sql": f"SELECT * FROM {table1_name} LIMIT 10",
            "use_as_onboarding_question": False,
            "verified_by": "Demo Generator",
            "verified_at": int(datetime.now().timestamp())
        })
    
    return json.dumps(ca_data).replace('"', '\\"')

def generate_semantic_view_queries(demo_data, table1_name, table2_name, company_name):
    """Generate example queries for the semantic view using LLM"""
    query_prompt = f"""
Generate 5 realistic natural language questions that a business user would ask about the data in these two joined tables for a {demo_data['title']} demo.

Context:
- Company: {company_name}
- Demo: {demo_data['title']}
- Description: {demo_data['description']}
- Table 1: {table1_name}
- Table 2: {table2_name}
- Tables are joined on ENTITY_ID

Generate business-relevant questions that Cortex Analyst could answer, such as:
- Trend analysis questions
- Aggregation questions  
- Comparison questions
- Performance questions
- Insight questions

Return ONLY a JSON array of question strings:
["question 1", "question 2", "question 3", "question 4", "question 5"]
"""

    try:
        result = session.sql("""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'claude-4-sonnet',
                ?
            ) as llm_response
        """, [query_prompt]).collect()
        
        response = result[0]['LLM_RESPONSE']
        
        # Parse JSON response
        match = re.search(r'\[.*\]', response, re.DOTALL)
        if match:
            questions = json.loads(match.group(0))
            return questions
        else:
            return get_fallback_queries(demo_data['title'])
            
    except Exception as e:
        st.warning(f"⚠️ Could not generate custom queries, using fallback: {str(e)}")
        return get_fallback_queries(demo_data['title'])

def get_fallback_queries(demo_title):
    """Fallback queries if LLM generation fails"""
    return [
        "What are the top 10 performing entities by revenue?",
        "Show me trends over the last 6 months",
        "Which categories have the highest growth rate?",
        "What is the average performance by region?",
        "Compare this quarter's results to last quarter"
    ]

def generate_chunked_data_from_samples(text_samples, num_records, table_info, company_name):
    """Generate chunked unstructured data from LLM text samples"""
    data = []
    chunk_id = 1
    
    for i in range(num_records):
        # Select a random text sample
        full_text = random.choice(text_samples)
        
        # Split into chunks (simulate document chunking)
        sentences = full_text.split('. ')
        
        # Create chunks of 1-2 sentences each
        chunk_size = random.randint(1, 2)
        for j in range(0, len(sentences), chunk_size):
            chunk_sentences = sentences[j:j+chunk_size]
            chunk_text = '. '.join(chunk_sentences)
            if chunk_text and not chunk_text.endswith('.'):
                chunk_text += '.'
                
            if chunk_text.strip():
                data.append({
                    'CHUNK_ID': f'CHUNK_{chunk_id:08d}',
                    'DOCUMENT_ID': f'DOC_{i+1:06d}',
                    'CHUNK_TEXT': chunk_text.strip(),
                    'CHUNK_POSITION': (j // chunk_size) + 1,
                    'CHUNK_LENGTH': len(chunk_text),
                    'DOCUMENT_TYPE': table_info['name'].replace('_CHUNKS', '').lower(),
                    'SOURCE_SYSTEM': company_name.upper(),
                    'CREATED_DATE': (datetime.now() - timedelta(days=random.randint(1, 365))).date(),
                    'LAST_MODIFIED': datetime.now() - timedelta(days=random.randint(0, 30)),
                    'METADATA': json.dumps({
                        'source_table': table_info['name'],
                        'chunk_method': 'sentence_boundary',
                        'language': 'en',
                        'confidence_score': round(random.uniform(0.7, 1.0), 2)
                    })
                })
                chunk_id += 1
    
    return data

def generate_fallback_data(table_name, num_records, company_name, join_key_values=None):
    """Fallback data generation when LLM fails"""
    # Use the existing create_sample_data function as fallback
    return create_sample_data("", table_name, num_records, company_name, join_key_values)

def generate_fallback_unstructured_data(table_name, num_records, company_name):
    """Fallback unstructured data when LLM fails"""
    fallback_texts = [
        "This document contains important business information that needs to be searchable and accessible.",
        "The quarterly review shows significant improvements in key performance indicators across all departments.",
        "Customer feedback indicates high satisfaction with our latest product features and service quality.",
        "Compliance requirements have been updated to reflect the latest regulatory changes in our industry.",
        "The technical documentation provides detailed instructions for system configuration and maintenance.",
        "Market analysis reveals new opportunities for expansion in emerging geographical regions.",
        "Employee training materials have been revised to include best practices and updated procedures.",
        "Financial projections indicate steady growth potential over the next fiscal year period.",
        "Quality assurance protocols ensure consistent delivery of services meeting industry standards.",
        "Strategic planning documents outline key initiatives for digital transformation and innovation."
    ]
    
    return generate_chunked_data_from_samples(fallback_texts, num_records, {'name': table_name}, company_name)

def create_sample_data(table_type, table_name, num_records, company_name, join_key_values=None):
    """Enhanced sample data creation with optional join keys"""
    data = []
    
    # Basic fallback schema
    base_columns = []
    if join_key_values is not None:
        base_columns.append(('ENTITY_ID', 'NUMBER'))
    
    base_columns.extend([
        ('ID', 'NUMBER'),
        ('NAME', 'STRING'), 
        ('CATEGORY', 'STRING'),
        ('VALUE', 'FLOAT'),
        ('STATUS', 'STRING'),
        ('CREATED_DATE', 'DATE'),
        ('MODIFIED_TIMESTAMP', 'TIMESTAMP')
    ])
    
    for i in range(num_records):
        record = {}
        
        for col_name, col_type in base_columns:
            if col_name == 'ENTITY_ID' and join_key_values is not None:
                # Use sequential assignment to ensure uniqueness within the table
                record[col_name] = join_key_values[i]
            elif col_name == 'ID':
                record[col_name] = i + 1
            elif col_name == 'NAME':
                record[col_name] = f"{company_name}_Item_{i+1}"
            elif col_name == 'CATEGORY':
                record[col_name] = random.choice(['A', 'B', 'C', 'Premium'])
            elif col_name == 'VALUE':
                record[col_name] = round(random.uniform(10, 1000), 2)
            elif col_name == 'STATUS':
                record[col_name] = random.choice(['Active', 'Inactive', 'Pending'])
            elif col_name == 'CREATED_DATE':
                record[col_name] = (datetime.now() - timedelta(days=random.randint(1, 365))).date()
            elif col_name == 'MODIFIED_TIMESTAMP':
                record[col_name] = datetime.now() - timedelta(days=random.randint(0, 30))
        
        data.append(record)
    
    return data

def create_structured_table_with_constraints(full_table_name, df, schema_name, table_name):
    """Create structured table with PRIMARY KEY constraint on ENTITY_ID"""
    try:
        # Drop table if exists
        session.sql(f"DROP TABLE IF EXISTS {full_table_name}").collect()
        
        # Generate DDL with proper data types and PRIMARY KEY constraint
        columns_ddl = []
        for col_name in df.columns:
            col_dtype = df[col_name].dtype
            
            # Map pandas dtypes to Snowflake types
            if col_name == 'ENTITY_ID':
                # Always make ENTITY_ID a NUMBER with PRIMARY KEY
                columns_ddl.append(f"{col_name} NUMBER PRIMARY KEY")
            elif col_dtype == 'int64' or col_dtype == 'Int64':
                columns_ddl.append(f"{col_name} NUMBER")
            elif col_dtype == 'float64' or col_dtype == 'Float64':
                columns_ddl.append(f"{col_name} FLOAT")
            elif col_dtype == 'bool' or col_dtype == 'boolean':
                columns_ddl.append(f"{col_name} BOOLEAN")
            elif col_dtype == 'datetime64[ns]' or 'datetime' in str(col_dtype):
                columns_ddl.append(f"{col_name} TIMESTAMP")
            elif col_dtype == 'object':
                # Check if it's a date column by looking at sample values
                sample_val = df[col_name].dropna().iloc[0] if not df[col_name].dropna().empty else None
                if hasattr(sample_val, 'date') and not hasattr(sample_val, 'time'):
                    columns_ddl.append(f"{col_name} DATE")
                else:
                    columns_ddl.append(f"{col_name} STRING")
            else:
                # Default to STRING for unknown types
                columns_ddl.append(f"{col_name} STRING")
        
        # Create table with constraints
        create_table_ddl = f"""
        CREATE OR REPLACE TABLE {full_table_name} (
            {', '.join(columns_ddl)}
        )
        """
        
        session.sql(create_table_ddl).collect()
        st.success(f"✅ Table '{table_name}' created with PRIMARY KEY constraint on ENTITY_ID")
        
        # Insert data using Snowpark DataFrame
        snow_df = session.create_dataframe(df)
        snow_df.write.mode("append").save_as_table(full_table_name)
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error creating structured table {table_name} with constraints: {str(e)}")
        # Fallback to regular table creation
        try:
            snow_df = session.create_dataframe(df)
            snow_df.write.mode("overwrite").save_as_table(full_table_name)
            st.warning(f"⚠️ Created {table_name} without PRIMARY KEY constraint (fallback)")
            return True
        except Exception as e2:
            st.error(f"❌ Fallback table creation also failed: {str(e2)}")
            return False

def create_tables_in_snowflake(schema_name, demo_data, num_records, company_name, enable_search_service=False, enable_semantic_view=False):
    """Create schema and tables in Snowflake with LLM-generated realistic data"""
    try:
        # Create database and schema properly
        session.sql(f"CREATE DATABASE IF NOT EXISTS SI_DEMOS").collect()
        session.sql(f"CREATE SCHEMA IF NOT EXISTS SI_DEMOS.{schema_name}").collect()
        st.success(f"✅ Schema 'SI_DEMOS.{schema_name}' created successfully")
        
        results = []
        structured_tables_data = {}
        unstructured_table_info = None
        
        # Generate unique ENTITY_ID values for each table with controlled overlap
        # Create a base pool of unique IDs
        base_entity_ids = list(range(1, num_records * 2 + 1))  # Create larger pool
        random.shuffle(base_entity_ids)
        
        # For first table: use first num_records unique values
        table1_entity_ids = base_entity_ids[:num_records]
        
        # For second table: overlap 70% with first table, 30% unique
        overlap_size = int(num_records * 0.7)
        table2_entity_ids = table1_entity_ids[:overlap_size] + base_entity_ids[num_records:num_records + (num_records - overlap_size)]
        random.shuffle(table2_entity_ids)  # Shuffle to distribute the overlapping IDs
        
        table_entity_ids = {
            'structured_1': table1_entity_ids,
            'structured_2': table2_entity_ids
        }
        
        st.write(demo_data['tables'])
        for table_key, table_info in demo_data['tables'].items():
            table_name = table_info['name']
            full_table_name = f"SI_DEMOS.{schema_name}.{table_name}"
            
            st.info(f"🤖 Generating realistic data for {table_name}...")
            
            # Generate sample data using LLM for schema and content
            if 'CHUNKS' in table_name or 'unstructured' in table_key:
                # Use LLM to generate realistic unstructured content
                with st.spinner(f"Generating {table_name} Data (Unstructured)"):
                    sample_data = generate_unstructured_content_with_llm(table_info, num_records, company_name)
                    unstructured_table_info = (table_name, table_info)
            else:
                # Use LLM to generate realistic structured data with unique join keys
                entity_ids_for_table = table_entity_ids.get(table_key, table1_entity_ids)
                with st.spinner(f"Generating {table_name} Data (Structured)"):
                    sample_data = generate_realistic_content_with_llm(table_info, num_records, company_name, True, entity_ids_for_table)
                    structured_tables_data[table_key] = (table_name, sample_data, table_info)

            if sample_data:
                # Create DataFrame
                df = pd.DataFrame(sample_data)
                
                # Show sample of generated data
                with st.expander(f"📋 Sample data for {table_name} (showing first 3 rows)"):
                    st.dataframe(df.head(3))
                
                # Create table with proper constraints for structured tables
                if 'CHUNKS' not in table_name and 'unstructured' not in table_key:
                    # This is a structured table - create with PRIMARY KEY constraint
                    create_structured_table_with_constraints(full_table_name, df, schema_name, table_name)
                else:
                    # This is an unstructured table - create normally
                    snow_df = session.create_dataframe(df)
                    snow_df.write.mode("overwrite").save_as_table(full_table_name)
                
                results.append({
                    'table': table_name,
                    'records': len(sample_data),
                    'description': table_info['description'],
                    'columns': list(df.columns)
                })
                
                st.success(f"✅ Table '{table_name}' created with {len(sample_data):,} records and {len(df.columns)} columns")
        
        # Confirm joinable tables
        if len(structured_tables_data) >= 2:
            st.success("✅ Structured tables created with unique ENTITY_ID join keys and 70% overlap for meaningful joins")
        
        # Optionally create semantic view
        if enable_semantic_view and len(structured_tables_data) >= 2:
            st.info("📊 Creating semantic view...")
            table_keys = list(structured_tables_data.keys())
            table1_key, table2_key = table_keys[0], table_keys[1]
            
            table1_name, table1_data, table1_info = structured_tables_data[table1_key]
            table2_name, table2_data, table2_info = structured_tables_data[table2_key]
            
            semantic_view_info = create_semantic_view(
                schema_name, table1_info, table2_info, demo_data, company_name
            )
            
            if semantic_view_info:
                results.append({
                    'table': semantic_view_info['view_name'],
                    'records': 'View',
                    'description': f"Semantic view combining {table1_name} and {table2_name}",
                    'columns': ['Joined view with all columns from both tables'],
                    'type': 'semantic_view',
                    'example_queries': semantic_view_info['example_queries'],
                    'join_key': semantic_view_info['join_key']
                })
        
        # Optionally create Cortex Search service
        if enable_search_service and unstructured_table_info:
            st.info("🔍 Creating Cortex Search service...")
            table_name, table_info = unstructured_table_info
            search_service = create_cortex_search_service(schema_name, table_name)
            
            if search_service:
                results.append({
                    'table': search_service,
                    'records': 'Service',
                    'description': f"Cortex Search service for {table_name}",
                    'columns': ['Search service for semantic text search'],
                    'type': 'search_service'
                })
        
        return results
        
    except Exception as e:
        st.error(f"❌ Error creating tables: {str(e)}")
        return []

def generate_data_story(company_name, demo_data, table_results):
    """Generate a concise, actionable demo guide"""
    # Separate different types of objects
    regular_tables = [t for t in table_results if t.get('type') not in ['semantic_view', 'search_service']]
    semantic_views = [t for t in table_results if t.get('type') == 'semantic_view']
    search_services = [t for t in table_results if t.get('type') == 'search_service']
    
    structured_tables = [t for t in regular_tables if not 'CHUNKS' in t['table']]
    unstructured_tables = [t for t in regular_tables if 'CHUNKS' in t['table']]
    
    total_records = sum(t['records'] for t in regular_tables if isinstance(t['records'], int))
    
    # Get business focus from demo data
    industry_focus = demo_data.get('industry_focus', 'Business Intelligence')
    business_value = demo_data.get('business_value', 'Improve operational efficiency and decision making')
    
    story = f"""
# 🎯 {company_name} Demo: {demo_data['title']}

## 📊 Data Generated
- **{len(structured_tables)} Structured Tables** ({total_records:,} records) with ENTITY_ID PRIMARY KEY for joins
- **{len(unstructured_tables)} Unstructured Table** (text chunks) for semantic search
- **1 Semantic View** connecting all data with AI-ready relationships
- **1 Cortex Search Service** for intelligent document retrieval

**Tables Created:**
"""
    
    for table in structured_tables:
        story += f"• **{table['table']}** - {table['description']}\n"
    
    for table in unstructured_tables:
        story += f"• **{table['table']}** - Searchable text content for knowledge retrieval\n"
    
    story += f"""
## 💼 Top 3 Business Value Points

1. **Unified Data Analytics** - Join structured data across tables for complete business insights
2. **AI-Powered Intelligence** - Natural language queries eliminate need for SQL expertise  
3. **Knowledge Discovery** - Semantic search finds relevant information in unstructured content

## 🔍 Example Analyst Queries (Cortex Analyst)
"""
    
    # Add example queries from semantic view if available
    if semantic_views and semantic_views[0].get('example_queries'):
        for i, query in enumerate(semantic_views[0]['example_queries'][:3], 1):
            story += f"{i}. \"{query}\"\n"
    else:
        # Fallback queries
        story += f"""1. "What are the top performing entities by key metrics this quarter?"
2. "Show me trends and patterns across all data over the last 6 months"
3. "Which categories have the highest performance and lowest costs?"
"""
    
    story += f"""
## 🔎 Example Search Queries (Cortex Search)

1. "Find best practices for {industry_focus.lower()} optimization"
2. "What are common challenges in {industry_focus.lower()} operations?"  
3. "Search for recommendations about performance improvements"

## 🚀 Step-by-Step Agent Demo Flow

### Step 1: Structured Data Analysis (Join Query)
**Ask:** *"What are the top 5 performing entities and their key metrics?"*
- ✅ Cortex Analyst queries structured tables
- ✅ Joins data using ENTITY_ID 
- ✅ Returns analytical insights with charts

### Step 2: Model Logic Follow-up  
**Ask:** *"What could be the reasons for these performance differences?"*
- ✅ Agent uses AI reasoning (not querying data)
- ✅ Provides business insights and hypotheses
- ✅ Suggests potential factors and correlations

### Step 3: Unstructured Knowledge Retrieval
**Ask:** *"Find relevant best practices or recommendations for improving these metrics"*
- ✅ Cortex Search queries unstructured content
- ✅ Returns contextual information from text data
- ✅ Combines with previous analysis for complete insights

## ✨ Demo Ready!
Your {company_name} demo environment is configured and ready to showcase the full power of Snowflake's AI agents with both structured analytics and unstructured search capabilities.
"""
    
    return story

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
            min_value=20,
            max_value=10000,
            value=100,
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
            value=True,
            help="Create a semantic view with relationships for Cortex Analyst"
        )
        if enable_semantic_view:
            st.caption("✨ Enables advanced join queries and relationships")
    
    with col2:
        enable_search_service = st.checkbox(
            "🔍 Create Cortex Search Service", 
            value=True,
            help="Create Cortex Search service for unstructured data"
        )
        if enable_search_service:
            st.caption("✨ Enables semantic search on text content")
    
    # Create Infrastructure Button
    if st.button("🛠️ Create Demo Infrastructure", type="primary"):
        if schema_name:
            with st.spinner("Creating schema and populating tables..."):
                session.sql(f"CREATE DATABASE IF NOT EXISTS SI_DEMOS").collect()
                st.success(f"✅ DATABASE SI_DEMOS EXISTS")
                
                table_results = create_tables_in_snowflake(
                    schema_name, 
                    st.session_state.selected_demo, 
                    num_records, 
                    company_name,
                    enable_search_service,
                    enable_semantic_view
                )
                
                if table_results:
                    st.session_state.generation_complete = True
                    st.session_state.table_results = table_results
                    st.session_state.schema_name = schema_name
                    
                    # Generate and display data story
                    story = generate_data_story(
                        company_name, 
                        st.session_state.selected_demo, 
                        table_results
                    )
                    
                    st.markdown("---")
                    st.markdown(story)
                    
                    # Summary metrics
                    total_records = sum(t['records'] for t in table_results if isinstance(t['records'], int))
                    st.balloons()
                    st.success(f"🎉 Demo infrastructure created successfully! Total records: {total_records:,}")

