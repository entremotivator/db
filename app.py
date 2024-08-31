import streamlit as st
import pandas as pd
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Function to establish a database connection
def get_db_connection(username, password, host, database):
    try:
        engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}/{database}")
        return engine
    except SQLAlchemyError as e:
        st.error(f"Error connecting to the database: {str(e)}")
        return None

# Function to fetch customer profiles from the database
def fetch_customer_profiles(engine):
    query = text("SELECT * FROM customer_profiles")
    try:
        with engine.connect() as connection:
            result = connection.execute(query)
            profiles = result.fetchall()
            return profiles
    except SQLAlchemyError as e:
        st.error(f"Error fetching data: {str(e)}")
        return []

# Function to insert a new customer profile into the database
def insert_customer_profile(engine, name, business_name, email, phone, address, description):
    query = text("""
        INSERT INTO customer_profiles (name, business_name, email, phone, address, description) 
        VALUES (:name, :business_name, :email, :phone, :address, :description)
    """)
    try:
        with engine.connect() as connection:
            connection.execute(query, {
                "name": name,
                "business_name": business_name,
                "email": email,
                "phone": phone,
                "address": address,
                "description": description
            })
        st.success("Profile added successfully!")
    except SQLAlchemyError as e:
        st.error(f"Error adding profile: {str(e)}")

# Function to update an existing customer profile in the database
def update_customer_profile(engine, profile_id, name, business_name, email, phone, address, description):
    query = text("""
        UPDATE customer_profiles
        SET name = :name, business_name = :business_name, email = :email, phone = :phone, address = :address, description = :description
        WHERE id = :id
    """)
    try:
        with engine.connect() as connection:
            connection.execute(query, {
                "id": profile_id,
                "name": name,
                "business_name": business_name,
                "email": email,
                "phone": phone,
                "address": address,
                "description": description
            })
        st.success("Profile updated successfully!")
    except SQLAlchemyError as e:
        st.error(f"Error updating profile: {str(e)}")

# Function to delete a customer profile from the database
def delete_customer_profile(engine, profile_id):
    query = text("DELETE FROM customer_profiles WHERE id = :id")
    try:
        with engine.connect() as connection:
            connection.execute(query, {"id": profile_id})
        st.success("Profile deleted successfully!")
    except SQLAlchemyError as e:
        st.error(f"Error deleting profile: {str(e)}")

# Streamlit app layout
st.title("Customer Business Profiles Management")

# Database connection info form
st.subheader("Database Connection")
with st.form(key="db_form"):
    db_username = st.text_input("Database Username")
    db_password = st.text_input("Database Password", type="password")
    db_host = st.text_input("Database Host", value="localhost")
    db_name = st.text_input("Database Name")
    connect_button = st.form_submit_button("Connect")

if connect_button and db_username and db_password and db_host and db_name:
    engine = get_db_connection(db_username, db_password, db_host, db_name)
else:
    engine = None

if engine:
    # Display profiles
    st.subheader("Customer Profiles")
    profiles = fetch_customer_profiles(engine)
    
    if profiles:
        df = pd.DataFrame(profiles, columns=["ID", "Name", "Business Name", "Email", "Phone", "Address", "Description", "Created At"])
        
        # Search Functionality
        search_term = st.text_input("Search Profiles")
        if search_term:
            df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
        
        st.dataframe(df)
        
        # Profile Editing and Deleting
        st.subheader("Edit or Delete a Profile")
        selected_id = st.selectbox("Select Profile ID", df["ID"])
        
        if selected_id:
            selected_profile = df[df["ID"] == selected_id].iloc[0]
            
            with st.form(key="edit_profile_form"):
                edit_name = st.text_input("Name", value=selected_profile["Name"])
                edit_business_name = st.text_input("Business Name", value=selected_profile["Business Name"])
                edit_email = st.text_input("Email", value=selected_profile["Email"])
                edit_phone = st.text_input("Phone", value=selected_profile["Phone"])
                edit_address = st.text_area("Address", value=selected_profile["Address"])
                edit_description = st.text_area("Description", value=selected_profile["Description"])
                
                update_button = st.form_submit_button("Update Profile")
                delete_button = st.form_submit_button("Delete Profile")
            
            if update_button:
                update_customer_profile(engine, selected_id, edit_name, edit_business_name, edit_email, edit_phone, edit_address, edit_description)
            
            if delete_button:
                delete_customer_profile(engine, selected_id)
    
    else:
        st.write("No profiles found.")
    
    # Adding a new customer profile
    st.subheader("Add a New Customer Profile")
    
    with st.form(key="add_profile_form"):
        name = st.text_input("Name")
        business_name = st.text_input("Business Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        address = st.text_area("Address")
        description = st.text_area("Description")
        
        submit_button = st.form_submit_button("Add Profile")
        
        if submit_button:
            if name and business_name and email:
                insert_customer_profile(engine, name, business_name, email, phone, address, description)
            else:
                st.error("Please fill in all required fields.")
else:
    st.warning("Please connect to the database to manage customer profiles.")

# Footer or additional functionality
st.write("Powered by Streamlit")
