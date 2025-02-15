# Databricks notebook source
# Common for Feature Store 

# COMMAND ----------

# MAGIC %run ../Common

# COMMAND ----------

def read_wine_data(data_path):
    return spark.read.load(data_path,
        format="csv",
        sep=";",
        inferSchema="true",
         header="true" 
  )

# COMMAND ----------

from pyspark.sql.functions import monotonically_increasing_id

def _add_id_column(df, id_column_name):
    columns = df.columns
    new_df = df.withColumn(id_column_name, monotonically_increasing_id())
    return new_df[[id_column_name] + columns]

def _rename_columns(df):
    new_df = df
    for column in df.columns:
        new_df = new_df.withColumnRenamed(column, column.replace(" ", "_"))
    return new_df

def _create_id_df(raw_df):
    renamed_df = _rename_columns(raw_df)
    data_id_df = _add_id_column(renamed_df, "wine_id")
    return data_id_df

# COMMAND ----------

def create_id_df(data_path):
    raw_df = read_wine_data(data_path)
    return _create_id_df(raw_df)
