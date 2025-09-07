# UI Deployment Guide - Snowflake Native Application

This guide walks you through deploying the SI Data Generator as a Snowflake Native Application using the Snowsight web interface.

## 🎯 Prerequisites

- **Snowflake Account** with ACCOUNTADMIN privileges
- **Native App Framework** enabled in your account
- **Cortex Functions** available
- **Streamlit** feature enabled
- **GitHub Repository** access (optional)

## 🖥️ Method 1: Upload from Local Files (Recommended)

### **Step 1: Prepare Files**
Ensure you have all files from the `native_app/` folder:
- ✅ `manifest.yml`
- ✅ `setup_script.sql`
- ✅ `ui/Dashboard` (Streamlit app)
- ✅ `requirements.txt`
- ✅ `README.md`

### **Step 2: Access Snowsight**
1. Log into **Snowsight** (https://app.snowflake.com)
2. Navigate to **Data** → **Native Apps** (left sidebar)
3. Click **"Create Application"**

### **Step 3: Upload Application**
1. Select **"Upload from Local Files"**
2. **Drag and drop** or **browse** to select all files from `native_app/` folder
3. Ensure all files are uploaded successfully
4. Click **"Next"**

### **Step 4: Configure Application**
Fill in the application details:
- **Application Name**: `SI_DATA_GENERATOR_APP`
- **Version**: `v1.0.0`
- **Description**: `Generate tailored demo data infrastructure for Cortex Analyst and Cortex Search services`
- **Category**: `Analytics`
- **Tags**: `demo, data-generation, cortex, ai, analytics`

### **Step 5: Review and Deploy**
1. **Review** the configuration
2. **Verify** all files are included
3. Click **"Create Application"**
4. Wait for deployment to complete (2-3 minutes)

### **Step 6: Grant Access**
1. After deployment, click **"Grant Access"**
2. Add users or roles that should have access
3. Click **"Grant"**

## 🔗 Method 2: Connect to Git Repository

### **Step 1: Access Snowsight**
1. Log into **Snowsight**
2. Navigate to **Data** → **Native Apps**
3. Click **"Create Application"**

### **Step 2: Connect to Git**
1. Select **"Connect to Git Repository"**
2. **Repository URL**: `https://github.com/kfir-liron-snowflake/SI_Data_Generator`
3. **Branch**: `main`
4. **Path**: `native_app/`
5. **Authentication**: Choose appropriate method (public repo = no auth needed)

### **Step 3: Configure and Deploy**
1. **Application Name**: `SI_DATA_GENERATOR_APP`
2. **Version**: `v1.0.0`
3. **Description**: `Generate tailored demo data infrastructure for Cortex Analyst and Cortex Search services`
4. Click **"Create Application"**

## 📦 Method 3: Application Package Approach

### **Step 1: Create Application Package**
1. Go to **Data** → **Application Packages**
2. Click **"Create Application Package"**
3. **Package Name**: `SI_DATA_GENERATOR_PACKAGE`
4. Upload files from `native_app/` folder
5. Click **"Create Package"**

### **Step 2: Add Version to Package**
1. Select your created package
2. Click **"Add Version"**
3. **Version**: `v1.0.0`
4. Upload the same files
5. Click **"Add Version"**

### **Step 3: Create Application from Package**
1. Go to **Data** → **Native Apps**
2. Click **"Create Application"**
3. Select **"From Application Package"**
4. Choose `SI_DATA_GENERATOR_PACKAGE`
5. Select version `v1.0.0`
6. **Application Name**: `SI_DATA_GENERATOR_APP`
7. Click **"Create Application"**

## ✅ Post-Deployment Verification

### **Step 1: Verify Application Created**
1. Go to **Data** → **Native Apps**
2. Confirm `SI_DATA_GENERATOR_APP` appears in the list
3. Status should show as **"Active"**

### **Step 2: Test Application Access**
1. Click on your application
2. Click **"Open Application"**
3. Verify the Streamlit interface loads correctly

### **Step 3: Verify Database Objects**
Run this query to verify setup:
```sql
-- Check if database and schemas were created
SHOW DATABASES LIKE 'SI_DEMOS';
SHOW SCHEMAS IN DATABASE SI_DEMOS;

-- Check if configuration table exists
SELECT * FROM SI_DEMOS.APPLICATIONS.APP_CONFIG;
```

## 👥 User Access Management

### **Grant Access to Users**
1. Go to **Data** → **Native Apps**
2. Click on `SI_DATA_GENERATOR_APP`
3. Click **"Grant Access"**
4. **Add Users/Roles**:
   - Individual users: `USER 'username'`
   - Roles: `ROLE 'role_name'`
5. Click **"Grant"**

### **Revoke Access**
1. Go to **Data** → **Native Apps**
2. Click on your application
3. Click **"Manage Access"**
4. Select users/roles to revoke
5. Click **"Revoke"**

## 🔄 Application Updates

### **Update Application**
1. Go to **Data** → **Native Apps**
2. Click on your application
3. Click **"Upgrade"**
4. Upload new files or connect to updated Git repository
5. Specify new version (e.g., `v1.1.0`)
6. Click **"Upgrade"**

### **Rollback Application**
1. Go to **Data** → **Native Apps**
2. Click on your application
3. Click **"Versions"**
4. Select previous version
5. Click **"Rollback"**

## 🛠️ Troubleshooting

### **Common Issues:**

**"Application creation failed"**
- ✅ Verify all required files are uploaded
- ✅ Check `manifest.yml` syntax
- ✅ Ensure ACCOUNTADMIN privileges

**"Setup script failed"**
- ✅ Check Cortex functions are available
- ✅ Verify warehouse permissions
- ✅ Review setup script for errors

**"Application not accessible"**
- ✅ Grant proper access to users
- ✅ Check application role permissions
- ✅ Verify database objects were created

**"Streamlit app not loading"**
- ✅ Check Python dependencies in `requirements.txt`
- ✅ Verify Streamlit app syntax
- ✅ Review application logs

### **View Application Logs**
1. Go to **Data** → **Native Apps**
2. Click on your application
3. Click **"Logs"**
4. Review error messages and debug information

## 📊 Monitoring and Analytics

### **Application Usage**
1. Go to **Data** → **Native Apps**
2. Click on your application
3. View **"Usage"** tab for statistics

### **Demo Statistics**
Access the built-in statistics in the application:
1. Open the application
2. Scroll to **"Demo Statistics"** section
3. View generated demo activity

## 🎉 Success Indicators

✅ **Deployment Successful When:**
- Application appears in **Data** → **Native Apps**
- Status shows as **"Active"**
- Streamlit interface loads without errors
- Database objects are created successfully
- Users can access the application

---

**Ready to deploy your Snowflake Native Application through the UI!** 🚀
