import streamlit as st
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


### Config
st.set_page_config(
    page_title="getaroundanalysis",
    layout="wide"
)

DATA_URL = 'https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_delay_analysis.xlsx'
### App
st.title("GetAround Delay Analysis")

st.image("https://lever-client-logos.s3.amazonaws.com/2bd4cdf9-37f2-497f-9096-c2793296a75f-1568844229943.png")

st.markdown("""
    Welcome to this dashboard ! 

    🚧 When using Getaround, drivers book cars for a specific time period, from an hour to a few days long. They are supposed to bring back the car on time, but it happens from time to time that drivers are late for the checkout.
    Late returns at checkout can generate high friction for the next driver if the car was supposed to be rented again on the same day : Customer service often reports users unsatisfied because they had to wait for the car to come back from the previous rental or users that even had to cancel their rental because the car wasn’t returned on time. 

    🎯The goal of this dashboard is to determine a minimum delay between two rentals or at least give some hint on the trade-off of minimum delay. A car won’t be displayed in the search results if the requested checkin or checkout times are too close from an already booked rental.
      It solves the late checkout issue but also potentially hurts Getaround/owners revenues: we need to find the right trade off.

    By examining historical data gathered on the GetAround app we will try to answer these questions : 

    * How often are drivers late for the next check-in? How does it impact the next driver?
    * Which share of our owner’s revenue would potentially be affected by the feature?
    * How many rentals would be affected by the feature depending on the threshold and scope we choose?
    * How many problematic cases will it solve depending on the chosen threshold and scope?
""")

st.caption('a caption')

st.markdown("---")


# Use `st.cache` when loading data is extremly useful
# because it will cache your data so that your app
# won't have to reload it each time you refresh your app
@st.cache
def load_data():
    data = pd.read_excel(DATA_URL)
    return data

st.text('Load data ...')

data_load_state = st.text('Loading data ...')
data = load_data()
data_load_state.text("") # change text from "Loading data..." to "" once the the load_data function has run

## Run the below code if the check is checked ✅
if st.checkbox('Show raw data'):
    st.header('Raw data')
    st.write(data)


st.header('Dataset overview')

fig1 = px.histogram(data_frame=data,
        x='delay_at_checkout_in_minutes',
        color='checkin_type',
        histnorm='percent',
        barmode='overlay')

fig2 = px.histogram(data_frame=data,
        x='time_delta_with_previous_rental_in_minutes',
        color='checkin_type',
        nbins=100,
        histnorm='percent',
        barmode='overlay')

st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("Users choosing the mobile rental agrement return the car later than the ones using the connect agrement. This is not very suprising because in a mobile rental the owner can also be late for checkin/checkout.")


st.header('How long should the minimum delay be ?')

data = data.dropna(subset=["time_delta_with_previous_rental_in_minutes", "delay_at_checkout_in_minutes"])
data_test = pd.melt(data, id_vars=['car_id', 'rental_id', 'state', 'checkin_type'], value_vars=['time_delta_with_previous_rental_in_minutes', 'delay_at_checkout_in_minutes'])

st.metric(label="car fleet", value=data_test['car_id'].nunique())

fig5 = px.pie(data, values="time_delta_with_previous_rental_in_minutes", names='checkin_type')

st.plotly_chart(fig5, use_container_width=True)

fig3 = px.ecdf(
    data_test[data_test['checkin_type']=='mobile'],
    x='value',
    color='variable',
    ecdfnorm= 'percent',
    range_x=[0, 800],
    labels={"value":'threshold (minutes)', "percent":'proportion of users (%)'}
    )

fig4 = px.ecdf(
    data_test[data_test['checkin_type']=='connect'],
    x='value',
    color='variable',
    ecdfnorm= 'percent',
    range_x=[0, 800],
    labels={"value":'threshold (minutes)', "percent":'proportion of users (%)'}
    )
    ##labels={"delay_at_checkout_in_minutes":'threshold (minutes)', "time_delta_with_previous_rental_in_minutes":'threshold (minutes)'}

##fig4 = px.ecdf(
##    data,
##    x="time_delta_with_previous_rental_in_minutes",
##    color="checkin_type",
##    ecdfnorm= 'percent',
##    range_x=[0, 800],
##    labels={"time_delta_with_previous_rental_in_minutes":'threshold (minutes)'}
##    )

##st.plotly_chart(fig3, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Mobile")
    st.plotly_chart(fig3, use_container_width=True)

with col2:
   st.subheader("Connect")
   st.plotly_chart(fig4, use_container_width=True)

st.markdown("These plots are Cumulative Distribution Function (ECDF), it allow us to show the percentage of users impacted by the introduction of a threshold for minimum time delay")
st.markdown("For example, if the threshold is set at 60 min : 30% of the potential drivers are lost for the car owner (30% of the owners revenue is lost), but 70% of late return cases is solved. We are missing one information here : the number of cancelations avoided by the owner due to the augmentation of the threshold.")
st.markdown("The threshold sould be lower for connect cars because there is much less late return.")