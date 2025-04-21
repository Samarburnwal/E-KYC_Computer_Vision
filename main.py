import streamlit as st
st.set_page_config(page_title="User Authentication", layout="wide")
 
import logging
import os
os.environ["STREAMLIT_WATCH_USE_POLLING"] = "true"
 
from sqlalchemy import text
from preProcessor import read_image, extract_id_card, save_image
from ocrEngine import extract_text
from postProcessor import extract_information
from faceVerification import detect_and_extract_face, face_comparison, get_face_embeddings
from mysql_dbOperations import insert_records, fetch_records, check_duplicacy, get_all_embeddings
from datetime import datetime
import mysql.connector
import ast
import face_recognition
import numpy as np
import base64
 
 
conn1 = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="ekyc"
)
 
def find_matching_user(user_embedding, all_users, threshold=0.5):
    for id, name, dob, gender, embeddings in all_users:
        arr_fixed = "[" + ", ".join(embeddings.strip("[]").split()) + "]"
        result = np.array(ast.literal_eval(arr_fixed))
        x = face_recognition.compare_faces([user_embedding],result,tolerance=0.4)[0]
        if x:
            return id, name, dob, gender, embeddings
    return None, None, None, None, None
 
logging_str = "[%(asctime)s:%(levelname)s:%(module)s]:%(message)s"
log_dir = "../logs"
 
os.makedirs(log_dir,exist_ok=True)
logging.basicConfig(filename=os.path.join(log_dir,"ekyc_logs.log"),level=logging.INFO,format=logging_str,filemode="a")
 
 
conn = st.connection('mysql',type='sql')
 
def image_to_base64(img_path):
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()
 
 
def main_content(id_image,face_image,conn):
    if id_image is not None:
        face_image = read_image(face_image,is_uploaded=True)
        logging.info("Face image loaded.")
        
        if face_image is not None:
            image = read_image(id_image,is_uploaded=True)
            logging.info("ID Card image loaded.")
            image_cropped,_ = extract_id_card(image)
            logging.info("ID card Info extracted.")
            face_image_path2 = detect_and_extract_face(img=image_cropped)
            face_image_path1 = save_image(face_image, "face_image.jpg", path="data\\02_intermediate_data")
            logging.info("Faces extracted and saved.")
            is_face_verified = face_comparison(image1_path=face_image_path1, image2_path=face_image_path2)
            logging.info(f"Face verification status: {'successful' if is_face_verified else 'failed'}.")
        
            if is_face_verified:
                id_image_path = save_image(image, "id_image.jpg", path="data\\02_intermediate_data")
                extracted_text = extract_text(id_image_path,confidence_threshold=0.3)
                text_info = extract_information(extracted_text)
                logging.info("Text Extracted and logging info parsed successfully")
                records = fetch_records(text_info)
                print(extracted_text)
                if records.shape[0] > 0:
                    st.write(records.shape)
                    st.write(records)
                isDupl = check_duplicacy(text_info)
                
                if isDupl:
                    st.write(f"User already present with ID {text_info['Aadhaar']}")
                else:
                    st.write(text_info)
                    date_obj = datetime.strptime(text_info['DOB'], "%d/%m/%Y")
                    text_info['DOB'] = date_obj.strftime('%Y-%m-%d')
                    text_info['Embedding'] =  get_face_embeddings(face_image_path1)
                    print(text_info)
                    insert_records(text_info)
                    logging.info(f"New user record inserted: {text_info['Aadhaar']}")
            else:
                logging.info("Face verification failed , Try again.")
        else:
            st.error("Face image not uploaded. Please upload a face image.")
            logging.error("No face image uploaded.")
    else:
        st.warning("Please upload an ID card image.")
        logging.warning("No Id card image uploaded")
                
            
 
# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "home"
 
# Function to navigate between pages
def navigate_to(page):
    st.session_state.page = page
 
# Sidebar with navigation options
st.sidebar.title("Navigation")
options = ["Home", "About", "Services", "Contact"]
st.sidebar.radio("Go to", options)
 
# Home Page
if st.session_state.page == "home":
    # Header
    st.markdown("<h1 style='text-align: center;'>Welcome to My App</h1>", unsafe_allow_html=True)
 
    # Main Content
    col1, col2, col3 = st.columns([1, 2, 1])
 
    with col2:
        st.markdown("<h2 style='text-align: center;'>User Portal</h2>", unsafe_allow_html=True)
        if st.button("Login"):
            navigate_to("login")
        if st.button("Register"):
            navigate_to("register")
 
# Login Page
elif st.session_state.page == "login":
    st.markdown("<h1 style='text-align: center;'>Login Page</h1>", unsafe_allow_html=True)
 
    image1 = st.file_uploader("Upload Profile Image (Optional)", type=["jpg", "png", "jpeg"])
    image2 = st.file_uploader("Upload ID Proof (Optional)", type=["jpg", "png", "jpeg"])
    if 'captured_image' not in st.session_state:
        st.session_state.captured_image = None
    
    capture_button = st.button("Capture Live Image")
 
    if capture_button:
        st.session_state.captured_image = st.camera_input("Or capture a live image")
 
    if st.button("Submit"):
        if image2:
            st.success(f"Welcome, User!")
            image2 = read_image(image2,is_uploaded=True)
            id_image_path = save_image(image2, "id_image.jpg", path="data\\02_intermediate_data")
            extracted_text = extract_text(id_image_path,confidence_threshold=0.3)
            text_info = extract_information(extracted_text)
            logging.info("Text Extracted and logging info parsed successfully")
            records = fetch_records(text_info)
            print(extracted_text)
            if records.shape[0] > 0:
                st.write(records.shape)
                st.write(records)
        elif image1 or st.session_state.captured_image:
            face_image = read_image(image1,is_uploaded=True)
            face_image_path1 = save_image(face_image, "face_image.jpg", path="data\\02_intermediate_data")
            embeddings = get_face_embeddings(face_image_path1)
            cursor = conn1.cursor()
            
            users = get_all_embeddings(cursor)
            id, name, dob, gender, embeddings = find_matching_user(embeddings,users)
            if id is not None:
                #st.write(id, name, dob, gender, embeddings)
                image_base64 = image_to_base64(face_image_path1)
                card_html = f"""
                    <div style="
                        background-color: #f9f9f9;
                        border: 2px solid #e0e0e0;
                        border-radius: 15px;
                        padding: 20px;
                        width: 80%;
                        margin: 20px auto;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                        font-family: Arial, sans-serif;
                        color: #444;
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                    ">
                        <div style="flex: 1;">
                            <h3 style="text-align:center; color:#2c3e50;">User Profile</h3>
                            <p><strong style='color:#2c3e50;'>ID:</strong> {id}</p>
                            <p><strong style='color:#2c3e50;'>Name:</strong> {name}</p>
                            <p><strong style='color:#2c3e50;'>Date of Birth:</strong> {dob}</p>
                            <p><strong style='color:#2c3e50;'>Gender:</strong> {gender}</p>
                        </div>
                        <div style="flex: 0 0 150px; text-align: center;">
                            <img src="data:image/jpeg;base64,{image_base64}" alt="Profile Image"
                                style="width: 120px; height: 120px; border-radius: 50%; object-fit: cover; border: 2px solid #ccc;">
                        </div>
                    </div>
                    """
                st.markdown(card_html, unsafe_allow_html=True)
            else:
                st.write("No data found")
 
        else:
            st.error("Please upload at least one image (Profile or ID Proof) to proceed.")
 
    if st.button("Go Back"):
        navigate_to("home")
 
# Register Page
elif st.session_state.page == "register":
    st.markdown("<h1 style='text-align: center;'>Register Page</h1>", unsafe_allow_html=True)
 
    faceImage = st.file_uploader("Upload Face Image", type=["jpg", "png", "jpeg"])
    idImage = st.file_uploader("Upload ID Proof", type=["jpg", "png", "jpeg"])
 
    if st.button("Register"):
        if idImage and faceImage:
            st.success(f"Account created for user!")
            
            main_content(idImage, faceImage, conn)
            
            st.image(faceImage, caption="Profile Image", width=150)
            st.image(idImage, caption="ID Proof", width=150)
        else:
            st.warning("Please upload both images.")
 
    if st.button("Go Back"):
        navigate_to("home")
 