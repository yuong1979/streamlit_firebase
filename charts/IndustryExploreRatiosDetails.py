import pandas as pd
from tools import error_email, export_gs_func, kpi_mapping, kpi_remove, extract_csv, extract_industry_pickle
import streamlit as st
import plotly.express as px  # pip install plotly-express
import plotly.graph_objects as go
import numpy as np



# #################################################################################################
# ####### Bar chart ratios of individual industries ###############################################
# #################################################################################################
# python -c 'from IndustryExploreRatiosDetails import Industry_Explore_Ratios_Details; Industry_Explore_Ratios_Details()'



# sort and and convert dataframe into a format that can be displayed in chart 
@st.experimental_memo
def process_dataframe(df, kpi_mapping, kpi):
    #to determine if the ratio is postive or negative
    if kpi_mapping[kpi] == True:
        df_grouped = df.sort_values(by=[kpi], ascending=False )
    else:
        df_grouped = df.sort_values(by=[kpi], ascending=True )

    df_grouped = df_grouped[kpi]
    df_grouped = df_grouped.reset_index()

    return df_grouped


def handle_select():
    st.session_state.ind_type=st.session_state.ind_IndustryExploreRatiosDetails


def Industry_Explore_Ratios_Details():

    # df = pd.read_pickle('data/industry_data.pickle')
    df = extract_industry_pickle()

    last_recorded_datetime = df['daily_agg_record_time'].min().strftime("%b %d %Y %H:%M:%S")

    cols = df.columns.values.tolist()
    #remove unwanted kpis
    cols = [i for i in cols if i not in kpi_remove]
    cols.remove("industry")

    # df = convert_emptystr2na(df,cols)
    df.set_index('industry', inplace=True)
    ind_list = df.index.values.tolist()


    # st.write('\n')
    # st.markdown('---')

    default_testing = ['grossMargins', 'operatingMargins']

    #retrieving the selected industry from sessions
    if 'ind_type' in st.session_state:
        sel_ind = st.session_state['ind_type']
        index_no = ind_list.index(sel_ind)
    else:
        index_no = 0


    col1, col2 = st.columns([1,2])

    with col1:
        selected_ind = st.selectbox(
            'Select an industry',
            tuple(ind_list),
            index=index_no,
            key = "ind_IndustryExploreRatiosDetails",
            on_change = handle_select,
        )

    # if 'ind_type' not in st.session_state:
    #     st.session_state['ind_type'] = selected_ind

    with col2:
        selected_kpi = st.multiselect(
            "Select a ratio:",
            options= cols ,
            default= None
        )

    if len(selected_kpi) >= 4:
        st.error('User may only choose a maximum of 3 ratios')
        st.stop()
    
    # #recording the selected industry from sessions
    # st.session_state['selected_ind'] = selected_ind

    color_map = {}
    for i in ind_list:
        color_map[i] = "grey"
    
    color_map[selected_ind] = "red"

    for kpi in selected_kpi:

        with open('style/style.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
            with st.container():

                df_grouped = process_dataframe(df, kpi_mapping, kpi)

                value = df.loc[selected_ind, kpi]

                if kpi_mapping[kpi] == True:
                    maximum = df_grouped[kpi].max()
                    minimum = df_grouped[kpi].min()
                else:
                    minimum = df_grouped[kpi].max()
                    maximum = df_grouped[kpi].min()

                median = df_grouped[kpi].median()

                st.write('\n')

                st.subheader(kpi)
                col1, col2, col3, col4 = st.columns(4)
                col1.metric(label="Value", value=value)
                col2.metric(label="Market Maximum", value=maximum)
                col3.metric(label="Market Minimum", value=minimum)
                col4.metric(label="Market Median", value=median)



                fig = px.bar(
                    df_grouped,
                    x = 'industry',
                    y = kpi,
                    color = 'industry',
                    color_discrete_map = color_map,
                    # title=f'<b>{kpi}</b>',
                    template='plotly_white',
                    orientation="v",
                )

                fig.update_layout(
                    barmode="relative",
                    showlegend=False,
                    autosize=True,
                    # width=800,
                    margin=dict(l=20, r=20, t=40, b=40),
                    width=1000,
                )

                st.plotly_chart(fig)

    st.caption("Last updated :" + str(last_recorded_datetime))



































# # ###############################################################################################################################
# # ####### Version of Bar chart ratios of individual industries that includes fake bars - NOT WORKING because of bug #############
# # ###############################################################################################################################
# # python -c 'from test import industry_details; industry_details()'

# def Industry_Compare_Ratio_Bar():


#     # Add a title and intro text
#     st.title('Industry Financials Explorer')
#     st.subheader('Explore ratios comparisons of individual industries')

#     # ratios_by_industry()
#     df = pd.read_csv('dataframe_csv/industry_data.csv', index_col=1)
#     df = df.drop("Unnamed: 0", axis='columns')
#     cols = df.columns.values.tolist()
#     #remove unwanted kpis
#     cols = [i for i in cols if i not in kpi_remove]

#     ind_list = df.index.values.tolist()

#     # st.write('\n')
#     st.markdown('---')

#     col1, col2 = st.columns([1,2])


#     with col1:
#         selected_ind = st.selectbox(
#             'Select an industry',
#             tuple(ind_list),
#         )


#     with col2:
#         selected_kpi = st.multiselect(
#             "Select your ratios:",
#             options= cols ,
#             default= None
#         )


#     if len(selected_kpi) >= 5:
#         st.error('User may only choose a maximum of 4 ratios')
#         st.stop()
    
#     # button = st.button("Print Locations",disabled=False)

#     color_map = {}
#     for i in ind_list:
#         color_map[i] = "grey"
    
#     color_map[selected_ind] = "red"

#     for kpi in selected_kpi:
#         # selected_kpi_list = [kpi]
#         #to determine if the ratio is postive or negative
#         if kpi_mapping[kpi] == True:
#             df_grouped = df.sort_values(by=[kpi], ascending=False )
#         else:
#             df_grouped = df.sort_values(by=[kpi], ascending=True )

#         df_grouped = df_grouped[kpi]
#         df_grouped = df_grouped.reset_index()
#         # df_transposed = df_grouped.transpose()
#         # df_list = df_transposed.values.tolist()

#         # max_number = max(df_list[1])
#         # min_number = min(df_list[1])

#         # inverted_df = []
#         # for i in df_list[1]:
#         #     if i < 0:
#         #         x = max_number
#         #     else:
#         #         x = max_number - i
#         #     inverted_df.append(x)

#         # inverted_df_plus = []
#         # for i in df_list[1]:
#         #     if min_number > 0:
#         #         x = 0
#         #     else:
#         #         if i > 0:
#         #             x = min_number
#         #         else:
#         #             x = min_number - i

#         #     inverted_df_plus.append(x)


#         fig = px.bar(
#             df_grouped,
#             x = 'industry',
#             y = kpi,
#             color = 'industry',
#             color_discrete_map = color_map,
#             title=f'<b>{kpi}</b>',
#             template='plotly_white',
#             orientation="v",

#         )
#         # #this needs to be added if not hoverinfo will be disrupted by hoverinfo below and bug
#         # fig.update_traces(hoverinfo='skip')

#         # fig.add_bar(
#         #             x = df_list[0], 
#         #             y = inverted_df,
#         #             marker_color='white',
#         #             hoverinfo='skip',
#         #             )

#         # fig.add_bar(
#         #             x = df_list[0], 
#         #             y = inverted_df_plus,
#         #             marker_color='white',
#         #             hoverinfo='skip',
#         #             )

#         fig.update_layout(
#             barmode="relative",
#             showlegend=False,
#             autosize=True,
#             # width=800,
#             margin=dict(l=20, r=20, t=20, b=20),
#             width=800,
#         )

#         # hovertemplate = ('Industry: %{customdata[0]}<br>' + 'Value: %{customdata[1]}<br><extra></extra>')
#         # customdata = np.stack((df_list[0], df_list[1]), axis=-1)
#         # fig.update_traces(customdata=customdata,hovertemplate=hovertemplate)

#         st.plotly_chart(fig)

#         # fig.show()

