import streamlit as st

from firebase_admin import auth
# from streamlit_option_menu import option_menu
from charts_sample.sales_dashboard import sales_report
# from charts_sample.sankey_dashboard import sankey_report
from charts_sample.scatterplot import scatterplot_report
# from charts_sample.bar_chart import bar_report
from charts_sample.coloredbarchart import colored_bar_chart
from settings import project_id, firebase_database, fx_api_key, firestore_api_key, google_sheets_api_key, schedule_function_key, firebase_auth_api_key

from charts.IndustryExploreRatiosDetails import Industry_Explore_Ratios_Details
from charts.IndustryExploreRatiosDashboard import Industry_Explore_Ratios_Dashboard
from charts.IndustryExploreRatiosColorRanked import Industry_Explore_Ratios_Color_Ranked
from charts.IndustryExploreRatiosMarketSize import Industry_Explore_Ratios_Market_Size
from charts.IndustryExploreRatiosRankings import Industry_Explore_Ratios_Rankings
from charts.IndustryExploreMarketSize import Industry_Explore_Market_Size

from charts.EquityExploreRatiosRankings import Equity_Explore_Ratios_Rankings
from charts.EquityExploreDetail import Equity_Explore_Detail
from charts.EquityExploreTimeSeries import Equity_Explore_Time_Series
from charts.EquityExploreIndustryMarket import Industry_Explore_Industry_Market
from charts.EquityExploreMarketSize import Equity_Explore_Market_Size
from charts.EquityExploreRatiosDetail import Equity_Explore_Ratios_Detail

from authentication_functions import home, status

import time



def main():

    st.set_page_config(page_title="Financial Assets Explorer", page_icon=":chart_with_upwards_trend:", layout="wide") #layout can be centered

    print ('running main')

    #remove streamlit logo and menu
    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)

    # # # insert testing charts/data here
    # Industry_Explore_Ratios_Dashboard()

    ind_chart_list = ['Explore Ratios Market Size', 
                    'Explore Ratios Rankings', 
                    'Explore Ratios Color Ranked', 
                    'Explore Ratios Details', 
                    'Explore Ratios Dashboard',
                    'Explore Market Size',
                    'Explore Industry Market',
                    ]

    equity_chart_list = [ 'Equity Explore Time_Series', 
                        'Equity Explore Detail', 
                        'Equity_Explore_Ratios_Rankings',
                        'Equity Explore Market Size',
                        'Equity Explore Ratios Details',
                        ]


    if 'page' not in st.session_state:
        st.session_state['page'] = 'Home'

    def gohome():
        st.session_state['page'] = 'Home'

    def industry():
        st.session_state['page'] = 'Industry'

    def equities():
        st.session_state['page'] = 'Equities'

    with st.sidebar:

        # st.button(label, key=None, help=None, on_click=None, args=None, kwargs=None, *, disabled=False)

        Home = st.button(label="Home", key="Home", on_click=gohome)


        with st.expander("Industry Explorers"):
            options = st.radio('Select display:', ind_chart_list, key="ind_chart", horizontal=False, on_change=industry )


        with st.expander("Equities Explorers"):
            options1 = st.radio('Select display:', equity_chart_list, key="equity_chart", horizontal=False, on_change=equities )

    # st.write(st.session_state['page'])

    if st.session_state['page'] == 'Home':
        home()


    
    if st.session_state['page'] == 'Industry':
        ### uncomment status to activate login only access
        # status()
        if options == 'Explore Ratios Market Size':
            st.title('Industry Financials Explorer')
            st.subheader('Explore Ratios Market Size')
            Industry_Explore_Ratios_Market_Size()

        elif options == 'Explore Ratios Rankings':
            st.title('Industry Financials Explorer')
            st.subheader('Explore Ratios Rankings')
            Industry_Explore_Ratios_Rankings()

        elif options == 'Explore Ratios Color Ranked':
            st.title('Industry Financials Explorer')
            st.subheader('Explore Ratios Color Ranked')
            Industry_Explore_Ratios_Color_Ranked()

        elif options == 'Explore Ratios Details':
            st.title('Industry Financials Explorer')
            st.subheader('Explore Ratios Details')
            Industry_Explore_Ratios_Details()

        elif options == 'Explore Ratios Dashboard':
            st.title('Industry Financials Explorer')
            st.subheader('Explore Ratios Dashboard')
            Industry_Explore_Ratios_Dashboard()

        elif options == 'Explore Market Size':
            st.title('Industry Financials Explorer')
            st.subheader('Explore Market Size')
            Industry_Explore_Market_Size()

        elif options == 'Explore Industry Market':
            st.title('Industry Financials Explorer')
            st.subheader('Explore Equity / Industry')
            Industry_Explore_Industry_Market()


    if st.session_state['page'] == 'Equities':
        if options1 == 'Equity Explore Detail':
            st.title('Equities Financials Explorer')
            st.subheader('Explore Equity Details')
            Equity_Explore_Detail()

        elif options1 == 'Equity Explore Time_Series':
            st.title('Equities Financials Explorer')
            st.subheader('Explore Equity Time Series')
            Equity_Explore_Time_Series()

        elif options1 == 'Equity_Explore_Ratios_Rankings':
            st.title('Equities Financials Explorer')
            st.subheader('Explore Equity / Industry')
            Equity_Explore_Ratios_Rankings()

        elif options1 == 'Equity Explore Market Size':
            st.title('Equities Financials Explorer')
            st.subheader('Explore Market Size')
            Equity_Explore_Market_Size()

        elif options1 == 'Equity Explore Ratios Details':
            st.title('Equities Financials Explorer')
            st.subheader('Explore Ratio Details')
            Equity_Explore_Ratios_Detail()




        # elif options1 == 'bar_report':
        #     bar_report()
        # elif options1 == 'scatterplot_report':
        #     scatterplot_report()
        # elif options1 == 'sankey_report':
        #     sankey_report()
        # elif options1 == 'sales_report':
        #     sales_report()




if __name__ == '__main__':
    main()
