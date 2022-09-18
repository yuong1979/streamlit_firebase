import pandas as pd
from tools import error_email, export_gs_func, kpi_mapping, kpi_remove, extract_csv, extract_industry_pickle
import streamlit as st
import plotly.express as px  # pip install plotly-express
import plotly.graph_objects as go
import numpy as np


# #################################################################################################
# ####### Spider chart ratios of individual industries ###############################################
# #################################################################################################
# python -c 'from test import ratios_ranked_per_industry_radar; ratios_ranked_per_industry_radar()'




def handle_select():
    st.session_state.ind_type=st.session_state.ind_IndustryExploreRatiosRankings


def Industry_Explore_Ratios_Rankings():
    
    # df = pd.read_pickle('data/industry_data.pickle')
    df = extract_industry_pickle()

    last_recorded_datetime = df['daily_agg_record_time'].min().strftime("%b %d %Y %H:%M:%S")

    cols = df.columns.values.tolist()

    # #to be replaced with cols on top when finish using
    # cols = ['forwardEps', 'trailingEps', 'forwardPE', 'trailingPE', 'pegRatio', 'trailingPegRatio', 'enterpriseToEbitda', 'enterpriseToRevenue']

    #remove unwanted kpis
    cols = [i for i in cols if i not in kpi_remove]
    cols.remove("industry")

    # df = convert_emptystr2na(df,cols)

    df.set_index('industry', inplace=True)

    ind_list = df.index.values.tolist()

    Default_cols = cols[:len(cols)-10]

    # st.write('\n')
    # st.markdown('---')


    #retrieving the selected industry from sessions
    if 'ind_type' not in st.session_state:
        index_no = 0
    else:
        sel_ind = st.session_state['ind_type']
        index_no = ind_list.index(sel_ind)

    col1, col2 = st.columns([1,2])

    with col1:
        selected_ind = st.selectbox(
            'Select an industry',
            tuple(ind_list),
            # types[st.session_state['type']],
            index=index_no,
            key = "ind_IndustryExploreRatiosRankings",
            on_change = handle_select
        )

    # if 'ind_type' not in st.session_state:
    #     st.session_state['ind_type'] = selected_ind


    with col2:
        selected_kpi = st.multiselect(
            "Select a ratio:",
            options = cols,
            default = cols
        )

    # #recording the selected industry from sessions
    # st.session_state['selected_ind'] = selected_ind

    # if len(selected_kpi) >= 15:
    #     st.error('User may only choose a maximum of 14 ratios')
    #     st.stop()


    #collecting the median and max values for comparison
    value_abs = {}
    value_max = {}
    value_min = {}
    value_median = {}
    adj_value = {} #adj value for ratios that are negative in nature - debt/equity
    adj_range = {} #adj value for max range to include negative values


    rank_max = {}
    rank_val = {}
    rank_median = {}
    rank_fraction = {}

    rank_df = {}

    # print (selected_kpi, 'selected_kpi')

    for i in selected_kpi:
        dfnew = df[[i]]
        testdf = dfnew.loc[selected_ind, i]
        value_abs[i] = dfnew[i][[selected_ind]].values[0]
        value_max[i] = dfnew[i].max()
        value_min[i] = dfnew[i].min()
        value_median[i] = dfnew[i].median()

        # if the kpi ratio is negative = good, than reverse the order to rank it - debt/equity
        if kpi_mapping[i] == True:

            adj_range[i] = value_max[i] - value_min[i]
            adj_value[i] = value_abs[i] - value_min[i]
            rank_df[i] = dfnew[i].rank(ascending=False)

        else:

            adj_range[i] = value_max[i] - value_min[i]
            #to get the value(which is reversed), we need to take the maximum range and minus the difference between min(which is best) and the value
            adj_value[i] = adj_range[i] - (value_abs[i] - value_min[i])
            rank_df[i] = dfnew[i].rank(ascending=True)

        rank_median[i] = round(rank_df[i].count()/2)
        rank_max[i] = rank_df[i].count()
        rank_val[i] = (rank_df[i][[selected_ind]].values)[0]

        try:
            rank_fraction[i] = str(int(rank_val[i])) + "/" + str(int(rank_max[i]))
        except:
            rank_fraction[i] = 0

        # print (' ')
        # print (i)
        # print ("value_abs", value_abs[i])

        # print ("value_max - nr", value_max[i])
        # print ("value_min - nr", value_min[i])
        # print ("value_median" , value_median[i])
        # print ("adj_value" , adj_value[i])
        # print ("adj_range" , adj_range[i])

        # print ('-')

        # print ("rank_val" , rank_val[i])
        # print ("rank_median" , rank_median[i])
        # print ("rank_fraction" , rank_fraction[i])
        # print ("rank_max" , rank_max[i])

    #normalizing the numbers for insertion into chart
    rank_list = list(rank_val.values())
    values_list = list(value_abs.values())
    rank_fraction_list = list(rank_fraction.values()) 
    main_list = []
    median_rank_list = []
    for i, value in enumerate(rank_max):
        #ranking ranks 0 to 1 so those with lower ranks should have higher scores therefore 1 -rank/maxrank is neccessary
        item = 1 - (rank_list[i] / rank_max[value])
        item = round(item, 3)
        main_list.append(item)

        item = 1 - (rank_median[value] / rank_max[value])
        item = round(item, 3)
        median_rank_list.append(item)



    # print (rank_list, "rank_list")
    # print (values_list, "values_list")
    # print (main_list, "main_list")
    # print (rank_fraction_list, "rank_fraction_list")
    # print (median_rank_list, "median_rank_list")
    # print (cols, "cols")

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r = main_list,
        theta = selected_kpi,
        fill = 'toself',
        # showlegend=True,
        fillcolor = 'green',
        line_shape = 'spline', #linear
        text = values_list, 
        opacity=0.6,
        mode = 'markers+text', 
        textfont_color='red', 
        # textposition='bottom center',
        marker_color='green',

    ))

    fig.add_trace(go.Scatterpolar(
        r = median_rank_list,
        theta = selected_kpi,
        # fill = 'toself',
    ))

    fig.update_layout(
    polar=dict(
        radialaxis=dict(
        visible=False,
        range=[0, 1]
        )),
        showlegend=False
    )

    fig.update_layout(
        autosize=False,
        # width=800,
        # margin=dict(l=20, r=20, t=100, b=100),
        height=800,
    )
    
    hovertemplate = ('Ratio: %{customdata[0]}<br>' + 'Ranking: %{customdata[1]}<br>' + 'Value: %{customdata[2]}<br><extra></extra>')
    customdata = np.stack((selected_kpi, rank_fraction_list, values_list), axis=-1)
    fig.update_traces(customdata=customdata,hovertemplate=hovertemplate)


    st.plotly_chart(fig, use_container_width=True)

    st.caption("Last updated :" + str(last_recorded_datetime))











# def testing():
#     if st.session_state.ind_IndustryExploreRatiosRankings:
#         st.session_state.type=st.session_state.ind_IndustryExploreRatiosRankings


# def Testinghello():
#     st.write('hello!')

#     # types = ["Advertising Agencies", "Aerospace & Defense", "Agricultural Inputs"]




#     # selected_ind = st.selectbox(
#     #     'Select an industry',
#     #     # tuple(types),
#     #     types[st.session_state['type']],

#     #     # index=index_no,
#     #     key = "ind_IndustryExploreRatiosRankings",
#     #     on_change = testing
#     # )




#     def handle_click_wo_button(): 
#         if st.session_state.kind_of_column: 
#             st.session_state.type = st.session_state.kind_of_column

#     if not st.session_state:
#         st.session_state["type"] = 'Advertising Agencies'

    
#     types = {"Advertising Agencies":['Advertising Agencies'], "Aerospace & Defense":['Aerospace & Defense'], "Agricultural Inputs":['Agricultural Inputs']}


#     # types = {
#     #     'Categorical':['PULocationID','DOLocationID','payment_type'],
#     #     'Numerical':['passenger_count','trip_distance','fare_amount']
#     #     }

#     column = st.selectbox('Select a column',
#                             types[st.session_state['type']]
#                         )


#     type_of_column = st.radio("What kind of analysis",['Advertising Agencies', "Aerospace & Defense", "Agricultural Inputs"], on_change=handle_click_wo_button, key='kind_of_column') 

#     if st.session_state['type'] == "Advertising Agencies":
#         st.write('dude')
#     else:
#         st.write("haha")












