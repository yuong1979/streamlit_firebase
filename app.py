import streamlit as st

from firebase_admin import auth
from streamlit_option_menu import option_menu
from sales_dashboard import sales_report
from sankey_dashboard import sankey_report
from scatterplot import scatterplot_report
from bar_chart import bar_report
from coloredbarchart import colored_bar_chart
from settings import project_id, firebase_database, fx_api_key, firestore_api_key, google_sheets_api_key, schedule_function_key, firebase_auth_api_key

from charts.IndustryExploreRatiosDetails import Industry_Explore_Ratios_Details
from charts.IndustryExploreRatiosDashboard import Industry_Explore_Ratios_Dashboard
from charts.IndustryExploreRatiosColorRanked import Industry_Explore_Ratios_Color_Ranked
from charts.IndustryExploreRatiosMarketSize import Industry_Explore_Ratios_Market_Size
from charts.IndustryExploreRatiosRankings import Industry_Explore_Ratios_Rankings

from tools import updating_industry_csv
from authentication_functions import home, status



def main():
    st.set_page_config(page_title="Financial Assets Explorer", page_icon=":chart_with_upwards_trend:", layout="wide") #layout can be centered

    #refreshing the data if its not refreshing
    updating_industry_csv()

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

    ind_chart_list = ['Explore Ratios Market Size', 'Explore Ratios Rankings', 'Explore Ratios Color Ranked', 'Explore Ratios Details', 'Explore Ratios Dashboard']
    equity_chart_list = ['colored_bar_chart', 'bar_report', 'scatterplot_report', 'sankey_report', 'sales_report']


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


    if st.session_state['page'] == 'Equities':
        if options1 == 'colored_bar_chart':
            colored_bar_chart()
        elif options1 == 'bar_report':
            bar_report()
        elif options1 == 'scatterplot_report':
            scatterplot_report()
        elif options1 == 'sankey_report':
            sankey_report()
        elif options1 == 'sales_report':
            sales_report()




if __name__ == '__main__':
    main()
