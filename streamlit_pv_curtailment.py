#Moix P-O
#www.albedo-engineering.com 2025
#v0.1

#to run the app: streamlit run streamlit_pv_curtailment.py

import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import datetime
#import random as rnd

#home made import:

from solarsystem import *

PV_POWER_INSTALLED = 9.5 #kWp

st.set_page_config(page_title="Albedo Engineering, PV clipping", page_icon='❄️',layout="wide")

# Title
st.title("🌞✂️ PV production curtailment study")


### Create sidebar with the options for simulation
# with st.sidebar:

#     st.title("Simulation Parameters")

#     st.write("⏱️📈 Planification with simple charge and discharge setpoint")

#     threshold_discharge = st.slider("⚡ Discharge when energy is expensive above (CHF/kWh): ", min_value=0.0, max_value=0.5, value=0.25, step=0.01)
#     threshold_charge  = st.slider("⚡ Charge when energy is cheap below (CHF/kWh): ", min_value=0.0, max_value=0.5, value=0.17, step=0.01)
#     st.write("between those levels nothing happens")

#     st.markdown("---")

#     st.write("🔋 Storage used for simulation")
#     battery_size_kwh = st.slider("Battery capacity (kWh): ", min_value=1.0, max_value=20.0, value=10.0, step=1.0)
#     battery_charge_power_kw = st.slider("Battery max charge power (kW): ", min_value=1.0, max_value=20.0, value=10.0, step=1.0)
#     st.write("C/2 would be a reasonable charge/discharge limit, note it is applied all day")

#     st.markdown("---")
#     st.write("✌️ Moix P-O, 2025")
#     st.write("I explored streamlit. Nice! Quite easily put in place for simple interactive dashboards...")



st.write(""" Visualizing the effect PV power injection limitation with the data of a real installation and quantifing the lost production.
    - **Why?** With today increase rate of PV production capacity, there will be so much production in the afternoon that the way we consume must be adapted but also the way we produce. Honestly, do you believe we can install 30GW of solar when there is 8GW of consumption in Switzerland and not manage it more than today?
    - **More Info?** Play with this website --> [production and consumption of Switzerland](https://www.energy-charts.info/charts/power/chart.htm?l=en&c=CH) and try to imagine 4 times more solar than today. Even in november there must be management performed.
    
    Live with the sun... adapt to the new world """)

# Create three columns
col1, col2, col3 = st.columns([1, 2, 1])
# Display the image in the center column
with col2:
    st.image("curtailment roots.jpg", caption="Something will happen...", width=500)

# st.image("curtailment roots.jpg", 
#          caption="Something will happen...", 
#          width=500)

# st.markdown(
#     """
#     <div style="text-align: center;">
#         <img src="curtailment roots.jpg" width="500">
#         <p>Something will happen...</p>
#     </div>
#     """,
#     unsafe_allow_html=True
# )


st.markdown("---")

st.subheader(" 🪓 Curtailment input ")

st.write("Historical data used for simulation is of a 9.5kWp installation, cut to 50% will limit to 4.25kW")
solar_scale = st.slider("🪓 Peak production shaving to (%): ", min_value=0.0, max_value=100.0, value=70.0, step=1.0)

st.markdown("---")




# Load Data
df_pow_profile = pd.read_csv("15min_pow_2024.csv")

# Ensure 'Time' is a DateTime type#
df_pow_profile["Time"] = pd.to_datetime(df_pow_profile["Time"])


#take the data of the power profile with the same length as the simulation
pow_array_all = df_pow_profile["15min mean System Pout Consumption power (ALL) [kW]"].to_numpy()
solar_array_all = df_pow_profile["15min mean Solar power (ALL) [kW]"].to_numpy()

#Add the column to the dataframe:
#df_price_varioplus["Consumption"] = pow_array 
consumption_kWh = df_pow_profile["15min mean System Pout Consumption power (ALL) [kW]"].sum()/4.0
production_kWh = df_pow_profile["15min mean Solar power (ALL) [kW]"].sum()/4.0



length_profile = len(df_pow_profile.index)
clipping_level = solar_scale*PV_POWER_INSTALLED/100.0
clipping_level_profile = np.ones(length_profile)* clipping_level
df_pow_profile["Clipping level"] = clipping_level_profile

#Make the clipping:
df_pow_profile["Clipped production"] = solar_array_all
df_pow_profile["Clipped production"] = df_pow_profile["Clipped production"].clip(upper=clipping_level)
df_pow_profile["lost production"] = df_pow_profile["15min mean Solar power (ALL) [kW]"]-df_pow_profile["Clipped production"]

clipped_production_kWh = df_pow_profile["Clipped production"].sum()/4.0
clipping_losses = (production_kWh-clipped_production_kWh)/production_kWh
clipping_losses2 = df_pow_profile["lost production"].sum()/4.0/production_kWh

print("----> losses: ", clipping_losses, clipping_losses2)

st.subheader("Case 1: stop the production at PV DC stage ")
st.write("The production is capped to the wanted level directly after the modules. ")

col1, col2 = st.columns(2)
col1.metric("Original Prod", str(int(production_kWh))+" kWh", "100%", delta_color="off")
col2.metric("Prod with clipping ", str(int(clipped_production_kWh))+" kWh", f"{-clipping_losses*100 :.1f}"+"%")



#resampling at hours with mean of power to retrieve kWh:
# Use time as index
df_pow_profile = df_pow_profile.set_index("Time")
hours_mean_df = df_pow_profile.resample('h', label="right", closed="right").mean() 

daily_summary = hours_mean_df.resample('d', label="right", closed="right").sum() 
monthly_summary = hours_mean_df.resample('ME', label="right", closed="right").sum() 


# # For grouping, add a date and a month indication: 

# df_pow_profile['Date'] = df_pow_profile.index.dt.date
# df_pow_profile['YearMonth'] = df_pow_profile.index.dt.to_period('M')
# df_pow_profile['Date'] = df_pow_profile['Time'].dt.date
# df_pow_profile['YearMonth'] = df_pow_profile['Time'].dt.to_period('M')
# #make regrouping:
# daily_summary = hours_mean_df.groupby('Date').sum(numeric_only=True)
# daily_summary = daily_summary.reset_index()

# #daily_summary["Energy lost"] = 

# #monthly_daily_summary = 
# monthly_summary = hours_mean_df.groupby('YearMonth').sum(numeric_only=True)
# monthly_summary = monthly_summary.reset_index()
# monthly_summary['YearMonth'] = monthly_summary['YearMonth'].astype(str)
# monthly_summary['MonthName'] = pd.to_datetime(monthly_summary['YearMonth']).dt.strftime('%B')

#'Date' is currently a date object, convert it to datetime
#daily_summary['Date'] = pd.to_datetime(daily_summary['Date']) 


st.write("""Let's see below the simulation on an real PV installed on a house : """)


# Combined Solar Power and Energy Consumption Plot using Plotly
if "15min mean System Pout Consumption power (ALL) [kW]" in df_pow_profile.columns:
    fig_combined = px.line(df_pow_profile, x=df_pow_profile.index, 
                            y=["15min mean Solar power (ALL) [kW]", "Clipping level", "Clipped production"], 
                            title="🌞 Solar Production and clipping level", 
                            labels={"value": "Power (kW)", "variable": "Legend"},
                            color_discrete_sequence=["lightcoral", "lightblue", "lightgreen"] )
    
    # Move legend below the graph
    fig_combined.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,  # Position below the graph
            xanchor="center",
            x=0.1
        )
    )
    st.plotly_chart(fig_combined)

    #st.dataframe(monthly_summary.head())


    fig_day = px.line(daily_summary, 
                            x=daily_summary.index, 
                            y=["15min mean Solar power (ALL) [kW]", "Clipped production","lost production"], 
                            title="Daily Solar Production without and with clipping", 
                            labels={"value": "Production (kWh per day)", "variable": "Legend"},
                            color_discrete_sequence=["lightcoral", "lightblue", "gray"] )
    
    # Move legend below the graph
    fig_day.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,  # Position below the graph
            xanchor="center",
            x=0.1
        )
    )
    st.plotly_chart(fig_day)

    fig_month = px.bar(monthly_summary, 
                            x=monthly_summary.index,  
                            y=["15min mean Solar power (ALL) [kW]", "Clipped production","lost production"], 
                            title="Production loss per month", 
                            labels={"value": "Energy (kWh)", "variable": "Legend"},
                            color_discrete_sequence=["lightcoral", "lightblue", "gray"],
                            barmode = 'group')
    
    # # Move legend below the graph
    # fig_month.update_layout(
    #     legend=dict(
    #         orientation="h",
    #         yanchor="top",
    #         y=-0.2,  # Position below the graph
    #         xanchor="center",
    #         x=0.1
    #     )
    # )
    st.plotly_chart(fig_month)






# st.markdown("---")
# st.markdown("---")

# # # Show dataset preview
# st.title("📋 **Data Overview, for debug purpose**")
# st.dataframe(df_pow_profile.head())

# st.dataframe(df_pow_profile.tail())







st.markdown("---")
st.subheader("Case 2: limit the gridfeeding at house introduction, allow the production for selfconsumption")
st.write("""Let's see below the simulation on an real PV installed on a house with its load profile : 
         Here the limitation is on the injected power only, the self consumption is not modified.
         That is the case described by the VSE-AES for Switzerland in [Recommandation de la branche: Directive relative à l’ajustement de l’injection des installations photovoltaïques au service du réseau](https://www.strom.ch/fr/media/15570/download) """
        )            








#Make the clipping:
df_pow_profile["grid power"] = pow_array_all-solar_array_all #all grid balance


    
# Replace all positive values with 0
df_pow_profile["grid injection only"] = -df_pow_profile["grid power"].mask(df_pow_profile["grid power"] > 0, 0.0)

df_pow_profile["grid clipped injection"] = df_pow_profile["grid injection only"].clip(upper=clipping_level)






injection_kWh = df_pow_profile["grid injection only"].sum()/4.0

clipped_injection_kWh = df_pow_profile["grid clipped injection"].sum()/4.0
clipping_losses_injection=(injection_kWh-clipped_injection_kWh)/injection_kWh



col1, col2 = st.columns(2)
col1.metric("Original Injection", str(int(injection_kWh))+" kWh", "100%", delta_color="off")
col2.metric("Injection with clipping ", str(int(clipped_injection_kWh))+" kWh", f"{-clipping_losses_injection*100 :.1f}"+"%")






# Combined Solar Power and Energy Consumption Plot using Plotly
if "15min mean System Pout Consumption power (ALL) [kW]" in df_pow_profile.columns:
    fig_combined = px.line(df_pow_profile, x=df_pow_profile.index, 
                            y=["15min mean Solar power (ALL) [kW]", "15min mean System Pout Consumption power (ALL) [kW]"], 
                            title="ORIGINAL DATA 🌞 Solar Production vs ⚡ Energy Consumption", 
                            labels={"value": "Power (kW)", "variable": "Legend"},
                            color_discrete_sequence=["lightcoral", "lightblue"] )
    
    # Move legend below the graph
    fig_combined.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,  # Position below the graph
            xanchor="center",
            x=0.1
        )
    )
    st.plotly_chart(fig_combined)




#st.dataframe(df_pow_profile.head())


fig_combined = px.line(df_pow_profile, x=df_pow_profile.index, 
                        y=["grid injection only", "grid clipped injection", "Clipping level"], 
                        title="grid injection and caping", 
                        labels={"value": "Power (kW)", "variable": "Legend"},
                        color_discrete_sequence=["lightcoral", "lightblue"] )

# Move legend below the graph
fig_combined.update_layout(
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.2,  # Position below the graph
        xanchor="center",
        x=0.1
    )
)
st.plotly_chart(fig_combined)


st.markdown("---")
st.subheader("Case 3: limit the gridfeeding and use storage")
st.write("""The storage is normally quite dumb: it charges as soon as there is solar excess and discharge as soon as there is more consumption than production. This is something that must evolve in the future, else it will not help the grid much. """)

st.markdown("<span style='color:red'><b> Smart Charging Simulation TODO, come back later </b></span>", unsafe_allow_html=True)




st.markdown("---")

st.subheader(" A short summary ")
st.write("""With those data, the loss due to curtailment is given below. With curtailment at the house introduction, the selfconsumption of 2150kWh per year is saved""")


# Create three columns
col1, col2, col3 = st.columns([1, 2, 1])
# Display the image in the center column
with col2:
    st.image("results.jpg", caption="what to expect with curtailment...")
