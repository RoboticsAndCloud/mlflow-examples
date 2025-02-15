# Databricks notebook source
# MAGIC %md ## Real-time Model Serving Llama 2
# MAGIC
# MAGIC ##### Overview
# MAGIC * Launches a model serving endpoint with the REST API.
# MAGIC * Sends questions to be scored to the endpoint.
# MAGIC * WIP: Creating correct request to model serving endpoint in the works.
# MAGIC
# MAGIC ##### Docs
# MAGIC * https://docs.databricks.com/api/workspace/servingendpoints
# MAGIC * https://docs.databricks.com/en/machine-learning/model-serving/create-manage-serving-endpoints.html#gpu
# MAGIC
# MAGIC ##### Widget values
# MAGIC _Workload type_
# MAGIC
# MAGIC [GPU types](https://docs.databricks.com/en/machine-learning/model-serving/create-manage-serving-endpoints.html#gpu):
# MAGIC * GPU
# MAGIC * GPU_MEDIUM - works fine
# MAGIC * GPU_MEDIUM_4
# MAGIC * GPU_MEDIUM_8
# MAGIC * GPU_LARGE_8
# MAGIC
# MAGIC _Workload size_
# MAGIC * Small - works fine
# MAGIC * Medium 
# MAGIC * Large
# MAGIC
# MAGIC ##### Last updated: 2023-10-18

# COMMAND ----------

import os
print("DBR: ", os.environ.get("DATABRICKS_RUNTIME_VERSION"))

# COMMAND ----------

# MAGIC %md #### Setup

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

# MAGIC %run ./includes/ModelServingClient

# COMMAND ----------

default_model_name = "marketplace_staging_llama_2_models.models.llama_2_7b_chat_hf"

dbutils.widgets.text("1. Model", default_model_name)
dbutils.widgets.text("2. Version", "1")
dbutils.widgets.text("3. Endpoint", "llama2_simple")
dbutils.widgets.text("4. Workload type", "")
dbutils.widgets.text("5. Workload size", "")

model_name = dbutils.widgets.get("1. Model")
version = dbutils.widgets.get("2. Version")
endpoint_name = dbutils.widgets.get("3. Endpoint")
workload_type = dbutils.widgets.get("4. Workload type")
workload_size = dbutils.widgets.get("5. Workload size")

print("model:", model_name)
print("version:", version)
print("endpoint_name:", endpoint_name)
print("workload_type:", workload_type)
print("workload_size:", workload_size)

# COMMAND ----------

assert_widget(model_name, "1. Model name")
assert_widget(version, "2. Version")
assert_widget(workload_type, "4. Workload type")
assert_widget(workload_size, "5. Workload size")

# COMMAND ----------

model_uri = f"models:/{model_name}/{version}"
model_uri

# COMMAND ----------

# MAGIC %md #### Define endpoint spec

# COMMAND ----------

served_model = "my-model"
spec = {
    "name": endpoint_name,
    "config": { 
      "served_models": [ 
        { 
          "name": "mi-llamita",
          "model_name": model_name,
          "model_version": version,
          "workload_size": "Medium",
          "scale_to_zero_enabled": False,
          "workload_type": workload_type,
        } 
      ] 
    } 
}
spec

# COMMAND ----------

# MAGIC %md #### Start the endpoint
# MAGIC
# MAGIC

# COMMAND ----------

model_serving_client.start_endpoint(spec)

# COMMAND ----------

# MAGIC %md #### Wait until endpoint is in READY state

# COMMAND ----------

model_serving_client.wait_until(endpoint_name, max=50, sleep_time=10)

# COMMAND ----------

# MAGIC %md #### Get endpoint info

# COMMAND ----------

model_serving_client.get_endpoint(endpoint_name)

# COMMAND ----------

# MAGIC %md #### Make questions

# COMMAND ----------

import pandas as pd
import json

def mk_questions(questions):
    questions = [ [q] for q in questions ]
    pdf = pd.DataFrame(questions, columns = ["question"])
    ds_dict = {"dataframe_split": pdf.to_dict(orient="split")}
    return json.dumps(ds_dict, allow_nan=True)

# COMMAND ----------

questions = [
  "What is the southern most town in the world? How do I get there?",
  "What is northern most town in the world?",
  "What is the eastern most town in the world?",
  "What is the western most town in the world?"
]

questions = mk_questions(questions)
questions

# COMMAND ----------

# MAGIC %md #### Call Model Server

# COMMAND ----------

endpoint_uri = f"https://{host_name}/serving-endpoints/{endpoint_name}/invocations"
endpoint_uri

# COMMAND ----------

import requests
import json

headers = { "Authorization": f"Bearer {token}", "Content-Type": "application/json" }
rsp = requests.post(endpoint_uri, headers=headers, data=questions, timeout=15)
rsp.status_code, print(rsp.json())
