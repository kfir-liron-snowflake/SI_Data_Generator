-- ================================================================================
-- SI Data Generator Native App Setup Script
-- 
-- This script sets up the environment for the SI Data Generator Native Application
-- including database objects, permissions, and initial configuration.
-- ================================================================================

-- Create application database and schemas
CREATE DATABASE IF NOT EXISTS SI_DEMOS
    COMMENT = 'Database for Snowflake Intelligence demo data and applications';

CREATE SCHEMA IF NOT EXISTS SI_DEMOS.APPLICATIONS
    COMMENT = 'Schema for Streamlit applications and configuration';

CREATE SCHEMA IF NOT EXISTS SI_DEMOS.DEMO_DATA
    COMMENT = 'Schema for generated demo data tables and semantic views';

-- Create warehouse for the application
CREATE WAREHOUSE IF NOT EXISTS SI_DEMO_WH
    WITH 
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    COMMENT = 'Warehouse for SI Data Generator application';

-- Grant permissions to application role
GRANT USAGE ON DATABASE SI_DEMOS TO APPLICATION ROLE app_instance_role;
GRANT USAGE ON SCHEMA SI_DEMOS.APPLICATIONS TO APPLICATION ROLE app_instance_role;
GRANT USAGE ON SCHEMA SI_DEMOS.DEMO_DATA TO APPLICATION ROLE app_instance_role;

-- Grant comprehensive permissions on DEMO_DATA schema
GRANT ALL PRIVILEGES ON SCHEMA SI_DEMOS.DEMO_DATA TO APPLICATION ROLE app_instance_role;
GRANT CREATE TABLE ON SCHEMA SI_DEMOS.DEMO_DATA TO APPLICATION ROLE app_instance_role;
GRANT CREATE VIEW ON SCHEMA SI_DEMOS.DEMO_DATA TO APPLICATION ROLE app_instance_role;
GRANT CREATE SEMANTIC VIEW ON SCHEMA SI_DEMOS.DEMO_DATA TO APPLICATION ROLE app_instance_role;

-- Grant permissions to create and manage all object types
GRANT CREATE SCHEMA ON DATABASE SI_DEMOS TO APPLICATION ROLE app_instance_role;

-- Grant warehouse usage
GRANT USAGE ON WAREHOUSE SI_DEMO_WH TO APPLICATION ROLE app_instance_role;
GRANT OPERATE ON WAREHOUSE SI_DEMO_WH TO APPLICATION ROLE app_instance_role;

-- Grant Cortex functions usage (required for LLM integration)
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.COMPLETE(STRING, STRING) TO APPLICATION ROLE app_instance_role;
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.COMPLETE(STRING, STRING, OBJECT) TO APPLICATION ROLE app_instance_role;

-- Grant permissions for Cortex Search service creation
GRANT CREATE CORTEX SEARCH SERVICE ON ALL SCHEMAS IN DATABASE SI_DEMOS TO APPLICATION ROLE app_instance_role;
GRANT CREATE CORTEX SEARCH SERVICE ON FUTURE SCHEMAS IN DATABASE SI_DEMOS TO APPLICATION ROLE app_instance_role;

-- Create application configuration table
CREATE OR REPLACE TABLE SI_DEMOS.APPLICATIONS.APP_CONFIG (
    CONFIG_KEY STRING PRIMARY KEY,
    CONFIG_VALUE STRING,
    DESCRIPTION STRING,
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Insert default configuration
INSERT INTO SI_DEMOS.APPLICATIONS.APP_CONFIG (CONFIG_KEY, CONFIG_VALUE, DESCRIPTION) VALUES
('DEFAULT_RECORDS', '100', 'Default number of records per table'),
('MAX_RECORDS', '10000', 'Maximum number of records per table'),
('MIN_RECORDS', '20', 'Minimum number of records per table'),
('DEFAULT_WAREHOUSE', 'SI_DEMO_WH', 'Default warehouse for demo generation'),
('ENABLE_SEMANTIC_VIEW', 'true', 'Enable semantic view creation by default'),
('ENABLE_SEARCH_SERVICE', 'true', 'Enable Cortex Search service creation by default');

-- Grant permissions on configuration table
GRANT SELECT, INSERT, UPDATE ON TABLE SI_DEMOS.APPLICATIONS.APP_CONFIG TO APPLICATION ROLE app_instance_role;

-- Create demo metadata table to track generated demos
CREATE OR REPLACE TABLE SI_DEMOS.APPLICATIONS.DEMO_METADATA (
    DEMO_ID STRING PRIMARY KEY,
    COMPANY_NAME STRING,
    COMPANY_URL STRING,
    SCHEMA_NAME STRING,
    TEAM_MEMBERS STRING,
    USE_CASES STRING,
    NUM_RECORDS INTEGER,
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    CREATED_BY STRING,
    STATUS STRING DEFAULT 'ACTIVE'
);

-- Grant permissions on metadata table
GRANT SELECT, INSERT, UPDATE ON TABLE SI_DEMOS.APPLICATIONS.DEMO_METADATA TO APPLICATION ROLE app_instance_role;

-- Create a view for demo statistics
CREATE OR REPLACE VIEW SI_DEMOS.APPLICATIONS.DEMO_STATISTICS AS
SELECT 
    COMPANY_NAME,
    COUNT(*) as TOTAL_DEMOS,
    SUM(NUM_RECORDS) as TOTAL_RECORDS,
    MIN(CREATED_AT) as FIRST_DEMO,
    MAX(CREATED_AT) as LAST_DEMO
FROM SI_DEMOS.APPLICATIONS.DEMO_METADATA
WHERE STATUS = 'ACTIVE'
GROUP BY COMPANY_NAME;

-- Grant permissions on statistics view
GRANT SELECT ON VIEW SI_DEMOS.APPLICATIONS.DEMO_STATISTICS TO APPLICATION ROLE app_instance_role;

-- Final verification
SELECT 'SI Data Generator Native App setup completed successfully! 🎉' AS status,
       CURRENT_ROLE() AS current_role,
       CURRENT_WAREHOUSE() AS current_warehouse,
       CURRENT_DATABASE() AS current_database,
       CURRENT_SCHEMA() AS current_schema;
