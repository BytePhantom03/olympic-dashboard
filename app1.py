import mysql.connector
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
# import geopandas as gpd
from matplotlib.pyplot import title, margins
from plotly.graph_objs.bar import Selected


from helper import DB

# Database connection
db = DB()

# Set page configuration
st.set_page_config(
    page_title="Olympic Analytics Dashboard",
    page_icon="🏅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar Menu
st.sidebar.title("Olympic Analytics 🏊")
st.sidebar.markdown("Explore the Olympic Games like never before!")


if "current_page" not in st.session_state:
    st.session_state.current_page = None


user_option = st.sidebar.radio(
    "Menu",
    ["Home", "Check Records", "Analytics", "Geographical Analysis"],
    index=0,
)


if user_option != st.session_state.current_page:
    if user_option == "Check Records":
        st.session_state.search_results = None
    st.session_state.current_page = user_option


# Home Page
if user_option == "Home":
    st.title("Welcome to Olympic Analytics Dashboard 🏆")
    st.markdown(
        """
        ### Discover insights about the Olympic Games with interactive visualizations and analytics tools.

        - 📊 **Search Records**: Find details of participants, sports, and medals.
        - 🌍 **Geographical Analysis**: Explore medal distribution across countries.
        - 🎯 **Analytics**: Dive into data trends and visualizations.

        """
    )

elif user_option == "Check Records":
    st.title("Search for Olympic Records 🔍")


    if "search_results" not in st.session_state:
        st.session_state.search_results = None


    with st.form("search_form"):
        col1, col2 = st.columns(2)
        with col1:
            Years = db.fecth_year()
            Selected_Y = st.selectbox("Select Year", Years, help="Choose the Olympic year.")
        with col2:
            Sports = db.fetch_sport()
            Selected_S = st.selectbox("Select Sport", Sports, help="Choose the sport.")
        submitted = st.form_submit_button("Search")


    if submitted:
        with st.spinner("Fetching results..."):
            year_condition = 0 if Selected_Y == 'All' else int(Selected_Y)
            st.session_state.search_results = db.fecth_all_records(year_condition, Selected_S)


    if st.session_state.search_results is not None:
        filtered_results = st.session_state.search_results

        gender = st.radio("Filter by Gender:", ["Both", "Male", "Female"], index=0, horizontal=True)

        if gender == "Male":
            filtered_results = filtered_results[filtered_results["Sex"] == "M"]
        elif gender == "Female":
            filtered_results = filtered_results[filtered_results["Sex"] == "F"]

        medal = st.radio("Filter by Medal:", ["All", "Gold", "Silver", "Bronze"], index=0, horizontal=True)

        if medal != "All":
            filtered_results = filtered_results[filtered_results["Medal"] == medal]

        if not filtered_results.empty:
            st.success(f"Found {len(filtered_results)} records for Year {Selected_Y} and Sport {Selected_S}.")
            st.dataframe(filtered_results, use_container_width=True)
        else:
            st.warning("No records found for the selected criteria.")


elif user_option == 'Geographical Analysis':
    st.title('Olympic Medals Distribution 🌍')

    df = db.fecth_all_records(0,'All')
    Countries = ['All']

    with st.form("flight_search_form"):
        col1, col2 ,col3 = st.columns(3)
        with col1:
            data =sorted(df['Team'].unique())
            for i in data:
                Countries.append(i)

            Selected_c = st.selectbox(
                "Select Country", Countries, help="Choose the country of the Olympic."
            )
        with col2:
            Years = db.fecth_year()
            Selected_y = st.selectbox(
                "Select Year", Years, help="Choose the year of the Olympic event."
            )
        with col3:
            Sports = db.fetch_sport()
            Selected_s = st.selectbox(
                "Select Sport", Sports, help="Choose the sport."
            )

        submitted = st.form_submit_button("Search")


    if submitted:

        Medals = db.fetch_all_geographic_records(Selected_c, Selected_y, Selected_s)

        if not Medals.empty:
            Medals["Medal Range"] = pd.cut(
                Medals["Medal Count"],
                bins=[0, 100, 300, 700, 1500, 6000],
                labels=["0-100", "100-300", "300-700", "700-1500", "1500+"]
            )

            fig = px.choropleth(
                Medals,
                locations="Team",
                locationmode="country names",
                color="Medal Range",
                hover_data={"Medal Count": True},
                title='Country Wise',
                color_continuous_scale=[
                    (0.0, "blue"),
                    (0.2, "lightblue"),
                    (0.4, "green"),
                    (0.6, "yellow"),
                    (0.8, "orange"),
                    (1.0, "red")
                ]
            )

            fig.update_layout(
                title_font_size=24,
                title_x=0.4,
                margin={"r": 0, "t": 50, "l": 0, "b": 0},
                height=600,
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning(
                f"{Selected_c} has not won any medals in {Selected_s} during {Selected_y}."
            )



else:
    st.title('All Over Analysis')
    st.markdown("<h1 style='font-size:24px;'>Country Wise Medal Distribution</h1>", unsafe_allow_html=True)


    team , total = db.fetch_country_distribution()

    fig_pie = go.Figure(
        go.Pie(
            labels=team,
            values=total,
            hoverinfo="value+percent",
            textinfo="label",
        )
    )


    st.plotly_chart(fig_pie, use_container_width=True)


    selected_C = st.selectbox('Select Country',sorted(db.fecth_all_country()))

    b1 = st.button('Analyze')

    if b1:
        all_male = db.fecth_all_male(selected_C,'M')
        A_male = all_male[0][0] if all_male else 0

        all_female = db.fecth_all_male(selected_C,'F')
        A_female = all_female[0][0] if all_female else 0

        W_male = db.fecth_all_played(selected_C,'M')
        W_male = W_male[0][0] if W_male else 0

        W_female = db.fecth_all_played(selected_C,'F')
        W_female = W_female[0][0] if W_female else 0

        if A_male == 0 and A_female == 0:
            st.warning("No participants found for the selected criteria.")
        else:
            categories = ["Males", "Females"]
            all_values = [A_male, A_female]
            winner_values = [W_male, W_female]

            fig_bar = go.Figure()

            fig_bar.add_trace(
                go.Bar(
                    x=categories,
                    y=all_values,
                    name="All Participants",
                    marker_color="blue",
                    text=all_values,
                    textposition="outside",
                )
            )
            fig_bar.add_trace(
                go.Bar(
                    x=categories,
                    y=winner_values,
                    name="Winners",
                    marker_color="green",
                    text=winner_values,
                    textposition="outside",
                )
            )
            fig_bar.update_layout(
                title={
                    "text": "Male and Female Participants vs Winners",
                    "font": {"size": 24},
                },
                xaxis_title="Gender",
                yaxis_title="Count",
                barmode="group",
                title_x=0.3,
                template="plotly_white",
                height=500,
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    year, medal = db.fecth_year_medal()
    fig_line = go.Figure(
        go.Scatter(
            x=year,
            y=medal,
            mode="lines+markers",
            line=dict(color="royalblue", width=2),
            marker=dict(size=8, color="lightblue"),
        )
    )
    fig_line.update_layout(
        title={
        "text": "Year Wise Medal Distribution",
        "x": 0.35,
        "font": {"size": 24},
        },
        xaxis_title="Year",
        yaxis_title="Toatl Medal",
        title_x=0.35,
        font=dict(family="Arial, sans-serif", size=14),
    )
    st.plotly_chart(fig_line, use_container_width=True)

    data = pd.DataFrame(db.fecth_top_athelet())

    fig = px.bar(
        data,
        x="Total",
        y="Name",
        orientation="h",  # Horizontal bars
        color="Total",
        text="Total",
        color_continuous_scale="Viridis",
    )
    fig.update_layout(
        xaxis_title="Total Medals",
        yaxis_title="Athletes",
        title={
            "text": "Top 8 Athletes by Total Medals",
            "x": 0.3,
            "font": {"size": 24},
        },
        title_x=0.35,
        template="plotly_white",
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)

























