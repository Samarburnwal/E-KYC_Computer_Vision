import streamlit as st

# Page configuration
st.set_page_config(page_title="User Authentication", layout="wide")

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
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # Image Upload Fields (One is required)
    image1 = st.file_uploader("Upload Profile Image (Optional)", type=["jpg", "png", "jpeg"])
    image2 = st.file_uploader("Upload ID Proof (Optional)", type=["jpg", "png", "jpeg"])

    if st.button("Submit"):
        if image1 or image2:  # Ensure at least one image is uploaded
            st.success(f"Welcome, {username}!")
        else:
            st.error("Please upload at least one image (Profile or ID Proof) to proceed.")

    if st.button("Go Back"):
        navigate_to("home")

# Register Page
elif st.session_state.page == "register":
    st.markdown("<h1 style='text-align: center;'>Register Page</h1>", unsafe_allow_html=True)
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    # Image Upload Fields
    image1 = st.file_uploader("Upload Profile Image", type=["jpg", "png", "jpeg"])
    image2 = st.file_uploader("Upload ID Proof", type=["jpg", "png", "jpeg"])

    if st.button("Register"):
        if new_password == confirm_password:
            if image1 and image2:
                st.success(f"Account created for {new_username}!")
                st.image(image1, caption="Profile Image", width=150)
                st.image(image2, caption="ID Proof", width=150)
            else:
                st.warning("Please upload both images.")
        else:
            st.error("Passwords do not match. Try again.")

    if st.button("Go Back"):
        navigate_to("home")

