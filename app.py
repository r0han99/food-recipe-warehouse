# Dashboard 
import streamlit as st

# Data-centric
import pandas as pd
import numpy as np

# src
from src.utils import *


def load_data():
    data = pd.read_csv("./data/Food-Links-Cleaned-Recipes.csv")
    return data



def process_data(data):

    def origins(link):
        origin = link.split(".")[1].title()
        if origin in ["Instagram","Facebook"]:
            return origin
        else:
            origin = "".join(link.split("/")[2].split(".")).title()
            return origin

    name_link_df = data[["NAME","LINK"]]
    name_link_df = name_link_df.dropna(axis=0)
    name_link_df['NAME'] = name_link_df['NAME'].apply(str.lower).apply(str.title)

    # origins
    name_link_df["FROM"] = name_link_df['LINK'].apply(origins)

    # Cuisine
    name_link_df["CUISINE"] = "None"
    


    return name_link_df


def save_data_backups(df, mode="overwrite"):

    if mode=="overwrite":

        df.to_csv("./data/recipe_data.csv",index=False)

    elif mode=="make-a-copy":

        pass



def increment_submission_count():
    st.session_state.submission_count += 1

    


def main():

    
    title("Food Recipes Dashboard 📄🧑‍🍳", color="navy", font_size="50px", text_align="center")
    st.divider()

    # Initialize session state if not already done
    if 'submission_count' not in st.session_state:
        st.session_state.submission_count = 0

    if 'submission_data' not in st.session_state:
        st.session_state.submission_data = []
    

    data = load_data()
    processed_data = process_data(data)

    tab1, tab2, tab3 = st.tabs(["Enter New Recipes to Database", "Watch Current Recipes", "View & Edit Raw Database"])


    with tab1:

        option = st.selectbox("Options", ["Select Option", "New Recipe Entry!", "Cuisine Entry!"], key="entry-mode")
        st.divider()
        subtitle(option, font_size="35px", color="dodgerblue", text_align="center")
        st.markdown("")

        NEW_RECORDS = []

        if option == "New Recipe Entry!":
            with st.form("New Recipe!", clear_on_submit=True):
                subtitle("Enter information", font_size="25px", text_align="center")
                st.markdown("")
            
                recipe_name = st.text_input(label="Recipe Name",placeholder="Chicken Biryani")
                video_link = st.text_input(label="Platform Video Link", placeholder="Instagram/Facebook/Youtube/Tiktok Link")
                from_label = st.selectbox("Platform Selector, FROM?", ["Select FROM", "Instagram","Facebook","Youtube","Tiktok","Other"], key="select-from")

                cuisine_list = ["Select Cuisine","Indian Main Course", "Italian Main Course", "Indian Non-Veg Snack", 
                                "Indian Veg-Snack", "Italian Side Dish", 
                                "Dish Foundation","Drinks & Smoothy", "Salads", "Other"]
                
                cuisine_label = st.selectbox("Cuisine", cuisine_list, key="select-cuisine")

                st.divider()
                submitted = st.form_submit_button("Enter Data!", use_container_width=True)

            if submitted:
                if from_label != "Select FROM" and cuisine_label != "Select Cuisine" and recipe_name != "" and video_link != "":
                    increment_submission_count()

                    new_data = {"NAME":recipe_name, 
                                "LINK":video_link, 
                                "FROM": from_label, 
                                "CUISINE": cuisine_label
                                
                                
                                }
                    
                    
                    
                    st.session_state.submission_data.append(new_data)
                    subtitle(f'Total submissions so far: {st.session_state.submission_count}')

                    
                else:
                    st.warning("Enter Data properly!")



            st.divider()
            if st.checkbox("Done Entering Data!",):
                st.divider()
                cols = st.columns(2)
                with cols[0]:
                    subtitle("Save Entered Data!")
                

                if cols[1].button("Save Data!", use_container_width=True):
                    
                    new_rec = pd.DataFrame(st.session_state.submission_data)
                    subtitle("New Entry", font_size="15px")
                    st.write(new_rec)
                    subtitle("Added to Data!", font_size="15px")
                    df = pd.concat([processed_data, new_rec], axis=0, ignore_index=True)
                    st.dataframe(df.tail())
                    
                    # saving
                    save_data_backups(df)
                    subtitle("Data Saved to Computer!", font_size="20px",color="green")
                    st.session_state.submission_count = 0
                    

            









    # Watch Current Recipes
    with tab2:

        origins = list(processed_data['FROM'].unique())
        origins.insert(0, "Select Platform")
        platform = st.selectbox("Choose platform", origins, key="select-origins")
        platform_df = processed_data[processed_data['FROM']==platform]

        st.divider()
        subtitle(platform, font_size="35px", color="blue", text_align="center")
        st.divider()
        
        # Display the data with buttons
        for index, row in platform_df.iterrows():
            col1, col2 = st.columns([3, 1])
            with col1:
                subtitle(f'''✦   {row["NAME"]}''', font_size="25px")
            with col2:
                st.link_button(f"{platform}", row["LINK"], use_container_width=True)
                

        


    # View & Edit Raw Database
    with tab3:

        function = st.selectbox("Choose function", ["Select Function", "View All Data", "Edit Data In-Place", ], key="select-func")
        st.divider()
        subtitle(function, font_size="35px", color="royalblue", text_align="center")
        st.markdown("")
        
        if function == "Edit Data In-Place":
            with st.expander("Original Sheet"):
                st.data_editor(processed_data.reset_index(drop=True))

                st.divider()
                st.info("If you edited anything in the Database and want to save the changes made.")
                st.image("./assets/save.png")
            

        elif function == "View All Data":
            st.dataframe(processed_data)
            





if __name__ == "__main__":


    # config
    st.set_page_config("Recipe Dashboard", page_icon='🧑‍🍳', layout="centered")
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,100..1000;1,9..40,100..1000&family=Outfit:wght@100..900&display=swap');
        </style>
        """,
        unsafe_allow_html=True
    )


    main()