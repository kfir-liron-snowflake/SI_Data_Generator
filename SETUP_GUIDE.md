# SI Data Generator Setup Guide

This guide will help you set up the complete Snowflake Intelligence Data Generator environment using the provided setup script.

## 🎯 What Gets Created

The setup script creates a complete environment including:

- **Database & Schemas**: `SI_DEMOS` with application and data schemas
- **Compute**: `SI_DEMO_WH` warehouse (X-Small) for processing
- **Roles & Permissions**: Proper access control for users and developers
- **Git Integration**: Connection to the [GitHub repository](https://github.com/kfir-liron-snowflake/SI_Data_Generator/blob/main/Original_Data_Generator)
- **Streamlit App**: Ready-to-use data generator application
- **Cortex Permissions**: Access to AI/ML functions

## 🚀 Quick Setup

### Prerequisites
- Snowflake account with ACCOUNTADMIN privileges
- Access to Snowsight (Snowflake's web interface)

### Step 1: Run the Setup Script
1. Open Snowsight and navigate to **Worksheets**
2. Create a new worksheet
3. Copy and paste the entire contents of `setup_si_data_generator.sql`
4. **Important**: Ensure you're using the `ACCOUNTADMIN` role
5. Run the entire script (this may take 2-3 minutes)

### Step 2: Verify Setup
The script will automatically verify the setup at the end. Look for:
```sql
✅ SI Data Generator setup completed successfully! 🎉
```

### Step 3: Access the Application
1. In Snowsight, navigate to **Data > Streamlit Apps**
2. Find `SI_DATA_GENERATOR_APP` in the `SI_DEMOS.APPLICATIONS` schema
3. Click to open the application

## 👥 User Management

### Grant Access to Users
```sql
-- Grant demo generator access to a user
USE ROLE ACCOUNTADMIN;
GRANT ROLE SI_DATA_GENERATOR_ROLE TO USER 'username';

-- Grant developer access (for app modification)
GRANT ROLE SI_DEVELOPER_ROLE TO USER 'developer_username';
```

### Roles Created
- **`SI_DATA_GENERATOR_ROLE`**: Can run the app and generate demo data
- **`SI_DEVELOPER_ROLE`**: Can modify the app and manage git integration

## 🏗️ Architecture Overview

```
SI_DEMOS (Database)
├── APPLICATIONS (Schema)
│   ├── SI_DATA_GENERATOR_REPO (Git Repository)
│   └── SI_DATA_GENERATOR_APP (Streamlit App)
└── DEMO_DATA (Schema)
    └── [Generated demo schemas created by the app]

SI_DEMO_WH (Warehouse)
├── X-Small size, auto-suspend after 5 minutes
└── Single cluster (cost-optimized)
```

## 🎮 Using the Application

### Demo Generation Flow
1. **Customer Info**: Enter company URL, team members, use cases
2. **AI Generation**: App creates 3 tailored demo ideas using Cortex LLM
3. **Demo Selection**: Choose the best demo for your customer
4. **Data Generation**: App creates:
   - 2 structured tables with realistic data and PRIMARY KEY constraints
   - 1 unstructured table with searchable text chunks
   - 1 semantic view connecting all data
   - 1 Cortex Search service for semantic search

### Example Generated Objects
```
SI_DEMOS.ACME_DEMO_20250115/
├── SALES_TRANSACTIONS (Structured table with ENTITY_ID PK)
├── CUSTOMER_PROFILES (Structured table with ENTITY_ID PK)
├── PRODUCT_REVIEWS_CHUNKS (Unstructured searchable content)
├── ACME_SEMANTIC_VIEW (Joins all structured data)
└── PRODUCT_REVIEWS_CHUNKS_SEARCH_SERVICE (Cortex Search)
```

## 🔧 Customization

### Modify Demo Templates
Edit the fallback demo ideas in the application code:
```python
def get_fallback_demo_ideas(company_name, team_members, use_cases):
    # Add your custom demo templates here
```

### Adjust Compute Resources
```sql
-- Scale warehouse up/down based on usage
ALTER WAREHOUSE SI_DEMO_WH SET WAREHOUSE_SIZE = 'X-SMALL';

-- Modify auto-suspend timing
ALTER WAREHOUSE SI_DEMO_WH SET AUTO_SUSPEND = 600; -- 10 minutes
```

## 🧹 Cleanup

### Remove Demo Data
```sql
-- List all demo schemas
SHOW SCHEMAS IN DATABASE SI_DEMOS LIKE '%_DEMO_%';

-- Remove specific demo
DROP SCHEMA IF EXISTS SI_DEMOS.ACME_DEMO_20250115;
```

### Complete Uninstall
```sql
USE ROLE ACCOUNTADMIN;

-- Remove applications and data
DROP DATABASE IF EXISTS SI_DEMOS;

-- Remove compute
DROP WAREHOUSE IF EXISTS SI_DEMO_WH;

-- Remove roles
DROP ROLE IF EXISTS SI_DATA_GENERATOR_ROLE;
DROP ROLE IF EXISTS SI_DEVELOPER_ROLE;

-- Remove git integration
DROP INTEGRATION IF EXISTS SI_DATA_GENERATOR_GIT_INTEGRATION;
```

## 📊 Monitoring & Costs

### Monitor Usage
- **Compute**: Check `SI_DEMO_WH` usage in Account > Billing & Usage
- **Storage**: Monitor table sizes in generated demo schemas
- **Cortex**: Review AI function calls in usage dashboard

### Cost Optimization
- Demo data is temporary - clean up old schemas regularly
- Warehouse auto-suspends after 5 minutes of inactivity
- Use smaller record counts (100-500) for demos vs. large datasets

## 🆘 Troubleshooting

### Common Issues

**"Insufficient privileges" Error**
```sql
-- Ensure you're using ACCOUNTADMIN for setup
USE ROLE ACCOUNTADMIN;
```

**"Cortex function not accessible" Error**
```sql
-- Grant Cortex permissions
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.COMPLETE(STRING, STRING) TO ROLE SI_DATA_GENERATOR_ROLE;
```

**"Git repository not found" Error**
- Verify internet access from Snowflake account
- Ensure API integration is enabled
- Check repository URL is correct

**Streamlit app not loading**
- Verify git repository is properly synced
- Check file path in Streamlit app definition
- Ensure all required permissions are granted

## 🎉 Success Indicators

✅ **Setup Complete When You See:**
- Streamlit app loads without errors
- Can generate demo ideas with LLM
- Tables created with PRIMARY KEY constraints  
- Semantic view creates successfully
- Cortex Search service is operational

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all permissions are granted correctly
3. Review Snowflake's query history for error details
4. Ensure your account has required features enabled (Cortex, Streamlit)

---

**Ready to generate amazing demos!** 🚀