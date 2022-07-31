
# https://youtu.be/92jUAXBmZyU?t=263

import streamlit as st

# "st.session_state object:", st.session_state

# if 'a_counter' not in st.session_state:
#     st.session_state['a_counter'] = 0

# if "boolean" not in st.session_state:
#     st.session_state.boolean = False
# st.write(st.session_state)

# st.write("a_counter is", st.session_state['a_counter'])
# st.write("boolean is:", st.session_state.boolean)

# for the_key in st.session_state.keys():
#     st.write(the_key)

# for the_values in st.session_state.values():
#     st.write(the_values)

# for item in st.session_state.items():
#     item

# button = st.button("Update state")
# "before pressing button", st.session_state
# if button:
#     st.session_state['a_counter'] += 1
#     st.session_state.boolean = not st.session_state.boolean
#     "after pressing button", st.session_state

# for key in st.session_state.keys():
#     del st.session_state[key]

# st.session_state


st.session_state["idtoken"] = "testvalue"

del st.session_state["idtoken"]

# if st.session_state["key1"] is not None:
#     print ("not none")

if 'idtoken' in st.session_state.keys():
  st.session_state['authenticated'] = True
else:
  st.session_state['authenticated'] = False


st.write(st.session_state)






# #slider that changes session state
# number = st.slider("A number", 1, 10, key="slider")

# st.write(st.session_state)
# col1, buff, col2 = st.columns([ 1, 0.5, 3])

# option_names = ["a", "b", "c"]

# next  = st.button("Next option")

# if next:
#     if st.session_state["radio_option"] == 'a':
#         st.session_state.radio_option = 'b'
#     elif st.session_state["radio_option"] == 'b':
#         st.session_state.radio_option = 'c'
#     else:
#         st.session_state.radio_option = 'a'

# option = col1.radio("Pick an option", option_names, key="radio_option")
# st.session_state

# if option == 'a':
#     col2.write("You picked a")
# elif option == 'b':
#     col2.write("You picked b")
# else:
#     col2.write("You picked c")








# # callbacks allow you to use widgets such as a currency converter that can be used on both sides
# "st.session_state object:", st.session_state


# def lbs_to_kgs():
#     st.session_state.kgs = st.session_state.lbs / 2.2046

# def kgs_to_lbs():
#     st.session_state.lbs = st.session_state.kgs * 2.2046


# col1, buff, col2 = st.columns([2,2,2])

# with col1:
#     pounds = st.number_input("Pounds:", key="lbs", on_change= lbs_to_kgs)
# with col2:
#     kilograms = st.number_input("Kilograms:", key="kgs", on_change= kgs_to_lbs)