# Databricks notebook source
# MAGIC %md
# MAGIC # Unity Catalog Quickstart (Python)
# MAGIC 
# MAGIC This notebook provides an example workflow for getting started with Unity Catalog (see "Unity Catalog" [AWS](https://docs.databricks.com/data-governance/unity-catalog/index.html) | [Azure](https://docs.microsoft.com/azure/databricks/data-governance/unity-catalog/)) in [PySpark](https://spark.apache.org/docs/latest/api/python/) by showing how to:
# MAGIC 
# MAGIC - Choose a catalog and create a new schema.
# MAGIC - Create a managed table and add it to the schema.
# MAGIC - Query the table by using a three-level Unity Catalog namespace combination of catalog-schema-table.
# MAGIC - Manage data access permissions on the table.
# MAGIC 
# MAGIC For information about Unity Catalog concepts and terminology, see "Key concepts" ([AWS](https://docs.databricks.com/data-governance/unity-catalog/key-concepts.html) | [Azure](https://docs.microsoft.com/azure/databricks/data-governance/unity-catalog/key-concepts)).
# MAGIC 
# MAGIC ## Requirements
# MAGIC 
# MAGIC - The workspace must be attached to a Unity Catalog metastore. See "Get started using Unity Catalog" ([AWS](https://docs.databricks.com/data-governance/unity-catalog/get-started.html) | [Azure](https://docs.microsoft.com/azure/databricks/data-governance/unity-catalog/get-started)).
# MAGIC - This notebook must be attached to a cluster that uses Databricks Runtime 11.1 or higher in shared or single user access mode (see "Access mode" [AWS](https://docs.databricks.com/clusters/configure.html#access-mode) | [Azure](https://docs.microsoft.com/azure/databricks/clusters/configure#access-mode)).
# MAGIC 
# MAGIC **Note**: Some APIs can be used in PySpark with Unity Catalog. However some APIs are still under development. For those APIs, this notebook uses `spark.sql` to run the related SQL query in PySpark instead.

# COMMAND ----------

# MAGIC %md
# MAGIC # Create a catalog
# MAGIC Each Unity Catalog metastore contains a default catalog named `main` with an empty schema (also called a database) named `default`.
# MAGIC 
# MAGIC To create a catalog, use the `CREATE CATALOG` command with `spark.sql`. You must be a metastore admin to create a catalog.
# MAGIC 
# MAGIC The following commands show how to:
# MAGIC 
# MAGIC 1. Create a catalog.
# MAGIC 2. Select a catalog.
# MAGIC 3. Show all catalogs.
# MAGIC 4. Grant permissions on a catalog.
# MAGIC 5. Show all grants on a catalog.

# COMMAND ----------

# Create a catalog.
spark.sql("CREATE CATALOG IF NOT EXISTS quickstart_catalog")

# COMMAND ----------

# Set the current catalog.
spark.sql("USE CATALOG quickstart_catalog")

# COMMAND ----------

# Show all catalogs in the metastore.
display(spark.sql("SHOW CATALOGS"))

# COMMAND ----------

# Grant create and use catalog permissions for the catalog to all users on the account.
# This also works for other account-level groups and individual users.
spark.sql("""
  GRANT CREATE, USE CATALOG
  ON CATALOG quickstart_catalog
  TO `account users`""")

# COMMAND ----------

# Show grants on the quickstart catalog.
display(spark.sql("SHOW GRANT ON CATALOG quickstart_catalog"))

# COMMAND ----------

# MAGIC %md
# MAGIC # Create and manage schemas (databases)
# MAGIC Schemas, also called databases, are the second level of the Unity Catalog three-level namespace. Schemas logically organize tables and views.

# COMMAND ----------

# Create a schema in the catalog that was set earlier.
spark.sql("""
  CREATE SCHEMA IF NOT EXISTS quickstart_schema
  COMMENT 'A new Unity Catalog schema called quickstart_schema'""")

# COMMAND ----------

# Show schemas in the catalog that was set earlier.
display(spark.sql("SHOW SCHEMAS"))

# COMMAND ----------

# Describe the schema.
display(spark.sql("DESCRIBE SCHEMA EXTENDED quickstart_schema"))

# COMMAND ----------

# Grant create table, create view, and use schema permissions for the schema to all users on the account.
# This also works for other account-level groups and individual users.
spark.sql("""
  GRANT CREATE TABLE, CREATE VIEW, USE SCHEMA
  ON SCHEMA quickstart_schema
  TO `account users`""")

# COMMAND ----------

# MAGIC %md
# MAGIC # Create a managed table
# MAGIC Managed tables are the default way to create table with Unity Catalog. If no `LOCATION` is included, a table is created in the managed storage location configured for the metastore.
# MAGIC 
# MAGIC The following commands show how to:
# MAGIC 
# MAGIC 1. Select a schema.
# MAGIC 2. Create a managed table and insert records into it.
# MAGIC 3. Show all tables in a schema.
# MAGIC 4. Describe a table.

# COMMAND ----------

# Set the current schema.
spark.sql("USE quickstart_schema")

# COMMAND ----------

# Show the current database (also called a schema).
spark.catalog.currentDatabase()

# COMMAND ----------

# Define the columns when creating a table with PySpark.
from pyspark.sql.types import StructType, StructField, StringType
schema = StructType([StructField("id", StringType(), True)])

# COMMAND ----------

# Create a managed Delta table in the catalog that was set earlier.
spark.catalog.createTable("quickstart_table", schema=schema)

# COMMAND ----------

# Grant select and modify permissions for the table to all users on the account.
# This also works for other account-level groups and individual users.
spark.sql("""
  GRANT SELECT, MODIFY
  ON TABLE quickstart_table
  TO `account users`""")

# COMMAND ----------

# List the available tables in the catalog that was set earlier.
spark.catalog.listTables()

# COMMAND ----------

# Insert 10 rows into the table.
spark.range(10).selectExpr("id").write.insertInto("quickstart_table")

# COMMAND ----------

# Show the table.
display(spark.table("quickstart_table"))

# COMMAND ----------

# Show all of the available tables in the schema.
display(spark.sql("SHOW TABLES in quickstart_schema"))

# COMMAND ----------

# MAGIC %md
# MAGIC # Use Unity Catalog in Pandas API on Spark
# MAGIC 
# MAGIC [Pandas API on Spark](https://spark.apache.org/docs/latest/api/python/user_guide/pandas_on_spark/index.html) also supports some APIs for using Unity Catalog, such as `read_table` and `to_table`.

# COMMAND ----------

# Read a table from Unity Catalog. (The catalog is omitted here, as it was set earlier.)
import pyspark.pandas as ps
psdf = ps.read_table("quickstart_schema.quickstart_table")

# COMMAND ----------

# Show the table.
display(psdf)

# COMMAND ----------

# Write the table to Unity Catalog.
psdf.to_table("quickstart_schema.quickstart_table_ps")

# COMMAND ----------

# Grant select and modify permission for the table to all users on the account.
# This also works for other account-level groups and individual users.
spark.sql("""
  GRANT SELECT, MODIFY
  ON TABLE quickstart_table_ps
  TO `account users`""")

# COMMAND ----------

# Show available tables in the schema.
display(spark.sql("SHOW TABLES in quickstart_schema"))

# COMMAND ----------

# Show the table's data.
display(spark.table("quickstart_table_ps"))
