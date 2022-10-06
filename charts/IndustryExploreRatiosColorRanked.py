import pandas as pd
from tools import error_email, export_gs_func, kpi_mapping, kpi_remove, extract_industry_pickle
import streamlit as st
import plotly.express as px  # pip install plotly-express
import plotly.graph_objects as go
import numpy as np

# #################################################################################################
# ####### Ratios by industries ####################################################################
# #################################################################################################
# python -c 'from test import ratios_by_industry; ratios_by_industry()'


def Industry_Explore_Ratios_Color_Ranked():

    # df = pd.read_pickle('data/eq_daily_industry.pickle')
    df = extract_industry_pickle()

    last_recorded_datetime = df['daily_agg_record_time'].min().strftime("%b %d %Y %H:%M:%S")

    cols = df.columns.values.tolist()
    #remove unwanted kpis
    cols = [i for i in cols if i not in kpi_remove]
    cols.remove("industry")

    # st.write('\n')
    # st.markdown('---')

    col1, col2, col3 = st.columns(3)

    with col1:

        options = st.radio('Select data to display:', ['All', 'Top 50', 'Bottom 50'], horizontal=True)
        # Navigation options
        if options == 'All':
            result = "All"
        elif options == 'Top 50':
            result = "Top_50"
        elif options == 'Bottom 50':
            result = "Bottom_50"


    with col2:
        selected_kpi1 = st.selectbox(
            'Select a primary financial ratio (Bar)',
            tuple(cols),
            index=0,
        )


    with col3:
        selected_kpi2 = st.selectbox(
            'Select a secondary financial ratio (Color)',
            tuple(cols),
            key = "ind_IndustryExploreRatiosColorRanked",
            index=1
        )


    df = df[['industry', selected_kpi1, selected_kpi2]]

    try:

        # Determine if the ratio is postive or negative
        if kpi_mapping[selected_kpi1] == True:
            df_grouped = df.sort_values(by=[selected_kpi1], ascending=True )
        else:
            df_grouped = df.sort_values(by=[selected_kpi1], ascending=False )


        if result == "Bottom_50":
            df_grouped = df_grouped.head(50)
        elif result == "Top_50":
            df_grouped = df_grouped.tail(50)
        else:
            pass

        st.write('\n')
        # st.markdown('---')

        # -- PLOT DATAFRAME
        fig = px.bar(
            df_grouped,
            x=selected_kpi1,
            y='industry',
            # log_y=True,
            color=selected_kpi2,
            # color_continuous_scale=['red', 'yellow', 'green'],
            template='plotly_white',
            orientation="h",
            barmode="relative", #overlay #group
            title=f'<b>Financial ratios by {selected_kpi1} and {selected_kpi2}</b>'
        )

        fig.update_layout(
        autosize=False,
        # width=800,
        margin=dict(l=20, r=20, t=100, b=100),
        height=1000,
        )

        st.plotly_chart(fig, use_container_width=True)
        # fig.show()

    except ValueError as e:
        st.error('Please choose a different secondary ratio')

    # except:
    #     st.error('Please choose a different secondary ratio')

    st.caption("Last updated :" + str(last_recorded_datetime))