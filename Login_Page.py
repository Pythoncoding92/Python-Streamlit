import streamlit as st
import mysql.connector
from mysql.connector import Error

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="Customer Login System",
    page_icon="🔐",
    layout="centered"
)


# ---------------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------------

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="turntable.proxy.rlwy.net",
            user="root",
            password="DSOYOxrCYfqjuhnrkcRWCxFAlTDgRXZF",
            database="project_1_test"
        )
        return conn

    except mysql.connector.Error as e:
        st.error(f"Database connection failed: {e}")
        return None


# ---------------------------------------------------------
# DATA INSERT FUNCTION
# ---------------------------------------------------------

def data_entry_sql_cust_details(
    full_name,
    address,
    ph_number,
    user_id,
    password
):
    conn_obj = get_connection()

    if conn_obj is None:
        return False

    try:
        cur_obj = conn_obj.cursor()

        sql = """
        INSERT INTO customer_details
        (full_name, address, phone_number, user_id, password)
        VALUES (%s, %s, %s, %s, %s)
        """

        data = (
            full_name,
            address,
            ph_number,
            user_id,
            password
        )

        cur_obj.execute(sql, data)
        conn_obj.commit()

        cur_obj.close()
        conn_obj.close()

        return True

    except mysql.connector.Error as e:
        conn_obj.rollback()
        conn_obj.close()

        st.error(f"Error inserting data to MySQL: {e}")
        return False


# ---------------------------------------------------------
# DATA RETRIEVE FUNCTION
# ---------------------------------------------------------

def data_retrieve(user_id_login):

    conn_obj = get_connection()

    if conn_obj is None:
        return None

    try:
        cur_obj = conn_obj.cursor()

        # Parameterized query
        query = """
        SELECT *
        FROM customer_details
        WHERE user_id = %s
        """

        cur_obj.execute(query, (user_id_login,))

        result = cur_obj.fetchone()

        cur_obj.close()
        conn_obj.close()

        return result

    except mysql.connector.Error as e:

        conn_obj.rollback()
        conn_obj.close()

        st.error(f"Error retrieving data from MySQL: {e}")

        return None


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "full_name" not in st.session_state:
    st.session_state.full_name = None


# ---------------------------------------------------------
# LOGGED-IN PAGE
# ---------------------------------------------------------

if st.session_state.logged_in:

    st.title("🎉 Welcome!")

    st.success("Login Successful")

    st.write(
        f"Welcome, **{st.session_state.full_name}**!"
    )

    st.write(
        f"User ID: **{st.session_state.user_id}**"
    )

    st.divider()

    if st.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.full_name = None

        st.rerun()


# ---------------------------------------------------------
# LOGIN / REGISTRATION PAGE
# ---------------------------------------------------------

else:

    st.title("🔐 Customer Account System")

    st.write("Welcome to our channel")

    st.divider()

    # -----------------------------------------------------
    # TABS
    # -----------------------------------------------------

    login_tab, registration_tab = st.tabs(
        ["🔑 Login", "📝 New Registration"]
    )


    # =====================================================
    # LOGIN
    # =====================================================

    with login_tab:

        st.subheader("Login")

        login_user_id = st.text_input(
            "Enter your User ID",
            key="login_user_id"
        )

        login_password = st.text_input(
            "Enter your Password",
            type="password",
            key="login_password"
        )

        login_button = st.button(
            "Login",
            type="primary",
            use_container_width=True
        )

        if login_button:

            if not login_user_id:
                st.warning("Please enter your User ID.")

            elif not login_password:
                st.warning("Please enter your password.")

            else:

                user_details_from_db = data_retrieve(
                    login_user_id
                )

                if user_details_from_db:

                    # Password is the last column
                    stored_password = user_details_from_db[-1]

                    if login_password == stored_password:

                        st.session_state.logged_in = True
                        st.session_state.user_id = login_user_id

                        # full_name is assumed to be column 2
                        st.session_state.full_name = (
                            user_details_from_db[1]
                        )

                        st.success("Login Successful!")

                        st.rerun()

                    else:

                        st.error(
                            "User ID or Password is incorrect."
                        )

                else:

                    st.error("User ID not found.")


    # =====================================================
    # REGISTRATION
    # =====================================================

    with registration_tab:

        st.subheader("Create New Account")

        with st.form("registration_form"):

            name = st.text_input(
                "Full Name"
            )

            address = st.text_area(
                "Address"
            )

            phone = st.text_input(
                "Contact Number",
                max_chars=10
            )

            new_user_id = st.text_input(
                "Set your User ID"
            )

            new_password = st.text_input(
                "Set your Password",
                type="password"
            )

            confirm_password = st.text_input(
                "Re-enter your Password",
                type="password"
            )

            register_button = st.form_submit_button(
                "Create Account",
                type="primary",
                use_container_width=True
            )


        # -------------------------------------------------
        # REGISTRATION VALIDATION
        # -------------------------------------------------

        if register_button:

            name = name.strip().upper()
            address = address.strip().upper()
            phone = phone.strip()
            new_user_id = new_user_id.strip()

            # Empty field validation

            if not name:
                st.warning("Please enter your full name.")

            elif not address:
                st.warning("Please enter your address.")

            # Phone validation

            elif len(phone) != 10 or not phone.isnumeric():

                st.error(
                    "Enter a valid 10-digit contact number."
                )

            # User ID validation

            elif not new_user_id:

                st.warning(
                    "Please enter a User ID."
                )

            else:

                # Check whether User ID already exists

                user_id_in_db = data_retrieve(
                    new_user_id
                )

                if user_id_in_db:

                    st.error(
                        "User ID already exists. "
                        "Please try another one."
                    )

                # Password validation

                elif not new_password:

                    st.warning(
                        "Please enter a password."
                    )

                elif new_password != confirm_password:

                    st.error(
                        "Passwords do not match."
                    )

                else:

                    # -------------------------------------------------
                    # INSERT DATA
                    # -------------------------------------------------

                    success = data_entry_sql_cust_details(
                        name,
                        address,
                        phone,
                        new_user_id,
                        new_password
                    )

                    if success:

                        st.success(
                            "Registration Successful! "
                            "You can now login."
                        )
