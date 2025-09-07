# Snowflake Intelligence Data Generator - Native Application

This is the Snowflake Native Application version of the SI Data Generator, designed to be deployed and distributed through Snowflake's Native App Framework.

## 📋 What's Included

### **Core Files:**
- **`manifest.yml`** - Application manifest defining the native app structure
- **`setup_script.sql`** - Database setup script that runs during app installation
- **`streamlit_app.py`** - Main Streamlit application (adapted for native app)
- **`README.md`** - This documentation file

### **Key Features:**
- **Native App Architecture** - Properly structured for Snowflake Native App Framework
- **Configuration Management** - Database-driven configuration system
- **Demo Metadata Tracking** - Tracks all generated demos with statistics
- **Enhanced Security** - Uses application roles and proper permissions
- **Statistics Dashboard** - Built-in demo activity tracking

## 🚀 Deployment Instructions

### **Prerequisites:**
- Snowflake account with ACCOUNTADMIN privileges
- Native App Framework enabled
- Cortex functions available
- Streamlit feature enabled

### **Step 1: Package the Application**
```bash
# Create the native app package
snow app create SI_DATA_GENERATOR_APP --source native_app/
```

### **Step 2: Deploy to Snowflake**
```sql
-- Deploy the native application
CREATE APPLICATION SI_DATA_GENERATOR_APP
FROM APPLICATION PACKAGE SI_DATA_GENERATOR_APP
USING VERSION v1.0.0;
```

### **Step 3: Grant Access**
```sql
-- Grant access to users
GRANT APPLICATION ROLE SI_DATA_GENERATOR_APP!app_instance_role TO USER 'username';
```

## 🏗️ Architecture

### **Database Structure:**
```
SI_DEMOS (Database)
├── APPLICATIONS (Schema)
│   ├── APP_CONFIG (Configuration table)
│   ├── DEMO_METADATA (Demo tracking table)
│   └── DEMO_STATISTICS (Statistics view)
└── DEMO_DATA (Schema)
    └── [Generated demo schemas created by the app]
```

### **Application Roles:**
- **`app_instance_role`** - Main application role with all necessary permissions
- **Automatic role management** - Handled by Native App Framework

### **Configuration System:**
The app uses a database-driven configuration system stored in `APP_CONFIG` table:
- `DEFAULT_RECORDS` - Default number of records per table
- `MAX_RECORDS` - Maximum allowed records
- `MIN_RECORDS` - Minimum allowed records
- `DEFAULT_WAREHOUSE` - Default warehouse for operations
- `ENABLE_SEMANTIC_VIEW` - Enable semantic view creation by default
- `ENABLE_SEARCH_SERVICE` - Enable Cortex Search service creation by default

## 📊 Enhanced Features

### **Demo Metadata Tracking:**
Every generated demo is tracked with:
- **Demo ID** - Unique identifier
- **Company Information** - Name, URL, team members
- **Configuration** - Schema name, record count, use cases
- **Timestamps** - Creation date and user
- **Status** - Active/Inactive status

### **Statistics Dashboard:**
Built-in statistics showing:
- **Total demos per company**
- **Total records generated**
- **First and last demo dates**
- **Recent activity summary**

### **Configuration Management:**
- **Runtime configuration** - Stored in database, not hardcoded
- **Easy customization** - Update configuration without code changes
- **Environment-specific settings** - Different configs for dev/prod

## 🔧 Customization

### **Modify Configuration:**
```sql
-- Update default record count
UPDATE SI_DEMOS.APPLICATIONS.APP_CONFIG 
SET CONFIG_VALUE = '500' 
WHERE CONFIG_KEY = 'DEFAULT_RECORDS';

-- Disable semantic view creation by default
UPDATE SI_DEMOS.APPLICATIONS.APP_CONFIG 
SET CONFIG_VALUE = 'false' 
WHERE CONFIG_KEY = 'ENABLE_SEMANTIC_VIEW';
```

### **Add New Configuration:**
```sql
-- Add new configuration option
INSERT INTO SI_DEMOS.APPLICATIONS.APP_CONFIG 
(CONFIG_KEY, CONFIG_VALUE, DESCRIPTION) 
VALUES ('NEW_FEATURE', 'true', 'Enable new feature');
```

## 🛡️ Security Features

### **Application Role Security:**
- **Principle of least privilege** - Only necessary permissions granted
- **Automatic role management** - Handled by Native App Framework
- **Secure data access** - All operations through application roles

### **Data Isolation:**
- **Schema-based isolation** - Each demo in its own schema
- **User-specific data** - Demo metadata tied to creating user
- **Clean separation** - Application data separate from demo data

## 📈 Monitoring & Analytics

### **Built-in Statistics:**
- **Demo activity tracking** - See all generated demos
- **Usage patterns** - Understand how the app is being used
- **Performance metrics** - Track record counts and generation times

### **Query Statistics:**
```sql
-- View all demo statistics
SELECT * FROM SI_DEMOS.APPLICATIONS.DEMO_STATISTICS;

-- View recent demo activity
SELECT * FROM SI_DEMOS.APPLICATIONS.DEMO_METADATA 
WHERE CREATED_AT >= DATEADD(day, -7, CURRENT_DATE())
ORDER BY CREATED_AT DESC;
```

## 🧹 Maintenance

### **Cleanup Old Demos:**
```sql
-- Mark old demos as inactive
UPDATE SI_DEMOS.APPLICATIONS.DEMO_METADATA 
SET STATUS = 'INACTIVE' 
WHERE CREATED_AT < DATEADD(month, -3, CURRENT_DATE());

-- Drop inactive demo schemas
-- (Run this after marking demos as inactive)
```

### **Update Configuration:**
```sql
-- Update app configuration
UPDATE SI_DEMOS.APPLICATIONS.APP_CONFIG 
SET CONFIG_VALUE = 'new_value', UPDATED_AT = CURRENT_TIMESTAMP()
WHERE CONFIG_KEY = 'CONFIG_KEY';
```

## 🔄 Version Management

### **Updating the Application:**
```sql
-- Update to new version
ALTER APPLICATION SI_DATA_GENERATOR_APP 
UPGRADE USING VERSION v1.1.0;
```

### **Rollback:**
```sql
-- Rollback to previous version
ALTER APPLICATION SI_DATA_GENERATOR_APP 
UPGRADE USING VERSION v1.0.0;
```

## 🆘 Troubleshooting

### **Common Issues:**

**"Application role not found" Error**
```sql
-- Verify application is properly installed
SHOW APPLICATIONS LIKE 'SI_DATA_GENERATOR_APP';
```

**"Configuration not found" Error**
```sql
-- Check if setup script ran successfully
SELECT * FROM SI_DEMOS.APPLICATIONS.APP_CONFIG;
```

**"Statistics not loading" Error**
```sql
-- Verify demo metadata table exists
SELECT COUNT(*) FROM SI_DEMOS.APPLICATIONS.DEMO_METADATA;
```

## 📞 Support

For issues with the native application:
1. Check the troubleshooting section above
2. Verify all permissions are granted correctly
3. Review the application logs in Snowsight
4. Ensure the setup script completed successfully

---

**Ready to deploy your Snowflake Native Application!** 🚀
