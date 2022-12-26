# Databricks notebook source
# Generate a list with users and corresponding groups

from pyspark.sql import functions as F
from pyspark.sql.types import StringType, StructType, StructField

user_list = spark.sql("""SHOW USERS""").select(F.col("name")).toPandas()
for user in user_list["name"]:
    groups = spark.sql("""SHOW GROUPS WITH USER ()""".format(user)).select(F.col("name")).toPandas()
    user_list.loc[user_list["name"] == user, 'groups'] = ', '.join(groups.name)

users_schema = StructType([StructField("name", StringType(), False), StructField('groups',StringType(), False)])
updates = spark.createDataframe(data=user_list.loc[~user_list["name"].isnull()], schema=users_schema) \
            .withColumn("groups",F.explode (F.split("groups",',', -1))) \
            .write.option("mode", "overwrite").saveAsTable("default.c_db_users")
