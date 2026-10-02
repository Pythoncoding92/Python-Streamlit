import streamlit as st
import mysql.connector
from mysql.connector import Error


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Customer Account System",
    page_icon="🔐",
    layout="centered"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    try:

        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=int(st.secrets["mysql"]["port"]),
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )

        return conn

    except Error as e:

        st.error(
            "Unable to connect to MySQL database."
        )

        st.error(f"Database error: {e}")

        return None


# =========================================================
# CHECK DATABASE CONNECTION
# =========================================================

def test_database_connection():

    conn = get_connection()

    if conn is not None:

        try:

            if conn.is_connected():

                conn.close()

                return True

        except Error:
            pass

    return False


# =========================================================
# INSERT CUSTOMER DATA
# =========================================================

def data_entry_sql_cust_details(
    full_name,
    address,
    ph_number,
    user_id,
    password
):

    conn = get_connection()

    if conn is None:
        return False

    cursor = None

    try:

        cursor = conn.cursor()

        sql = """
            INSERT INTO customer_details
            (
                full_name,
                address,
                phone_number,
                user_id,
                password
            )
            VALUES (%s, %s, %s, %s, %s)
        """

        data = (
            full_name,
            address,
            ph_number,
            user_id,
            password
        )

        cursor.execute(sql, data)

        conn.commit()

        return True

    except Error as e:

        if conn.is_connected():
            conn.rollback()

        st.error(
            f"Error inserting data into MySQL: {e}"
        )

        return False

    finally:

        if cursor is not None:
            cursor.close()

        if conn.is_connected():
            conn.close()


# =========================================================
# RETRIEVE CUSTOMER DATA
# =========================================================

def data_retrieve(user_id_login):

    conn = get_connection()

    if conn is None:
        return None

    cursor = None

    try:

        cursor = conn.cursor()

        # Parameterized query
        # This is safer than using an f-string.

        sql = """
            SELECT
                cust_id,
                full_name,
                address,
                phone_number,
                user_id,
                password
            FROM customer_details
            WHERE user_id = %s
        """

        cursor.execute(
            sql,
            (user_id_login,)
        )

        result = cursor.fetchone()

        return result

    except Error as e:

        st.error(
            f"Error retrieving data from MySQL: {e}"
        )

        return None

    finally:

        if cursor is not None:
            cursor.close()

        if conn.is_connected():
            conn.close()


# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "full_name" not in st.session_state:
    st.session_state.full_name = None


# =========================================================
# LOGGED-IN USER PAGE
# =========================================================

if st.session_state.logged_in:

    st.title("🎉 Welcome!")

    st.success("Login Successful!")

    st.write(
        f"Welcome, **{st.session_state.full_name}**"
    )

    st.write(
        f"User ID: **{st.session_state.user_id}**"
    )

    st.divider()

    st.subheader("Account Information")

    user_details = data_retrieve(
        st.session_state.user_id
    )

    if user_details:

        col1, col2 = st.columns(2)

        with col1:

            st.write("**Customer ID**")
            st.write(user_details[0])

            st.write("**Full Name**")
            st.write(user_details[1])

            st.write("**Phone Number**")
            st.write(user_details[3])

        with col2:

            st.write("**User ID**")
            st.write(user_details[4])

            st.write("**Address**")
            st.write(user_details[2])

    st.divider()

    if st.button(
        "Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.full_name = None

        st.rerun()


# =========================================================
# LOGIN / REGISTRATION PAGE
# =========================================================

else:

    st.title("🔐 Customer Account System")

    st.write(
        "Welcome to our channel"
    )

    st.divider()

    # =====================================================
    # TABS
    # =====================================================

    login_tab, registration_tab = st.tabs(
        [
            "🔑 Login",
            "📝 New Registration"
        ]
    )


    # =====================================================
    # LOGIN TAB
    # =====================================================

    with login_tab:

        st.subheader("Login")

        login_user_id = st.text_input(
            "Enter your User ID",
            placeholder="Enter User ID",
            key="login_user_id"
        )

        login_password = st.text_input(
            "Enter your Password",
            type="password",
            placeholder="Enter Password",
            key="login_password"
        )

        login_button = st.button(
            "Login",
            type="primary",
            use_container_width=True
        )

        if login_button:

            # ---------------------------------------------
            # Validate User ID
            # ---------------------------------------------

            if not login_user_id.strip():

                st.warning(
                    "Please enter your User ID."
                )

            # ---------------------------------------------
            # Validate Password
            # ---------------------------------------------

            elif not login_password:

                st.warning(
                    "Please enter your password."
                )

            else:

                user_details_from_db = data_retrieve(
                    login_user_id.strip()
                )

                # -----------------------------------------
                # User ID found
                # -----------------------------------------

                if user_details_from_db:

                    # Table structure:
                    #
                    # 0 = cust_id
                    # 1 = full_name
                    # 2 = address
                    # 3 = phone_number
                    # 4 = user_id
                    # 5 = password

                    stored_password = (
                        user_details_from_db[5]
                    )

                    # -------------------------------------
                    # Check password
                    # -------------------------------------

                    if login_password == stored_password:

                        st.session_state.logged_in = True

                        st.session_state.user_id = (
                            user_details_from_db[4]
                        )

                        st.session_state.full_name = (
                            user_details_from_db[1]
                        )

                        st.rerun()

                    else:

                        st.error(
                            "User ID or Password is incorrect."
                        )

                # -----------------------------------------
                # User ID not found
                # -----------------------------------------

                else:

                    st.error(
                        "User ID not found."
                    )


    # =====================================================
    # REGISTRATION TAB
    # =====================================================

    with registration_tab:

        st.subheader(
            "Create New Account"
        )

        with st.form(
            "registration_form"
        ):

            name = st.text_input(
                "Full Name",
                placeholder="Enter your full name"
            )

            address = st.text_area(
                "Address",
                placeholder="Enter your address"
            )

            phone = st.text_input(
                "Contact Number",
                placeholder="10-digit mobile number",
                max_chars=10
            )

            new_user_id = st.text_input(
                "Set your User ID",
                placeholder="Create a unique User ID"
            )

            new_password = st.text_input(
                "Set your Password",
                type="password",
                placeholder="Create your password"
            )

            confirm_password = st.text_input(
                "Re-enter your Password",
                type="password",
                placeholder="Confirm your password"
            )

            register_button = st.form_submit_button(
                "Create Account",
                type="primary",
                use_container_width=True
            )


        # =================================================
        # REGISTRATION VALIDATION
        # =================================================

        if register_button:

            # ---------------------------------------------
            # Clean input
            # ---------------------------------------------

            name = name.strip().upper()

            address = address.strip().upper()

            phone = phone.strip()

            new_user_id = new_user_id.strip()


            # ---------------------------------------------
            # Name validation
            # ---------------------------------------------

            if not name:

                st.warning(
                    "Please enter your full name."
                )


            # ---------------------------------------------
            # Address validation
            # ---------------------------------------------

            elif not address:

                st.warning(
                    "Please enter your address."
                )


            # ---------------------------------------------
            # Phone validation
            # ---------------------------------------------

            elif (
                len(phone) != 10
                or not phone.isnumeric()
            ):

                st.error(
                    "Enter a valid 10-digit contact number."
                )


            # ---------------------------------------------
            # User ID validation
            # ---------------------------------------------

            elif not new_user_id:

                st.warning(
                    "Please enter a User ID."
                )


            else:

                # -----------------------------------------
                # Check if User ID already exists
                # -----------------------------------------

                user_id_in_db = data_retrieve(
                    new_user_id
                )

                if user_id_in_db:

                    st.error(
                        "User ID already exists. "
                        "Please choose another User ID."
                    )


                # -----------------------------------------
                # Password validation
                # -----------------------------------------

                elif not new_password:

                    st.warning(
                        "Please enter a password."
                    )


                elif new_password != confirm_password:

                    st.error(
                        "Passwords do not match."
                    )


                # -----------------------------------------
                # Create account
                # -----------------------------------------

                else:

                    success = (
                        data_entry_sql_cust_details(
                            name,
                            address,
                            phone,
                            new_user_id,
                            new_password
                        )
                    )

                    if success:

                        st.success(
                            "🎉 Registration Successful!"
                        )

                        st.info(
                            "Your account has been created. "
                            "Please go to the Login tab."
                        )