-- Initialize PostgreSQL databases for ML Pipeline
--
-- This script creates separate databases for MLflow and Prefect

-- Create MLflow database
CREATE DATABASE mlflow;

-- Create Prefect database
CREATE DATABASE prefect;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE mlflow TO mlpipeline;
GRANT ALL PRIVILEGES ON DATABASE prefect TO mlpipeline;
