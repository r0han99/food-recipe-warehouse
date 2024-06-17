# Dashboard 
import streamlit as st

# Data-centric
import pandas as pd
import numpy as np

# standard library
import datetime
import sys


# src
from src.utils import *

# google sheet
import gspread
from oauth2client.service_account import ServiceAccountCredentials

@st.cache_resource
def oauth():

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    google_credentials = st.secrets["google_credentials"]
    credentials_dict = {
    "type": google_credentials["type"],
    "project_id": google_credentials["project_id"],
    "private_key_id": google_credentials["private_key_id"],
    "private_key": google_credentials["private_key"].replace("\\n", "\n"),
    "client_email": google_credentials["client_email"],
    "client_id": google_credentials["client_id"],
    "auth_uri": google_credentials["auth_uri"],
    "token_uri": google_credentials["token_uri"],
    "auth_provider_x509_cert_url": google_credentials["auth_provider_x509_cert_url"],
    "client_x509_cert_url": google_credentials["client_x509_cert_url"]
}
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    client = gspread.authorize(creds)

    return client


@st.cache_data
def load_data(default="google-sheet"):

    if default == "google-sheet":

        # load from google sheet
        client = oauth()

        # Open the Google Sheet by name
        spreadsheet = client.open("recipe_data")

        sheet = spreadsheet.sheet1

        data = sheet.get_all_values()

        df = pd.DataFrame(data[1:], columns=data[0])
        
        return df, sheet


    else:
        # load previous snap-shot

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

    if 'data_read_date' not in st.session_state:
        st.session_state.data_read_date = datetime.now().strftime("%m/%d/%Y")
    

    data, sheet = load_data()
    processed_data = data.copy(deep=True)

    tab0, tab1, tab2 = st.tabs(["Data Snapshot and Load time", "Enter New Recipes to Database", "Watch Current Recipes"]) #"View & Edit Raw Database"])

    with tab0:

        subtitle(f"Data Read Date ~ {st.session_state.data_read_date}")
        subtitle("Snapshot")
        st.dataframe(data)
        st.divider()

        subtitle("Login to Platforms to Access the Videos without Interruption", color="green", font_size="25px")
        st.markdown("")
        cols = st.columns(2)
        with cols[0]:
            for platform in ["Instagram", "Facebook", "Youtube"]:
                subtitle(f"✦  {platform}")

        with cols[1]:
            for platform_link in ["https://www.instagram.com/", "https://www.facebook.com/", "https://www.youtube.com/" ]:
                st.link_button(label="Login", url=platform_link, use_container_width=True)



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
                                "Dish Foundation","Drinks & Smoothy", "Salads", "Other", "Dessert",'Ice-Cream']
                
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
            subtitle("↪ If you are done entering New Recipes check this Box here!", font_size="25px")
            if st.checkbox("Done Entering"):
                st.divider()
                cols = st.columns(3)
                with cols[0]:
                    subtitle("Save/Show Entered Data!", font_size="18px")

                if cols[1].button("Show Data!", use_container_width=True):
                    new_rec = st.session_state.submission_data
                    st.write(new_rec)
                

                if cols[2].button("Save Data!", use_container_width=True):

                    rows = [] # to append the data at end ( list of lists as values)
                    new_rec = st.session_state.submission_data

                    for dicts in new_rec:
                        rows.append(list(dicts.values()))

                    subtitle(f"New Entries {st.session_state.submission_count}", font_size="15px")
                    # st.write(rows)

                    # load from google sheet
                    client = oauth()

                    # Open the Google Sheet by name
                    spreadsheet = client.open("recipe_data")
                    sheet = spreadsheet.sheet1
                    sheet.append_rows(rows)

                    subtitle("Added to Data!", font_size="15px")
                
                    # Saving
                    # save_data_backups(df)
                    subtitle("Data Saved to Google-Sheet!", font_size="20px",color="green")
                    st.session_state.submission_count = 0

                    st.divider()
                    with st.expander("Link to the Google-Sheet"):
                        st.link_button("Google-Sheet", url="https://docs.google.com/spreadsheets/d/1TUkP_tcYUxxTyh2t4L4VnjxS2ItRSL-yIAxxlkvE6GA/edit?gid=412808850#gid=412808850")

        # cuisine Entry
        elif option == "Cuisine Entry!":
            st.markdown("_This section will be used to fill in the current absence of Cuisines for the existing recipe Links._") 
            st.warning("Under Development! ⏳")


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
    # with tab3:

    #     function = st.selectbox("Choose function", ["Select Function", "View All Data", "Edit Data In-Place", ], key="select-func")
    #     st.divider()
    #     subtitle(function, font_size="35px", color="royalblue", text_align="center")
    #     st.markdown("")
        
    #     if function == "Edit Data In-Place":
    #         with st.expander("Original Sheet"):
    #             st.data_editor(processed_data.reset_index(drop=True))

    #             st.divider()
    #             st.info("If you edited anything in the Database and want to save the changes made.")
    #             st.image("./assets/save.png")
            

    #     elif function == "View All Data":
    #         st.dataframe(processed_data)
            





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