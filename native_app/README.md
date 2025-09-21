# SI Data Generator - Native App

**Intelligent Demo Data Generator for Snowflake Cortex Services**

Generate tailored demo environments in minutes with AI-powered scenarios that showcase Snowflake's Cortex Analyst and Cortex Search capabilities.

## What This App Does

The SI Data Generator creates complete, realistic demo environments tailored to your customers:

- **AI-Generated Scenarios**: Creates 3 custom demo ideas based on company information using Cortex LLM
- **Structured Business Data**: Generates realistic tables with proper relationships and constraints
- **Searchable Content**: Creates unstructured text data optimized for Cortex Search
- **Semantic Views**: Builds AI-ready views with relationships for Cortex Analyst
- **Search Services**: Configures Cortex Search services for document retrieval

## Getting Started

### Prerequisites
- Snowflake account with Cortex functions enabled
- A warehouse with USAGE and OPERATE privileges granted to this application
- ACCOUNTADMIN or equivalent privileges for initial setup

### Installation
1. Install the application from the Snowflake Marketplace or via sharing
2. Grant warehouse access to the application:
   ```sql
   GRANT USAGE, OPERATE ON WAREHOUSE your_warehouse 
   TO APPLICATION si_data_generator_app;
   ```
3. Access the application through Snowflake's Apps interface

## How to Use

### Step 1: Customer Information
Enter details about your customer:
- **Company URL**: The customer's website (used for context)
- **Team Members**: Key stakeholders who will see the demo
- **Use Cases**: Specific business scenarios they want to explore

### Step 2: AI Demo Generation
The app uses Snowflake Cortex LLM to generate 3 tailored demo scenarios based on your input, such as:
- E-commerce product analytics with customer behavior insights
- Healthcare patient data analysis with compliance considerations
- Financial services risk assessment with regulatory reporting

### Step 3: Demo Selection
Choose the most relevant demo scenario for your customer's needs.

### Step 4: Data Generation
The app automatically creates:
- **2 Structured Tables**: Business data with PRIMARY KEY constraints for optimal joins
- **1 Unstructured Table**: Searchable text chunks for semantic search demos
- **1 Semantic View**: Connects all data with AI-ready relationships
- **1 Cortex Search Service**: Ready-to-use semantic search functionality

## Generated Demo Structure

Each demo creates a dedicated schema with the following objects:

```
CUSTOMER_DEMO_YYYYMMDD/
├── [TABLE_1] (Structured data with ENTITY_ID primary key)
├── [TABLE_2] (Related structured data with ENTITY_ID primary key)
├── [CONTENT]_CHUNKS (Unstructured searchable content)
├── [CUSTOMER]_SEMANTIC_VIEW (Joins all structured data)
└── [CONTENT]_CHUNKS_SEARCH_SERVICE (Cortex Search service)
```

## Example Use Cases

### E-commerce Demo
- **Customer Profiles**: Demographics, preferences, purchase history
- **Sales Transactions**: Orders, products, revenue data
- **Product Reviews**: Searchable customer feedback
- **Semantic View**: Complete customer journey analysis

### Healthcare Demo
- **Patient Records**: Demographics, medical history, treatments
- **Clinical Data**: Lab results, diagnoses, medications
- **Research Documents**: Medical literature and case studies
- **Semantic View**: Patient care analytics and outcomes

### Financial Services Demo
- **Account Data**: Customer profiles, account types, balances
- **Transaction History**: Payments, transfers, investment activity
- **Regulatory Documents**: Compliance reports and policies
- **Semantic View**: Risk assessment and regulatory reporting

## Working with Generated Data

### Cortex Analyst Integration
The semantic views are designed to work seamlessly with Cortex Analyst:
```sql
-- Example query for Cortex Analyst
SELECT * FROM [CUSTOMER]_SEMANTIC_VIEW 
WHERE [relevant_conditions];
```

### Cortex Search Usage
Use the generated search service for semantic document retrieval:
```sql
-- Example search query
SELECT * FROM TABLE(
  [CONTENT]_CHUNKS_SEARCH_SERVICE.SEARCH(
    'your search query here',
    LIMIT => 10
  )
);
```

## Data Management

### Schema Organization
- Each demo gets its own schema named `[COMPANY]_DEMO_[DATE]`
- All objects within a demo are self-contained
- Easy to clean up when demos are no longer needed

### Cleanup
Remove demo data when no longer needed:
```sql
-- List all demo schemas
SHOW SCHEMAS LIKE '%_DEMO_%';

-- Remove specific demo
DROP SCHEMA IF EXISTS [COMPANY]_DEMO_[DATE] CASCADE;
```

## Best Practices

### Demo Preparation
1. **Research the Customer**: Use their actual website URL for better AI context
2. **Identify Key Stakeholders**: Include relevant team members for targeted scenarios
3. **Define Clear Use Cases**: Specific business problems lead to better demos

### During the Demo
1. **Start with the Story**: Explain the business context before showing data
2. **Show the Journey**: Demonstrate how structured and unstructured data work together
3. **Interactive Exploration**: Use Cortex Analyst for live query generation
4. **Search Capabilities**: Showcase semantic search with relevant business questions

### After the Demo
1. **Leave Access**: Consider leaving the demo environment for customer exploration
2. **Provide Documentation**: Share query examples and use case explanations
3. **Plan Next Steps**: Discuss how to implement similar solutions with their real data

## Troubleshooting

### Common Issues

**"Insufficient privileges" Error**
- Ensure warehouse access is granted to the application
- Verify Cortex functions are available in your account

**"Demo generation failed" Error**
- Check that Cortex LLM functions are accessible
- Verify warehouse has sufficient resources

**"Search service creation failed" Error**
- Ensure account has Cortex Search enabled
- Check that the warehouse can access required compute resources

### Getting Help
- Check Snowflake documentation for Cortex services
- Verify account features and privileges
- Contact your Snowflake representative for advanced configuration

## Technical Details

### Data Characteristics
- **Realistic Scale**: 100-1000 records per table (configurable)
- **Proper Relationships**: All tables join via ENTITY_ID primary keys
- **Business Context**: Data reflects real-world business scenarios
- **AI-Optimized**: Structured for optimal Cortex Analyst performance

### Performance Considerations
- Demos are designed for interactive exploration, not production workloads
- Warehouse size recommendations: SMALL or larger for optimal performance
- Search services are optimized for demo-scale data volumes

---

**Ready to create compelling Snowflake demos that showcase the power of AI-driven analytics!**

For technical support or feature requests, contact your Snowflake representative.
