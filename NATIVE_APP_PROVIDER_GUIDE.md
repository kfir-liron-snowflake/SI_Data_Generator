# SI Data Generator Native App - Provider Setup Guide

This guide helps Native Application providers install, test, and release the SI Data Generator Native App using Snowflake's Native App framework.

## What This Native App Provides

The SI Data Generator Native App creates:

- **Intelligent Demo Generation**: AI-powered demo scenarios using Cortex LLM
- **Structured Data Tables**: Realistic business data with proper constraints
- **Unstructured Content**: Searchable text chunks for Cortex Search demos
- **Semantic Views**: Connected data relationships for Cortex Analyst
- **Search Services**: Ready-to-use Cortex Search implementations

## App Package Installation

### Prerequisites
- Snowflake account with Native App development capabilities
- Snow CLI installed and configured
- ACCOUNTADMIN privileges for testing

### Quick Installation
All Native App files are provided in this repository:

```bash
# Clone and navigate to the project
git clone <repository-url>
cd SI_Data_Generator

# Deploy the application package
snow app deploy

# Create a test instance
snow app run
```

The `snowflake.yml` configuration handles all artifact deployment automatically, including:
- `manifest.yml` → Application manifest
- `setup_script.sql` → Installation procedures  
- `Dashboard.py` → Streamlit interface
- `environment.yml` → Python dependencies

## Testing Your App Instance

### Deploy Test Instance
After running `snow app deploy` and `snow app run`, your test instance will be available at:
```
https://app.snowflake.com/<account>/#/apps/application/SI_DATA_GENERATOR_APP
```

### Test Scenarios
1. **Basic Functionality**: Generate a demo with company info
2. **AI Integration**: Verify Cortex LLM generates custom scenarios
3. **Data Creation**: Confirm tables, views, and search services are created
4. **Permissions**: Test with different warehouse configurations

### Validation Checklist
- App loads without errors  
- Can input customer information  
- AI generates 3 tailored demo ideas  
- Demo selection creates proper schemas  
- Tables have PRIMARY KEY constraints  
- Semantic views connect data properly  
- Cortex Search services are operational  

## Releasing New Versions

### Version Management
Update your application version in `manifest.yml`:

```yaml
version:
  name: V1_1
  label: "1.1"
  comment: "Enhanced demo generation with new industry templates"
```

### Release Process
1. **Update Code**: Make changes to Dashboard.py or other components
2. **Test Locally**: Deploy and test with `snow app deploy && snow app run`
3. **Update Manifest**: Increment version number and add release notes
4. **Deploy Package**: `snow app deploy` to update the application package
5. **Create Version**: Use Snow CLI to create and release the new version

```bash
# Create a new version from the current stage
snow app version create V1_1

# Set the new version as the default release
snow app version drop V1_1 --force  # if updating existing version
snow app release-directive set --version V1_1 --default

# Verify the release
snow app release-directive list
```

Alternative single command approach:
```bash
# Create version and set as default in one step
snow app version create V1_1 --set-as-default
```

### Advanced Release Management
For complex release scenarios including patches, rollbacks, and staged deployments, refer to the [official Snowflake Native Apps documentation](https://docs.snowflake.com/en/developer-guide/native-apps/versioning-apps).

## Architecture Overview

```
SI Data Generator Native App
├── APPLICATION ROLE: app_instance_role
├── APPLICATIONS (Schema)
│   └── DASHBOARD (Streamlit App)
├── CONFIG (Schema)
│   └── REGISTER_SINGLE_REFERENCE (Callback Procedure)
└── Consumer Warehouse Reference
    ├── USAGE privilege
    └── OPERATE privilege
```

## Customization for Providers

### Modify Demo Templates
Edit fallback scenarios in `Dashboard.py`:
```python
def get_fallback_demo_ideas(company_name, team_members, use_cases):
    # Customize industry-specific templates
    return [
        {"title": "Your Custom Demo", "description": "..."},
        # Add more templates
    ]
```

### Adjust Resource Requirements
Update `manifest.yml` for different warehouse requirements:
```yaml
references:
  - consumer_warehouse:
      object_type: warehouse
      label: "Demo Generation Warehouse"
      description: "Minimum SMALL warehouse recommended for optimal performance"
```

## Consumer Management

### Installation for Consumers
Consumers install via Snowflake Marketplace or direct sharing:
```sql
-- Consumer installs the app
CREATE APPLICATION si_data_generator_app
  FROM APPLICATION PACKAGE provider_account.si_data_generator_pkg;

-- Grant warehouse access
GRANT USAGE, OPERATE ON WAREHOUSE consumer_warehouse 
  TO APPLICATION si_data_generator_app;
```

### Consumer Cleanup
```sql
-- Remove application instance
DROP APPLICATION si_data_generator_app;

-- Clean up generated demo schemas (consumer responsibility)
DROP SCHEMA IF EXISTS demo_schema_name;
```

## Monitoring & Analytics

### Provider Analytics
Monitor app usage through Snowflake's Native App analytics:
- Installation counts
- Active usage metrics  
- Error rates and performance
- Consumer feedback

### Performance Optimization
- Monitor Cortex function usage
- Optimize data generation algorithms
- Track warehouse consumption patterns
- Implement efficient cleanup procedures

## Troubleshooting

### Common Provider Issues

**Deployment Failures**
```bash
# Check manifest syntax
snow app deploy --validate-only

# Review setup script
snow app deploy --debug
```

**Permission Errors**
- Verify `setup_script.sql` creates all required schemas
- Ensure proper grants to `app_instance_role`
- Check consumer warehouse permissions

**Consumer Installation Issues**
- Validate manifest references section
- Test callback procedures
- Verify privilege requirements

## Success Indicators

**Ready for Distribution When:**
- Test instance deploys without errors
- All demo generation workflows complete successfully  
- Consumer can install and use immediately
- Proper cleanup procedures work
- Documentation is complete

## Support Resources

- [Snowflake Native Apps Documentation](https://docs.snowflake.com/en/developer-guide/native-apps/)
- [Snow CLI Reference](https://docs.snowflake.com/en/developer-guide/snowflake-cli/)
- [Application Package Management](https://docs.snowflake.com/en/developer-guide/native-apps/creating-app-package/)

---

**Ready to empower customers with intelligent demo generation!**