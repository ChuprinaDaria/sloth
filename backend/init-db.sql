-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create function for tenant schema management
CREATE OR REPLACE FUNCTION create_tenant_schema(schema_name text)
RETURNS void AS $$
BEGIN
    EXECUTE format('CREATE SCHEMA IF NOT EXISTS %I', schema_name);
    EXECUTE format('GRANT ALL ON SCHEMA %I TO sloth', schema_name);
END;
$$ LANGUAGE plpgsql;

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE sloth TO sloth;
