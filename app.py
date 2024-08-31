import streamlit as st
import pandas as pd

# Function to establish a database connection
def get_db_connection(username, password, host, database):
    try:
        connection = pymysql.connect(
            host=host,
            user=username,
            password=password,
            database=database,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.MySQLError as e:
        st.error(f"Error connecting to the database: {str(e)}")
        return None

# Function to fetch customer profiles from the database
def fetch_customer_profiles(connection):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM customer_profiles")
            profiles = cursor.fetchall()
            return profiles
    except pymysql.MySQLError as e:
        st.error(f"Error fetching data: {str(e)}")
        return []

# Function to insert a new customer profile into the database
def insert_customer_profile(connection, name, business_name, email, phone, address, description):
    query = """
        INSERT INTO customer_profiles (name, business_name, email, phone, address, description) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (name, business_name, email, phone, address, description))
            connection.commit()
        st.success("Profile added successfully!")
    except pymysql.MySQLError as e:
        st.error(f"Error adding profile: {str(e)}")

# Function to update an existing customer profile in the database
def update_customer_profile(connection, profile_id, name, business_name, email, phone, address, description):
    query = """
        UPDATE customer_profiles
        SET name = %s, business_name = %s, email = %s, phone = %s, address = %s, description = %s
        WHERE id = %s
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (name, business_name, email, phone, address, description, profile_id))
            connection.commit()
        st.success("Profile updated successfully!")
    except pymysql.MySQLError as e:
        st.error(f"Error updating profile: {str(e)}")

# Function to delete a customer profile from the database
def delete_customer_profile(connection, profile_id):
    query = "DELETE FROM customer_profiles WHERE id = %s"
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (profile_id,))
            connection.commit()
        st.success("Profile deleted successfully!")
    except pymysql.MySQLError as e:
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
    connection = get_db_connection(db_username, db_password, db_host, db_name)
else:
    connection = None

if connection:
    # Display profiles
    st.subheader("Customer Profiles")
    profiles = fetch_customer_profiles(connection)
    
    if profiles:
        df = pd.DataFrame(profiles)
        
        # Search Functionality
        search_term = st.text_input("Search Profiles")
        if search_term:
            df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
        
        st.dataframe(df)
        
        # Profile Editing and Deleting
        st.subheader("Edit or Delete a Profile")
        selected_id = st.selectbox("Select Profile ID", df["id"])
        
        if selected_id:
            selected_profile = df[df["id"] == selected_id].iloc[0]
            
            with st.form(key="edit_profile_form"):
                edit_name = st.text_input("Name", value=selected_profile["name"])
                edit_business_name = st.text_input("Business Name", value=selected_profile["business_name"])
                edit_email = st.text_input("Email", value=selected_profile["email"])
                edit_phone = st.text_input("Phone", value=selected_profile["phone"])
                edit_address = st.text_area("Address", value=selected_profile["address"])
                edit_description = st.text_area("Description", value=selected_profile["description"])
                
                update_button = st.form_submit_button("Update Profile")
                delete_button = st.form_submit_button("Delete Profile")
            
            if update_button:
                update_customer_profile(connection, selected_id, edit_name, edit_business_name, edit_email, edit_phone, edit_address, edit_description)
            
            if delete_button:
                delete_customer_profile(connection, selected_id)
    
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
                insert_customer_profile(connection, name, business_name, email, phone, address, description)
            else:
                st.error("Please fill in all required fields.")
else:
    st.warning("Please connect to the database to manage customer profiles.")

# Footer or additional functionality
st.write("Powered by Streamlit")
