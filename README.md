# ❄️ Snowflake Intelligence Data Generator

A powerful Streamlit application that generates tailored demo data infrastructure for Snowflake's Cortex Analyst and Cortex Search services. Create realistic, AI-powered demo environments in minutes with custom data that matches your customer's industry and use cases.

## 🎯 What This App Does

The SI Data Generator creates complete demo environments that showcase Snowflake's AI capabilities:

- **🤖 AI-Generated Demo Ideas**: Uses Cortex LLM to create 3 tailored demo scenarios based on customer information
- **📊 Realistic Structured Data**: Generates business-relevant tables with proper relationships and constraints
- **🔍 Searchable Unstructured Data**: Creates text chunks optimized for semantic search
- **🔗 Semantic Views**: Builds AI-ready views with relationships for Cortex Analyst
- **🔎 Cortex Search Services**: Configures semantic search services for document retrieval

## 🚀 Key Features

### 🎨 **Intelligent Demo Generation**
- **Customer-Specific**: Tailors demos based on company URL, team members, and use cases
- **Industry-Aware**: Generates relevant scenarios for e-commerce, healthcare, financial services, etc.
- **AI-Powered**: Uses Snowflake Cortex LLM to create realistic business contexts

### 📈 **Complete Data Infrastructure**
- **Structured Tables**: 2 tables with PRIMARY KEY constraints and realistic business data
- **Unstructured Content**: Searchable text chunks with metadata
- **Joinable Architecture**: All tables connect via ENTITY_ID for comprehensive analytics
- **Semantic Views**: AI-ready views with synonyms, relationships, and example queries

### 🔧 **Production-Ready Setup**
- **Automated Schema Creation**: Creates organized database schemas
- **Proper Constraints**: PRIMARY KEY constraints for optimal join performance
- **Cortex Integration**: Ready-to-use Cortex Search services
- **Comprehensive Documentation**: Generated demo guides and example queries

## 🏗️ Architecture

```
SI_DEMOS (Database)
├── APPLICATIONS (Schema)
│   ├── SI_DATA_GENERATOR_REPO (Git Repository)
│   └── SI_DATA_GENERATOR_APP (Streamlit App)
└── [COMPANY]_DEMO_[DATE] (Generated Demo Schemas)
    ├── TABLE_1 (Structured data with ENTITY_ID PK)
    ├── TABLE_2 (Structured data with ENTITY_ID PK)
    ├── CONTENT_CHUNKS (Unstructured searchable text)
    ├── [COMPANY]_SEMANTIC_VIEW (AI-ready view)
    └── [TABLE]_SEARCH_SERVICE (Cortex Search)
```

## 📋 Prerequisites

- **Snowflake Account** with ACCOUNTADMIN privileges
- **Cortex Access** enabled in your Snowflake account
- **Streamlit** feature enabled
- **Git Integration** capabilities

## 🛠️ Quick Setup

### 1. **Run the Setup Script**
```sql
-- Execute the complete setup script
-- File: Setup.sql
-- This creates the entire environment including:
-- - Database and schemas
-- - Roles and permissions  
-- - Git integration
-- - Streamlit application
```

### 2. **Access the Application**
- Navigate to **Data > Streamlit Apps** in Snowsight
- Open `SI_DATA_GENERATOR_APP` from `SI_DEMOS.APPLICATIONS`
- Start generating demos!

## 🎮 How to Use

### **Step 1: Customer Information**
Enter:
- **Company URL**: Customer's website (e.g., `https://acme.com`)
- **Team Members**: Who you're presenting to (e.g., "CTO, Data Team")
- **Use Cases**: Specific requirements (optional)
- **Record Count**: Number of sample records per table

### **Step 2: AI Demo Generation**
- Click **"Generate Demo Ideas"**
- App uses Cortex LLM to create 3 tailored scenarios
- Each demo includes:
  - Compelling title and description
  - Industry focus and business value
  - 2 structured tables + 1 unstructured table
  - Purpose and use case explanations

### **Step 3: Demo Selection**
- Review the 3 AI-generated demo ideas
- Each shows:
  - **Structured Table 1**: Primary business data
  - **Structured Table 2**: Supporting/related data  
  - **Unstructured Table**: Searchable content
- Select the best fit for your customer

### **Step 4: Infrastructure Creation**
- Choose schema name (auto-generated)
- Enable optional features:
  - **Semantic View**: AI-ready analytics view
  - **Cortex Search Service**: Semantic search capability
- Click **"Create Demo Infrastructure"**

### **Step 5: Demo Ready!**
The app creates:
- ✅ **Database Schema** with organized structure
- ✅ **Structured Tables** with realistic data and PRIMARY KEY constraints
- ✅ **Unstructured Table** with searchable text chunks
- ✅ **Semantic View** with relationships and example queries
- ✅ **Cortex Search Service** for document retrieval
- ✅ **Complete Documentation** with demo flow and example questions

## 🎯 Example Demo Scenarios

### **E-commerce Analytics**
- **Tables**: Sales transactions, customer profiles
- **Search**: Product reviews and feedback
- **Queries**: "What are our top-performing customer segments by revenue?"

### **Financial Services**
- **Tables**: Transaction monitoring, compliance events  
- **Search**: Regulatory documents and policies
- **Queries**: "Show me high-risk transactions and their compliance status"

### **Healthcare Analytics**
- **Tables**: Patient outcomes, treatment protocols
- **Search**: Clinical notes and research documentation
- **Queries**: "Which treatment protocols have the best patient outcomes?"

## 🔍 Demo Flow Example

### **1. Structured Analytics (Cortex Analyst)**
```
Question: "What are the top 5 performing entities and their key metrics?"
→ Cortex Analyst queries structured tables
→ Joins data using ENTITY_ID relationships
→ Returns analytical insights with visualizations
```

### **2. AI Reasoning Follow-up**
```
Question: "What could be the reasons for these performance differences?"
→ Agent uses AI reasoning (not data querying)
→ Provides business insights and hypotheses
→ Suggests potential factors and correlations
```

### **3. Knowledge Retrieval (Cortex Search)**
```
Question: "Find relevant best practices for improving these metrics"
→ Cortex Search queries unstructured content
→ Returns contextual information from text data
→ Combines with previous analysis for complete insights
```

## 📊 Generated Data Features

### **Structured Tables**
- **Realistic Business Data**: Industry-relevant columns and values
- **PRIMARY KEY Constraints**: ENTITY_ID for optimal joins
- **70% Data Overlap**: Meaningful relationships between tables
- **Proper Data Types**: NUMBER, STRING, DATE, TIMESTAMP, BOOLEAN
- **Business Context**: Relevant to customer's industry

### **Unstructured Content**
- **Chunked Text**: Optimized for semantic search
- **Rich Metadata**: Document types, sources, timestamps
- **Searchable Attributes**: CHUNK_ID, DOCUMENT_ID, DOCUMENT_TYPE
- **Realistic Content**: Business-relevant text samples

### **Semantic Views**
- **AI-Ready Relationships**: Properly defined joins
- **Business Synonyms**: Multiple ways to reference data
- **Example Queries**: Pre-built questions for demos
- **Cortex Analyst Extension**: Enhanced AI capabilities

## 🔧 Customization Options

### **Demo Templates**
Modify fallback demo ideas in the application:
```python
def get_fallback_demo_ideas(company_name, team_members, use_cases):
    # Add your custom industry templates
    # Healthcare, Finance, Retail, Manufacturing, etc.
```

### **Data Generation**
- **Record Counts**: 20 to 10,000 records per table
- **Industry Focus**: Automatic detection from company URL
- **Use Case Tailoring**: Custom scenarios based on requirements

### **Compute Resources**
```sql
-- Scale warehouse based on usage
ALTER WAREHOUSE SI_DEMO_WH SET WAREHOUSE_SIZE = 'LARGE';
```

## 📈 Business Value

### **For Sales Teams**
- **Rapid Demo Setup**: Create tailored demos in minutes
- **Customer-Specific**: Relevant to prospect's industry
- **Complete Infrastructure**: Ready-to-use AI capabilities
- **Professional Presentation**: Polished, realistic data

### **For Technical Teams**
- **Best Practices**: Proper constraints and relationships
- **AI Integration**: Cortex Analyst and Search examples
- **Scalable Architecture**: Easy to extend and modify
- **Documentation**: Complete setup and usage guides

### **For Customers**
- **Real-World Scenarios**: Relevant to their business
- **AI Capabilities**: See both analytics and search in action
- **Immediate Value**: Understand capabilities through familiar data
- **Future-Ready**: Architecture supports growth and expansion

## 🧹 Cleanup & Management

### **Remove Demo Data**
```sql
-- List all demo schemas
SHOW SCHEMAS IN DATABASE SI_DEMOS LIKE '%_DEMO_%';

-- Remove specific demo
DROP SCHEMA IF EXISTS SI_DEMOS.ACME_DEMO_20250115;
```

### **Monitor Usage**
- **Compute Costs**: Monitor warehouse usage
- **Storage**: Track table sizes in demo schemas
- **Cortex**: Review AI function call costs

## 🆘 Troubleshooting

### **Common Issues**

**"Insufficient privileges" Error**
```sql
USE ROLE ACCOUNTADMIN;
-- Re-run setup script
```

**"Cortex function not accessible" Error**
```sql
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.COMPLETE(STRING, STRING) 
TO ROLE SI_DATA_GENERATOR_ROLE;
```

**"Streamlit app not loading"**
- Verify git repository is synced
- Check file path in app definition
- Ensure all permissions are granted

## 📚 Documentation

- **`SETUP_GUIDE.md`**: Complete setup instructions
- **`Setup.sql`**: Automated environment creation
- **Generated Demo Guides**: Custom documentation for each demo

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎉 Success Stories

> *"This tool has revolutionized our demo process. We can now create customer-specific demos in minutes instead of hours, and the AI-generated scenarios are incredibly realistic and relevant."* - Sales Engineering Team

> *"The semantic views and Cortex Search integration make it easy to showcase the full power of Snowflake's AI capabilities. Our customers immediately understand the value."* - Solutions Architect

---

**Ready to create amazing Snowflake demos?** 🚀

[Get Started with Setup Guide](SETUP_GUIDE.md) | [View Setup Script](Setup.sql) | [Report Issues](https://github.com/kfir-liron-snowflake/SI_Data_Generator/issues)