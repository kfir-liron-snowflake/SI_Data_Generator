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

-- Create compute warehouse for Cortex operations
CREATE WAREHOUSE IF NOT EXISTS compute_wh
    WITH 
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    COMMENT = 'Compute warehouse for Cortex LLM operations';

-- ================================================================================
-- 3. ENABLE CORTEX AND VERIFY SETUP
-- ================================================================================
ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION';

-- ================================================================================
-- 4. CREATE GIT INTEGRATION
-- ================================================================================

-- Create API integration for GitHub (requires ACCOUNTADMIN)
CREATE OR REPLACE API INTEGRATION SI_DATA_GENERATOR_GIT_INTEGRATION
    API_PROVIDER = GIT_HTTPS_API
    API_ALLOWED_PREFIXES = ('https://github.com/kfir-liron-snowflake/SI_Data_Generator.git')
    ENABLED = TRUE
    COMMENT = 'API integration for SI Data Generator GitHub repository';

-- Grant usage on integration to ACCOUNTADMIN
GRANT USAGE ON INTEGRATION SI_DATA_GENERATOR_GIT_INTEGRATION TO ROLE ACCOUNTADMIN;

-- Create git repository object
USE ROLE ACCOUNTADMIN;
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
    MAIN_FILE = '/Dashboard.py'
    QUERY_WAREHOUSE = SI_DEMO_WH
    COMMENT = 'SI Data Generator Streamlit Application'
    TITLE = 'Snowflake Agent Demo Data Generator';

-- Grant usage on the Streamlit app to ACCOUNTADMIN
GRANT USAGE ON STREAMLIT SI_DATA_GENERATOR_APP TO ROLE ACCOUNTADMIN;

-- ================================================================================
-- 6. ADDITIONAL SETUP FOR CORTEX SEARCH
-- ================================================================================

-- Cortex Search permissions are handled by ACCOUNTADMIN role

-- ================================================================================
-- 7. SETUP VALIDATION AND INFORMATION
-- ================================================================================

-- Set context for testing
USE ROLE ACCOUNTADMIN;
USE WAREHOUSE SI_DEMO_WH;
USE DATABASE SI_DEMOS;

-- Show created objects
SHOW DATABASES LIKE 'SI_DEMOS';
SHOW SCHEMAS IN DATABASE SI_DEMOS;
SHOW WAREHOUSES LIKE 'SI_DEMO_WH';
-- SHOW ROLES LIKE '%SI_%'; -- No custom roles created

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
   - All operations run with ACCOUNTADMIN privileges
   - No additional role grants needed for basic functionality

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
   - All permissions handled by ACCOUNTADMIN role
   - No additional role management required

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
