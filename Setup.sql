-- ================================================================================
-- SI Data Generator Setup Script
-- 
-- This script sets up the complete environment for the SI Data Generator
-- Streamlit application including database, permissions, git integration,
-- and the Streamlit app itself.
--
-- Requirements:
-- - ACCOUNTADMIN role to create roles, databases, and integrations
-- - Git repository: https://github.com/kfir-liron-snowflake/SI_Data_Generator
-- ================================================================================

USE ROLE ACCOUNTADMIN;

-- ================================================================================
-- 1. CREATE DATABASES AND SCHEMAS
-- ================================================================================

-- Create main demo database
CREATE DATABASE IF NOT EXISTS SI_DEMOS
    COMMENT = 'Database for Snowflake Intelligence demo data and applications';

-- Create schema for the application
CREATE SCHEMA IF NOT EXISTS SI_DEMOS.APPLICATIONS
    COMMENT = 'Schema for Streamlit applications and notebooks';

-- Create schema for demo data (this will be populated by the app)
CREATE SCHEMA IF NOT EXISTS SI_DEMOS.DEMO_DATA
    COMMENT = 'Schema for generated demo data tables and semantic views';

-- ================================================================================
-- 2. CREATE COMPUTE RESOURCES
-- ================================================================================

-- Create warehouse for the application
CREATE WAREHOUSE IF NOT EXISTS SI_DEMO_WH
    WITH 
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    COMMENT = 'Warehouse for SI Data Generator application';

-- ================================================================================
-- 3. CREATE ROLES AND PERMISSIONS
-- ================================================================================
ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION';

-- Create application role
CREATE ROLE IF NOT EXISTS SI_DATA_GENERATOR_ROLE
    COMMENT = 'Role for SI Data Generator application users';

-- Create developer role
CREATE ROLE IF NOT EXISTS SI_DEVELOPER_ROLE
    COMMENT = 'Role for developers working with SI Data Generator';

GRANT ROLE SI_DATA_GENERATOR_ROLE TO ROLE ACCOUNTADMIN;
GRANT ROLE SI_DEVELOPER_ROLE TO ROLE ACCOUNTADMIN;
-- Grant database and schema usage
GRANT USAGE ON DATABASE SI_DEMOS TO ROLE SI_DATA_GENERATOR_ROLE;
GRANT USAGE ON SCHEMA SI_DEMOS.APPLICATIONS TO ROLE SI_DATA_GENERATOR_ROLE;
GRANT USAGE ON SCHEMA SI_DEMOS.DEMO_DATA TO ROLE SI_DATA_GENERATOR_ROLE;

-- Grant comprehensive permissions on DEMO_DATA schema
GRANT ALL PRIVILEGES ON SCHEMA SI_DEMOS.DEMO_DATA TO ROLE SI_DATA_GENERATOR_ROLE;
GRANT CREATE TABLE ON SCHEMA SI_DEMOS.DEMO_DATA TO ROLE SI_DATA_GENERATOR_ROLE;
GRANT CREATE VIEW ON SCHEMA SI_DEMOS.DEMO_DATA TO ROLE SI_DATA_GENERATOR_ROLE;
GRANT CREATE SEMANTIC VIEW ON SCHEMA SI_DEMOS.DEMO_DATA TO ROLE SI_DATA_GENERATOR_ROLE;

-- Grant permissions to create and manage all object types
GRANT CREATE SCHEMA ON DATABASE SI_DEMOS TO ROLE SI_DATA_GENERATOR_ROLE;

-- Grant warehouse usage
GRANT USAGE ON WAREHOUSE SI_DEMO_WH TO ROLE SI_DATA_GENERATOR_ROLE;
GRANT OPERATE ON WAREHOUSE SI_DEMO_WH TO ROLE SI_DATA_GENERATOR_ROLE;

-- Grant developer role additional permissions
GRANT USAGE ON DATABASE SI_DEMOS TO ROLE SI_DEVELOPER_ROLE;
GRANT USAGE ON SCHEMA SI_DEMOS.APPLICATIONS TO ROLE SI_DEVELOPER_ROLE;
GRANT ALL PRIVILEGES ON SCHEMA SI_DEMOS.APPLICATIONS TO ROLE SI_DEVELOPER_ROLE;
GRANT USAGE ON WAREHOUSE SI_DEMO_WH TO ROLE SI_DEVELOPER_ROLE;

-- Grant Cortex functions usage (required for LLM integration)
-- GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.COMPLETE(STRING, STRING) TO ROLE SI_DATA_GENERATOR_ROLE;
-- GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.COMPLETE(STRING, STRING, OBJECT) TO ROLE SI_DATA_GENERATOR_ROLE;

-- Grant roles to current user (modify as needed)
-- GRANT ROLE SI_DATA_GENERATOR_ROLE TO USER CURRENT_USER();
-- GRANT ROLE SI_DEVELOPER_ROLE TO USER CURRENT_USER();

-- ================================================================================
-- 4. CREATE GIT INTEGRATION
-- ================================================================================

-- Create API integration for GitHub (requires ACCOUNTADMIN)
CREATE OR REPLACE API INTEGRATION SI_DATA_GENERATOR_GIT_INTEGRATION
    API_PROVIDER = GIT_HTTPS_API
    API_ALLOWED_PREFIXES = ('https://github.com/kfir-liron-snowflake/SI_Data_Generator.git')
    ENABLED = TRUE
    COMMENT = 'API integration for SI Data Generator GitHub repository';

-- Grant usage on integration to developer role
GRANT USAGE ON INTEGRATION SI_DATA_GENERATOR_GIT_INTEGRATION TO ROLE SI_DEVELOPER_ROLE;

-- Create git repository object
USE ROLE SI_DEVELOPER_ROLE;
USE SCHEMA SI_DEMOS.APPLICATIONS;

CREATE OR REPLACE GIT REPOSITORY SI_DATA_GENERATOR_REPO
    API_INTEGRATION = SI_DATA_GENERATOR_GIT_INTEGRATION
    GIT_CREDENTIALS = NULL  -- For public repositories
    ORIGIN = 'https://github.com/kfir-liron-snowflake/SI_Data_Generator.git'
    COMMENT = 'SI Data Generator repository containing Streamlit application';

-- ================================================================================
-- 5. CREATE STREAMLIT APPLICATION
-- ================================================================================

-- Switch to the application schema
USE SCHEMA SI_DEMOS.APPLICATIONS;
USE WAREHOUSE SI_DEMO_WH;

-- Create the Streamlit application
CREATE OR REPLACE STREAMLIT SI_DATA_GENERATOR_APP
    ROOT_LOCATION = '@SI_DEMOS.APPLICATIONS.SI_DATA_GENERATOR_REPO/branches/main'
    MAIN_FILE = '/Original_Data_Generator.py'
    QUERY_WAREHOUSE = SI_DEMO_WH
    COMMENT = 'SI Data Generator Streamlit Application'
    TITLE = 'Snowflake Agent Demo Data Generator';

-- Grant usage on the Streamlit app
GRANT USAGE ON STREAMLIT SI_DATA_GENERATOR_APP TO ROLE SI_DATA_GENERATOR_ROLE;

-- ================================================================================
-- 6. ADDITIONAL SETUP FOR CORTEX SEARCH
-- ================================================================================

-- Grant permissions for Cortex Search service creation
USE ROLE ACCOUNTADMIN;

GRANT CREATE CORTEX SEARCH SERVICE ON ALL SCHEMAS IN DATABASE SI_DEMOS TO ROLE SI_DATA_GENERATOR_ROLE;
GRANT CREATE CORTEX SEARCH SERVICE ON FUTURE SCHEMAS IN DATABASE SI_DEMOS TO ROLE SI_DATA_GENERATOR_ROLE;

-- ================================================================================
-- 7. SETUP VALIDATION AND INFORMATION
-- ================================================================================

-- Set context for testing
USE ROLE SI_DATA_GENERATOR_ROLE;
USE WAREHOUSE SI_DEMO_WH;
USE DATABASE SI_DEMOS;

-- Show created objects
SHOW DATABASES LIKE 'SI_DEMOS';
SHOW SCHEMAS IN DATABASE SI_DEMOS;
SHOW WAREHOUSES LIKE 'SI_DEMO_WH';
SHOW ROLES LIKE '%SI_%';

-- Test Cortex function access
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'claude-4-sonnet', 
    'Say "SI Data Generator setup is working!" and nothing else.'
) AS test_result;

-- ================================================================================
-- 8. POST-SETUP INSTRUCTIONS
-- ================================================================================

/*
================================================================================
POST-SETUP INSTRUCTIONS
================================================================================

1. STREAMLIT APP ACCESS:
   - The Streamlit app is available at: SI_DEMOS.APPLICATIONS.SI_DATA_GENERATOR_APP
   - Access URL will be provided in Snowsight under "Streamlit Apps"

2. USER ACCESS:
   - Grant SI_DATA_GENERATOR_ROLE to users who need to run the application
   - Grant SI_DEVELOPER_ROLE to users who need to modify the application

3. DEMO USAGE:
   - The app will create schemas under SI_DEMOS with pattern: SI_DEMOS.[COMPANY]_DEMO_[DATE]
   - Each demo creates tables, semantic views, and Cortex Search services
   - All demo data is isolated by schema for easy cleanup

4. CUSTOMIZATION:
   - Modify the Streamlit app by updating the git repository and refreshing
   - Add new demo templates by modifying the fallback demo ideas
   - Customize warehouse size based on expected usage

5. MONITORING:
   - Monitor warehouse usage and costs
   - Review generated schemas periodically for cleanup
   - Check Cortex function usage for cost optimization

6. PERMISSIONS:
   To grant access to additional users, run:
   GRANT ROLE SI_DATA_GENERATOR_ROLE TO USER '<username>';

7. CLEANUP:
   To remove demo data, drop the individual demo schemas:
   DROP SCHEMA SI_DEMOS.[COMPANY]_DEMO_[DATE];

================================================================================
SETUP COMPLETE - SI DATA GENERATOR IS READY TO USE!
================================================================================
*/

-- Final verification
SELECT 'SI Data Generator setup completed successfully! 🎉' AS status,
       CURRENT_ROLE() AS current_role,
       CURRENT_WAREHOUSE() AS current_warehouse,
       CURRENT_DATABASE() AS current_database,
       CURRENT_SCHEMA() AS current_schema;
