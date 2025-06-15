import mysql.connector
import streamlit as st
import pandas as pd
import json
import numpy as np

# CREATE TABLE users(  
#     id VARCHAR(255) NOT NULL PRIMARY KEY,
#     create_time DATETIME COMMENT 'Create Time',
#     name VARCHAR(255),
#     father_name VARCHAR(255),
#     dob DATETIME,
#     id_type VARCHAR(255) NOT NULL,
#     embedding BLOB
# )

mydb = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="root",
    database="ekyc"
)

mycursor=mydb.cursor()
print("Connection Established")

def insert_records(text_info):
    sql = "INSERT INTO users(id,name,dob,gender,embedding) VALUES (%s,%s,%s,%s,%s)"
    
    value = (
        text_info['Aadhaar'],
        text_info['Name'],
        text_info['DOB'],
        text_info['Gender'],
        str(text_info['Embedding'])
    )
    mycursor.execute(sql,value)
    mydb.commit()
    
    
def fetch_records(text_info):
    sql = "SELECT * FROM users WHERE id=%s"
    value = (text_info['Aadhaar'],)
    mycursor.execute(sql,value)
    
    result = mycursor.fetchall()
    
    if result:
        df = pd.DataFrame(result, columns=[desc[0] for desc in mycursor.description])
        return df
    else:
        return pd.DataFrame()
    
    
def check_duplicacy(text_info):
    is_duplicate = False
    df =  fetch_records(text_info)
    if df.shape[0]>0:
        is_duplicate = True
    return is_duplicate

def get_all_embeddings(cursor):
    cursor.execute("SELECT id, name, dob, gender, embedding FROM users")
    results = cursor.fetchall()

    users = []
    for row in results:
        id, name, dob, gender, embedding = row
        users.append((id, name, dob, gender, embedding))

    return users