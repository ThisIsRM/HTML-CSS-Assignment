import streamlit as st
import pyrebase
import re
from streamlit_option_menu import option_menu
import json
from pprint import pprint
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import random
import string
import pyperclip

# Streamlit Imp Variables
st.set_page_config(page_title = 'TEST ENVT', page_icon = '⛔', layout = 'wide')

# Firebase Configuration Key
firebaseConfig = {
    'apiKey': "AIzaSyDsY0-hfeVI2roagdIlzERYUWEHHDTAPF0",
    'authDomain': "bikebuddy0118.firebaseapp.com",
    'projectId': "bikebuddy0118",
    'databaseURL': "https://bikebuddy0118-default-rtdb.europe-west1.firebasedatabase.app/",
    'storageBucket': "bikebuddy0118.appspot.com",
    'messagingSenderId': "899355751515",
    'appId': "1:899355751515:web:b9c611f8645eec9c8ebb7e",
    'measurementId': "G-2TS8BDR3S0"
}

# Firebase Authentication
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# Database
db = firebase.database()
storage = firebase.storage()

# Streamlit Session State Control
if "user_status" not in st.session_state:
    st.session_state['user_status'] = 'logged_out'

if "user_id" not in st.session_state:
    st.session_state['user_id'] = None

# Function to load local CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Define a regular expression pattern for a basic email validation
def is_valid_email(email):
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_pattern, email) is not None

# Define criteria for password validation
def is_valid_password(password):
    return len(password) >= 7

# Login and Sign Up Form
def userauth():
    st.sidebar.title("BikeBuddy")
    st.sidebar.empty()

    if st.session_state['user_status'] == "logged_out":
        choice = st.sidebar.selectbox("Login/Sign Up", ['Login', 'Sign Up'])
       
        # Login
        if choice == "Login":
            email = st.sidebar.text_input("E-Mail")
            password = st.sidebar.text_input("Password", type="password")
            submit = st.sidebar.button("Login")
           
            if submit and is_valid_email(email) and is_valid_password(password):
                try:
                    user = auth.sign_in_with_email_and_password(email, password)
                    if user:
                        st.session_state['user_id'] = user

                    username = db.child(user['localId']).child("username").get().val()
                    st.title("Welcome, " + username)

                    # Hide the sidebar after successful login
                    st.markdown(
                        """
                        <style>
                        section[data-testid="stSidebar"][aria-expanded="true"]{
                            display: none;
                        }
                        </style>
                        """,
                        unsafe_allow_html=True,
                    )
                    return "logged_in"
                except Exception as e:
                    print("\n\n-->", e)
                    st.warning("Incorrect Email or Password.")
       
        # Sign Up
        elif choice == "Sign Up":
            name = st.sidebar.text_input("Full Name")
            email = st.sidebar.text_input("E-Mail")
            username = st.sidebar.text_input("Username")
            password = st.sidebar.text_input("Password", type="password")
            age = st.sidebar.number_input("Age", min_value=18, step=1)
            blood_types = ['Select', 'A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
            blood_group = st.sidebar.selectbox("Blood Group", blood_types)
            mob_number = st.sidebar.text_input("Mobile Number")
            submit = st.sidebar.button("Sign Up")
           
            if submit:
                try:
                    user = auth.create_user_with_email_and_password(email, password)

                    db.child(user['localId']).child("name").set(name)
                    db.child(user['localId']).child("email").set(email)
                    db.child(user['localId']).child("username").set(username)
                    db.child(user['localId']).child("password").set(password)
                    db.child(user['localId']).child("age").set(age)
                    db.child(user['localId']).child("blood_group").set(blood_group)
                    db.child(user['localId']).child("mob_number").set(mob_number)
                    db.child(user['localId']).child("ID").set(user['localId'])

                    st.success("Your account has been created successfully. Go ahead and log in.")
                    user = auth.sign_in_with_email_and_password(email, password)
                    if user:
                        st.session_state['user_id'] = user

                    st.info("Welcome, " + username)
                except Exception as e:
                    pass
    return "logged_out"

#! ---> runapp() is calling the below modules
def check_log(widgets_list):
    for i in widgets_list:
        if i == "":
            st.warning("Fill the missing fields")
            return False
    return True

def ride_code_generator():
    length = 6
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def tab1_content():
    col1, col2, col3 = st.columns([1.5, 1, 3])

    with col1:
        st.subheader('Log your ride details here.')
        ride_name = st.text_input('Ride Name')
        starting_loc = st.text_input('Starting Point')
        destination_loc = st.text_input('Destination')
        ride_date = st.date_input('Date', format = 'DD/MM/YYYY')
        fuel = st.slider('Petrol in tank', min_value=0.5, max_value = 15.0, step = 0.5)
        petrol_exp = st.number_input('Petrol Expenditure', step = 1)
        start_odo = st.number_input('Starting Odometer', step = 1)
        end_odo = st.number_input('Ending Odometer', step = 1)
        with st.expander('More...'):
            other_exp = st.number_input('Misc. Expenses', step = 1)

        widgets_list = [ride_name, starting_loc, destination_loc, ride_date, fuel, petrol_exp, start_odo, end_odo]
        log_btn = st.button('Log Details')
        if log_btn:
            log_status = check_log(widgets_list)
            if log_status:
                #! feed details in firebase
                #! feed details in firebase
                #! feed details in firebase
                ride_date = json.dumps(ride_date.isoformat())
                ride_log = {
                    'Starting_Location' : starting_loc,
                    'Destination_Location' : destination_loc,
                    'Ride_Date' : ride_date,
                    'Fuel' : fuel,
                    'Petrol_Expense' : petrol_exp,
                    'Start Odometer' : start_odo,
                    'End Odometer' : end_odo,
                    'Other Expense' : other_exp
                }
                user = st.session_state['user_id']
                db.child(user['localId']).child("Rides").child(ride_name).set(ride_log)
                st.success('Your Ride Details have been logged.', icon="✅")

    with col2:
        st.empty()

    with col3:
        # can display some image here
        st.subheader('Log sheet preview.')
        st.divider()
        st.write("\n")
        st.write("💠 Ride Name: ", ride_name)
        st.write("💠 Starting Point: ", starting_loc)
        st.write("💠 Destination: ", destination_loc)
        st.write("💠 Date: ", ride_date)
        st.write("💠 Fuel in Tank: ", fuel, "Ltrs." )
        st.write("💠 Fuel Expense: ₹", petrol_exp)
        st.write("💠 Starting Odometer Reading: ", start_odo, "Kms")
        st.write("💠 Ending Odometer Reading: ", end_odo, "Kms")
        st.write("💠 Total Distance: ", end_odo - start_odo, "Kms")
        st.write("💠 Other Expenses: ₹", other_exp)
       
def tab2_content():
    st.subheader('All your previous Rides, well documented.')
    st.write("\n")
    col1, col2, col3 = st.columns([1.5, 0.2, 3])
   
    user = st.session_state['user_id']

    total_petrol_expense = []
    all_ride_names = []
    total_distance_travelled = []
    all_start_odometer = []
    all_end_odometer = []
    total_other_expense = []
    with col1:
        rides = db.child(user['localId']).child("Rides").get().val()
        rides_list = list(rides.items())

        for ride in rides_list:
            with st.expander(ride[0]):
                st.write("💠 Starting Point: ", ride[1]['Starting_Location'])
                st.write("💠 Destination: ", ride[1]['Destination_Location'])
                st.write("💠 Date: ", ride[1]['Ride_Date'])
                st.write("💠 Fuel in Tank: ", ride[1]['Fuel'], "Ltrs." )
                st.write("💠 Fuel Expense: ₹", ride[1]['Petrol_Expense'])
                st.write("💠 Starting Odometer Reading: ", ride[1]['Start Odometer'], "Kms")
                st.write("💠 Ending Odometer Reading: ", ride[1]['End Odometer'], "Kms")
                st.write("💠 Total Distance: ", ride[1]['End Odometer'] - ride[1]['Start Odometer'], "Kms")
                st.write("💠 Other Expenses: ₹", ride[1]['Other Expense'])

    with col2:
        st.empty()
   
    with col3:
        tab1, tab2, tab3, tab4 = st.tabs(["Fuel Expenses", "Distance Travelled", "Odometer Readings", "All Expenses"])

        with tab1:
            st.header("Fuel Expenses")
            st.write('\n\n\n')
            rides = db.child(user['localId']).child("Rides").get().val()
            rides_list = list(rides.items())

            for ride in rides_list:
                all_ride_names.append(ride[0])
                total_petrol_expense.append(ride[1]['Petrol_Expense'])
           
            chart_data = pd.DataFrame(
                {
                    "Ride Name" : all_ride_names,
                    "Petrol Cost in ₹" : total_petrol_expense
                }
            )
            st.bar_chart(chart_data, x="Ride Name", y="Petrol Cost in ₹")

        with tab2:
            st.header("Distance Travelled - A Bar Graph")
            st.write('\n\n\n')
            rides = db.child(user['localId']).child("Rides").get().val()
            rides_list = list(rides.items())

            for ride in rides_list:
                total_distance_travelled.append(ride[1]['End Odometer'] - ride[1]['Start Odometer'])

            chart_data = pd.DataFrame(
                {
                    "Ride Name" : all_ride_names,
                    "Distance in Kms" : total_distance_travelled
                }
            )
           
            st.bar_chart(chart_data, x="Ride Name", y="Distance in Kms", color = '#BEADFA')

            # Create a pie chart using Plotly Express
            st.header("Distance Travelled - A Pie Chart")
            fig = px.pie(names = all_ride_names, values = total_distance_travelled)
            st.plotly_chart(fig, use_container_width = True)

        with tab3:
            st.header("Odometer Readings")
            rides = db.child(user['localId']).child("Rides").get().val()
            rides_list = list(rides.items())

            for ride in rides_list:
                # all_ride_names.append(ride[0])
                all_start_odometer.append(ride[1]['Start Odometer'])
                all_end_odometer.append(ride[1]['End Odometer'])
           
            data = pd.DataFrame({
                'Ride Name': all_ride_names,
                'Start Odometer': all_start_odometer,
                'End Odometer': all_end_odometer
                })

            # Create a grouped bar chart using Plotly
            fig = go.Figure(data=[
                go.Bar(name='Start Odometer', x = data['Ride Name'], y = data['Start Odometer']),
                go.Bar(name='End Odometer', x = data['Ride Name'], y = data['End Odometer'])
            ])

            fig.update_layout(barmode='group', xaxis_tickangle=0)

            # Reduce the y-axis unit to 10,000
            y_max = max(data[['Start Odometer', 'End Odometer']].max())
            y_tick_values = list(range(0, int(y_max) + 10000, 10000))
            fig.update_yaxes(range=[0, y_max + 10000], tickvals=y_tick_values)

            st.plotly_chart(fig, use_container_width=True)
       
        with tab4:
            st.header("All Expenses")
            rides = db.child(user['localId']).child("Rides").get().val()
            rides_list = list(rides.items())

            for ride in rides_list:
                # all_ride_names.append(ride[0])
                total_other_expense.append(ride[1]['Other Expense'])
           
            data = pd.DataFrame({
                'Ride Name': all_ride_names,
                'Petrol Expense' : total_petrol_expense,
                'Other Expense' : total_other_expense
            })

            # Create a grouped bar chart using Plotly
            fig = go.Figure(data=[
                go.Bar(name='Petrol Expense', x=data['Ride Name'], y=data['Petrol Expense']),
                go.Bar(name='Other Exoense', x=data['Ride Name'], y=data['Other Expense'])
            ])

            fig.update_layout(barmode='group', xaxis_tickangle=0)

            # Reduce the y-axis unit to 500
            y_max = max(data[['Petrol Expense', 'Other Expense']].max())
            y_tick_values = list(range(0, int(y_max) + 500, 500))
            fig.update_yaxes(range=[0, y_max + 500], tickvals=y_tick_values)

            st.plotly_chart(fig, use_container_width=True)



def tab3_content():
    st.subheader('Join your fellow riders from the Motorcycling Community.')

    col1, col2, col3 = st.columns([2, 0.1, 2])

    with col1:
        with st.expander('Create a Ride'):
            st.write("Lets's get started.")
            ride_name = st.text_input('Ride Name')
            creator = st.text_input('Created By')
            starting_loc = st.text_input('Starting Point')
            destination_loc = st.text_input('Destination')
            ride_date = st.date_input('Date', format = 'DD/MM/YYYY')
            approx_expense = st.number_input('Approx. Expenses', step = 100)
            ride_desc = st.text_area('Description (if any)')
            ride_code = ride_code_generator()

            create_ride = st.button('Create a new ride')
            if create_ride:
                ride_date = json.dumps(ride_date.isoformat())
                ride_details = {
                    'Created_By' : creator,
                    'Starting_Location' : starting_loc,
                    'Destination_Location' : destination_loc,
                    'Ride_Date' : ride_date,
                    'Approx_Expense' : approx_expense,
                    'Ride_Description' : ride_desc,
                    'Ride_Code' : ride_code
                }
               
                user = st.session_state['user_id']
                db.child(user['localId']).child("Created Rides").child(ride_name).set(ride_details)
                st.toast('A ride has been created succesfully!', icon='✅')
               
                subcol1, subcol2 = st.columns([1, 2])
                with subcol1:
                    body = 'Your Ride Code: ' + ride_code
                    st.info(body)
                with subcol2:
                    # Create a button to copy the code to the clipboard
                    copy_code_button = st.button('Copy Ride Code to Clipboard', key="copy_code")

                # Add a condition to display the success message
                if copy_code_button:
                    # Copy the ride code to the clipboard
                    pyperclip.copy(ride_code)
                    st.success('Ride Code copied.', icon="📋")

   
    with col2:
        st.empty()

    with col3:
        join_btn = st.button('Join A Ride', use_container_width=True)
        if join_btn:
            st.write('Join us mate!')
               
def tab4_content():
    st.subheader('All your important documents, stored away safe and secure.')


def runapp():
    # After Login and Sign Up
    # st.sidebar.title("BikeBuddy")
    if st.session_state['user_status'] == "logged_in": # which means user is logged in
        options = ["Ride Log", "My Rides", "Create/Join a Ride", "Your Documents"]
        icons = ["book", "person-check", "plus-circle", "files"]
        nav_item = option_menu(
            menu_title = "BikeBuddy",
            options = options,
            icons = icons,
            menu_icon = "wrench-adjustable",
            orientation = "horizontal"
        )
     
        if nav_item == "Ride Log":
            tab1_content()
        if nav_item == "My Rides":
            tab2_content()
        if nav_item == "Create/Join a Ride":
            tab3_content()
        if nav_item == "Your Documents":
            tab4_content()

# ---------> Webapp entry point
if __name__ == "__main__":
    local_css("css/style.css")
    if st.session_state['user_status'] == "logged_out":
        # After successful login, change the session_state to "logged_in"
        print('before userauth(): ', st.session_state['user_status'])
        st.session_state['user_status'] = userauth() # should return "logged_in"
        print('after userauth(): ', st.session_state['user_status'])
   
    if st.session_state['user_status'] == "logged_in":
        runapp()
