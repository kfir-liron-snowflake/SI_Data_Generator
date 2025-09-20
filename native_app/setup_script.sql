-- ================================================================================
-- SI Data Generator Native App Setup Script
-- 
-- This script sets up the environment for the SI Data Generator Native Application
-- within the application's own context and schemas.
-- ================================================================================

-- Create application role for permissions
CREATE APPLICATION ROLE IF NOT EXISTS app_instance_role;

-- Create application schemas for organization
CREATE SCHEMA IF NOT EXISTS APPLICATIONS
    COMMENT = 'Schema for Streamlit applications and configuration';

CREATE SCHEMA IF NOT EXISTS CONFIG
    COMMENT = 'Schema for generated demo data tables and semantic views';

-- Grant schema usage to application role
GRANT USAGE ON SCHEMA APPLICATIONS TO APPLICATION ROLE app_instance_role;
GRANT USAGE ON SCHEMA CONFIG TO APPLICATION ROLE app_instance_role;
GRANT ALL PRIVILEGES ON SCHEMA APPLICATIONS TO APPLICATION ROLE app_instance_role;
GRANT ALL PRIVILEGES ON SCHEMA CONFIG TO APPLICATION ROLE app_instance_role;

CREATE or replace PROCEDURE CONFIG.REGISTER_SINGLE_REFERENCE(
  ref_name STRING, operation STRING, ref_or_alias STRING)
  RETURNS STRING
  LANGUAGE SQL
  AS $$
    BEGIN
      CASE (operation)
        WHEN 'ADD' THEN
          SELECT SYSTEM$SET_REFERENCE(:ref_name, :ref_or_alias);
        WHEN 'REMOVE' THEN
          SELECT SYSTEM$REMOVE_REFERENCE(:ref_name);
        WHEN 'CLEAR' THEN
          SELECT SYSTEM$REMOVE_REFERENCE(:ref_name);
      ELSE
        RETURN 'unknown operation: ' || operation;
      END CASE;
      RETURN NULL;
    END;
  $$;

GRANT USAGE 
  ON PROCEDURE CONFIG.REGISTER_SINGLE_REFERENCE(STRING, STRING, STRING) 
  TO APPLICATION ROLE app_instance_role;

-- Create the Streamlit application
CREATE OR REPLACE STREAMLIT APPLICATIONS.DASHBOARD
FROM '/ui'
MAIN_FILE = '/Dashboard.py'
TITLE='Snowflake Intelligence Demo Data Generator';

-- Grant Streamlit access to application role
GRANT USAGE ON STREAMLIT APPLICATIONS.DASHBOARD TO APPLICATION ROLE app_instance_role;