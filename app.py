import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import datetime
import re
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# URL of Fightmatrix webpage
# url_fightmatrix= str(input())
# url_fightmatrix_1 = "https://www.fightmatrix.com/fighter-profile/Benoit+St.+Denis/205208/"    #Temp pour les test
# url_fightmatrix_2 = "https://www.fightmatrix.com/fighter-profile/Joel+Alvarez/143278/"        #Temp pour les test

# Get tapology URL and soup_fightmatrix
def get_tapology_url(url):
    headers ={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("Success")
        html_content = response.text
    else:
        print(f"Error : {response.status_code}")

    soup_fightmatrix = BeautifulSoup(html_content, "html.parser")

    fighter_url=soup_fightmatrix.find("a", title=lambda x: x and "Tapoploy.com" in x)["href"]

    return fighter_url, soup_fightmatrix

# Send request to Tapology fighter page
def send_request_tapology(url_tapology):
    headers ={
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }

    # Send the request GET
    response = requests.get(url_tapology, headers=headers)

    if response.status_code == 200:
        print("Success")
        html_content = response.text
    else:
        print(f"Error : {response.status_code}")

    # Analysis of HTML content with BeautifulSoup
    soup_tapology = BeautifulSoup(html_content, "html.parser")
    return soup_tapology

# Function to retrieve Tapology fights in a Dataframe
def retrieve_tapology_fights(soup_tapology):

    # Extract data
    pro_fights_list=soup_tapology.find_all("div",attrs={"class":"div mb-2.5 bg-tap_f2 relative rounded-sm","data-division":"pro"})

    # List creation

    result_list=[]
    outcome_list=[]
    name_list=[]
    opp_record_list=[]
    opp_win_list=[]
    opp_lose_list=[]
    opp_draw_list=[]
    record_list=[]
    win_list=[]
    lose_list=[]
    draw_list=[]
    details_list=[]
    year_list=[]
    date_list=[]
    organization_list=[]
    art_list=[]

    for fight in pro_fights_list:

        
        result=fight.find("div",class_= lambda x:x in ["div w-[28px] md:w-[32px] flex shrink-0 items-center justify-center text-white text-opacity-60 text-lg leading-none font-extrabold h-full rounded-l-sm bg-[#29b829] opacity-90","div w-[28px] md:w-[32px] flex shrink-0 items-center justify-center text-white text-opacity-60 text-lg leading-none font-extrabold h-full rounded-l-sm bg-[#c1320c] opacity-90"])
        result_list.append(result.text if result else np.NaN)

        outcome=fight.find("div",class_=lambda x: x in ["div text-[#29b829] -rotate-90", "div text-[#c1320c] -rotate-90"])
        outcome_list.append(outcome.text if outcome else np.NaN)

        name=fight.find("a",attrs={"class":"border-b border-dotted border-tap_6 hover:border-solid"})
        name_list.append(name.text if name else np.NaN)

        opp_record=fight.find("span",attrs={"class":"cursor-zoom-in","title":"Opponent Record Before Fight"})
        opp_record_list.append(opp_record.text if opp_record else np.NaN) 

        if opp_record and opp_record.text != "N/A":
            opp_record_split=opp_record.text.split('-')  # Split le record en liste pour pouvoir distinguer win, lose, draw: X-Y-Z ->[X,Y,Z]
            opp_win_list.append(int(opp_record_split[0]))
            opp_lose_list.append(int(opp_record_split[1]))
            opp_draw_list.append(int(opp_record_split[2]) if len(opp_record_split)==3 else 0)
        else:
            opp_record_split=[np.NaN,np.NaN,np.NaN] # Prends en compte le cas où aucun record n'est affiché pour l'adversaire (Pas de page tapology, autre art martial,...)
            opp_win_list.append(opp_record_split[0])
            opp_lose_list.append(opp_record_split[1])
            opp_draw_list.append(opp_record_split[2]) 
    
        


        record=fight.find("span",attrs={"class":"cursor-zoom-in","title":"Fighter Record Before Fight"})
        record_list.append(record.text if record else np.NaN)
        
        if record and record.text != 'N/A':
            record_split=record.text.split('-')  # Split le record en liste pour pouvoir distinguer win, lose, draw: X-Y-Z ->[X,Y,Z]
            win_list.append(int(record_split[0]))
            lose_list.append(int(record_split[1]))
            draw_list.append(int(record_split[2]) if len(record_split)==3 else 0) 
        else:
            record_split=[np.NaN,np.NaN,np.NaN] # Prends en compte le cas où aucun record n'est affiché pour l'adversaire (Pas de page tapology, autre art martial,...)
            win_list.append(record_split[0])
            lose_list.append(record_split[1])
            draw_list.append(record_split[2]) 


        details=fight.find("div",class_="div text-tap_3 text-[13px] leading-[16px]")
        detail= details.text.replace("\n","") if details else np.NaN
        details_list.append(detail)

        year=fight.find("span",class_="text-[13px] md:text-xs text-tap_3 font-bold")
        year_list.append(year.text if year else np.NaN)

        month_to_number_dict = {"Jan": "1 ","Feb": "2 ","Mar": "3 ","Apr":  "4 ","May": "5 ","Jun":  "6 ","Jul":  "7 ","Aug":  "8 ","Sep":  "9 ","Oct":  "10 ","Nov":  "11 ","Dec":  "12 "}
        date=fight.find("span",class_="text-xs11 text-neutral-600")
        if date:
            date_split=date.text.split()
            date_split[0]=month_to_number_dict[date_split[0]]
            date="".join(date_split)
        date_list.append(date if date else np.NaN)


        org_img = fight.find('img', class_='opacity-70')
        organization_list.append(org_img['alt'] if org_img and 'alt' in org_img.attrs else np.NaN)

        art=fight.find("span",class_="hidden md:block text-tap_gold")
        art_list.append(art.text if art else "MMA")


    data_dict={"Record":record_list,"Opponent Name":name_list,"Opponent Record":opp_record_list,"Result":result_list,"Outcome":outcome_list,\
               "Details":details_list,"Year":year_list,"Date":date_list,"Fighter Win":win_list,"Fighter Lose":lose_list,"Fighter draw":draw_list,\
                "Opponent Win":opp_win_list,"Opponent Lose":opp_lose_list,"Opponent draw":opp_draw_list,"Organization":organization_list,"Art":art_list}

    df = pd.DataFrame.from_dict(data_dict)

    # Dataframe data cleaning
    df["Date"] = df["Date"]+" "+df["Year"]
    df = df.drop(columns=["Year"])

    df["Date"] = pd.to_datetime(df["Date"])
    df[["Result","Outcome","Details","Organization","Art"]] = df[["Result","Outcome","Details","Organization","Art"]].astype('category')

    return df

# Retrieve fighters informations
def retrieve_fighter_info(soup_tapology,soup_fightmatrix):

    fighter_info={}

    picture_div=soup_tapology.find("div",class_="div mt-5 flex flex-col items-center justify-center")
    picture=picture_div.find("img")
    picture=picture['src']
    fighter_info["Picture"]=picture

    name_div = soup_tapology.find("div",attrs={"class":"div text-tap_3 text-[26px] leading-tight md:leading-none font-bold"})
    name = name_div.text
    fighter_info["Name"] = name

    today=datetime.now()
    fighter_birthday = soup_tapology.find("span", attrs={"data-controller":"age-calc"})
    fighter_birthday = fighter_birthday.text if fighter_birthday else np.NaN
    fighter_birthday = datetime.strptime(str(fighter_birthday), '%Y-%m-%d')
    fighter_info["Birthday"] = fighter_birthday

    fighter_age = today.year - fighter_birthday.year - ((today.month, today.day) < (fighter_birthday.month, fighter_birthday.day))
    fighter_info["Age"] = fighter_age

    record_div = soup_fightmatrix.find_all(string=re.compile('Pro Record: '))
    record = [record.parent for record in record_div]
    record=record[0].find("strong").text
    fighter_info["Record"]=record

    last_5_div = soup_fightmatrix.find_all(string=re.compile('Last 5: '))
    last_5_div= last_5_div[0].parent
    last_5_div=last_5_div.find_all("span")
    last_5=[last.text for last in last_5_div]
    fighter_info["Last 5"]=last_5

    ranking=soup_fightmatrix.find("a",title="view the divisional ranking")
    ranking=ranking.text if ranking else np.NaN
    fighter_info["Ranking"]=ranking

    finish_perc_div=soup_fightmatrix.find_all(string=re.compile('Win Finish %: '))
    finish_perc_div = [i.parent for i in finish_perc_div]
    finish_perc=finish_perc_div[0].find("strong")
    finish_perc=finish_perc.text if finish_perc else np.NaN
    fighter_info["Finish %"]=finish_perc

    streak_div=soup_tapology.find("strong",string="Current MMA Streak:")
    streak_div=streak_div.parent
    streak=streak_div.find("span")
    streak=streak.text if streak else np.NaN
    fighter_info["Streak"]=streak


    return fighter_info

# Retrieve fight data from fightmatrix
def retrieve_fightmatrix_fights(soup_fightmatrix):

    opponent_name_list=[]
    opponent_ranking_list=[]
    date_list=[]
    soup_body=soup_fightmatrix.find("div",class_="xma_desktop")
    fights_div = soup_body.find_all("td",class_=lambda x: x and ("tdRank" in x),attrs={"style":"text-align: left; padding-top: 5px; padding-left: 2px; padding-right: 2px; padding-bottom: 5px; width: 180px"})

    for fight in fights_div:
        opponent_name = fight.find("a",class_="sherLink")
        opponent_name_list.append(opponent_name.text if opponent_name else np.NaN)

        opponent_ranking = fight.find("em")
        opponent_ranking_list.append(opponent_ranking.text if opponent_ranking else np.NaN)


    fights_div = soup_body.find_all("td",class_=lambda x: x and ("tdRank" in x),attrs={"style":"text-align: left; padding-top: 5px; padding-left: 2px; padding-right: 2px; padding-bottom: 5px;"})

    for fight in fights_div:

        if fight.find("a",class_="sherLink"):
            date=fight.find("em")
            date_list.append(date.text.split(",")[1].strip().replace("1st", "1").replace("2nd", "2").replace("3rd", "3").replace("th", "") if date else np.NaN)

    fights_dict = {"Opponent Name": opponent_name_list, "Opponent Ranking":opponent_ranking_list, "Date": date_list}
    df_fightmatrix = pd.DataFrame.from_dict(fights_dict)

    # Clean dataframe
    df_fightmatrix["Date"] = pd.to_datetime(df_fightmatrix["Date"].str.strip(), format='%B %d %Y')    
    split_column = df_fightmatrix["Opponent Ranking"].str.split(expand=True)
    df_fightmatrix["Opponent Ranking"] = split_column[0]
    df_fightmatrix["Ranking Category"] = split_column[1] + ((" " + split_column[2]) if split_column.shape[1]==3 else "")
    df_fightmatrix["Opponent Ranking"] = df_fightmatrix["Opponent Ranking"].str.replace("#","")
    df_fightmatrix["Opponent Ranking"] = df_fightmatrix["Opponent Ranking"].astype("Int64")
    df_fightmatrix["Ranking Category"] =  df_fightmatrix["Ranking Category"].astype("category")
    return df_fightmatrix

# Retrieve fighter's rankings from fightmatrix
def retrieve_fightmatrix_rankings(soup_fightmatrix):

    date_list=[]
    rank_list=[]

    ranking_table = soup_fightmatrix.find("table",class_="tblRank",attrs={"onmouseover":"TagToTip('hist')","onmouseout":"UnTip()"})
    rankings = ranking_table.find_all("tr")

    for rank in rankings:
        if rank.find("a",class_="sherLink"):

            date = rank.find("a",class_= "sherLink")
            date_list.append(date.text if date else np.NaN)

            ranking=rank.find("td",string=lambda x:x and "#" in x)
            rank_list.append(ranking.text if ranking else np.NaN)

    ranking_dict={"Date": date_list,"Ranking":rank_list}
    df_ranking_history=pd.DataFrame.from_dict(ranking_dict)

    # Data cleaning
    df_ranking_history["Date"] = pd.to_datetime(df_ranking_history["Date"])
    split_column = df_ranking_history["Ranking"].str.split(expand=True)
    df_ranking_history["Ranking"] = split_column[0]
    df_ranking_history["Ranking Category"] = split_column.apply(lambda x: " ".join(filter(None, x[1:])), axis=1)
    df_ranking_history["Ranking"] = df_ranking_history["Ranking"].str.replace("#","")
    df_ranking_history["Ranking"] = df_ranking_history["Ranking"].astype("Int64")
    df_ranking_history["Ranking Category"] =  df_ranking_history["Ranking Category"].astype("category")

    return df_ranking_history

def retrieve_all_data(url_fightmatrix):
    if url_fightmatrix:
        url_tapology, soup_fightmatrix = get_tapology_url(url_fightmatrix)
        soup_tapology = send_request_tapology(url_tapology)
        df_tapology=retrieve_tapology_fights(soup_tapology)
        fighter_info=retrieve_fighter_info(soup_tapology,soup_fightmatrix)
        df_fightmatrix = retrieve_fightmatrix_fights(soup_fightmatrix)
        df_ranking_history=retrieve_fightmatrix_rankings(soup_fightmatrix)
        return df_tapology,fighter_info,df_fightmatrix,df_ranking_history
    else:
        return

# _________________________ DATAFRAMES CREATION _________________________

def fights_analysis(func_fights_df,func_ranking_history_df):
    opponents_win_lose_total = func_fights_df.loc[func_fights_df["Result"]=="W"][['Opponent Win', 'Opponent Lose', "Fighter Name"]].groupby("Fighter Name").agg("sum")
    opponents_win_lose_total = opponents_win_lose_total.rename(columns={"Opponent Win":"Win","Opponent Lose":"Loss","Fighter Name":"Name"})
    df_melted = opponents_win_lose_total.melt(ignore_index=False).reset_index()
    temp_ranking_history_df = func_ranking_history_df.sort_values("Date",ascending=True)
    temp_ranking_history_df["Date"] = temp_ranking_history_df["Date"].dt.strftime('%B %Y')
    opponents_ranking = func_fights_df.loc[func_fights_df["Result"]=="W"][["Fighter Name","Result","Opponent Ranking","Date"]].sort_values("Date",ascending=True)


# _________________________ DATA VISUALISATION STREAMLIT _________________________

# __________Header__________
st.set_page_config(page_title='Fighters comparison',  layout='wide', page_icon=':chart_with_upwards_trend:')

#Fighter selection
left_col,right_col =st.columns(2)
fighters_names_url_dict={"Benoît St. Denis":'https://www.fightmatrix.com/fighter-profile/Benoit+St.+Denis/205208/',"Joel Alvarez":'https://www.fightmatrix.com/fighter-profile/Joel+Alvarez/143278/'}
dict_url_to_df = {} #Temp test pas encore fonctionnel

fighters_list_df = pd.read_csv('data/fighters_list.csv')
fighters_list_df = fighters_list_df.drop_duplicates()
to_dict = fighters_list_df.to_dict('list')
name_link_dict = {name: link for name, link in zip(fighters_list_df['names'], fighters_list_df['links'])}
fighter_propositions = ["URL Fightmatrix"] + fighters_list_df['names'].tolist()

with left_col:
    fighter1_selectbox = st.selectbox("Fighter 1", fighter_propositions)
    if fighter1_selectbox == "URL Fightmatrix":
        fighter1_url = st.text_input("Enter the 1st fighter's link")
    else:
        fighter1_url =  "https://www.fightmatrix.com"+name_link_dict[fighter1_selectbox]

with right_col:
    fighter2_selectbox = st.selectbox("Fighter 2", fighter_propositions)
    if fighter2_selectbox == "URL Fightmatrix":
        fighter2_url = st.text_input("Enter the 2nd fighter's link")
    else:
        fighter2_url = "https://www.fightmatrix.com"+name_link_dict[fighter2_selectbox]

compare_button=st.button("Compare" if fighter1_url and fighter2_url else "Present")




# _________Display results_________
if compare_button:
#     # Get data 
#     try:
#         df_tapology_1,fighter_info_1,df_fightmatrix_1,df_ranking_history_1 = dict_url_to_df[fighter1_url][0],dict_url_to_df[fighter1_url][1],dict_url_to_df[fighter1_url][3],dict_url_to_df[fighter1_url][4]
#     except:
#         df_tapology_1,fighter_info_1,df_fightmatrix_1,df_ranking_history_1 =retrieve_all_data(fighter1_url)
#         dict_url_to_df[fighter1_url] = [df_tapology_1.copy(),fighter_info_1.copy(),df_fightmatrix_1.copy(),df_ranking_history_1.copy()]
#     try:
#         df_tapology_2,fighter_info_2,df_fightmatrix_2,df_ranking_history_2 = dict_url_to_df[fighter2_url][0],dict_url_to_df[fighter2_url][1],dict_url_to_df[fighter2_url][3],dict_url_to_df[fighter2_url][4]
#     except:
#         df_tapology_2,fighter_info_2,df_fightmatrix_2,df_ranking_history_2 =retrieve_all_data(fighter2_url)
#         dict_url_to_df[fighter2_url] =[df_tapology_2.copy(),fighter_info_2.copy(),df_fightmatrix_2.copy(),df_ranking_history_2.copy()]

#     #TEMPORARY FOR LOCAL USE
    import pickle

#     with open('soup_df_tapology_1.pkl', 'wb') as f:
#         pickle.dump(df_tapology_1, f)
    
#     with open('soup_fighter_info_1.pkl', 'wb') as f:
#         pickle.dump(fighter_info_1, f)
    
#     with open('soup_df_fightmatrix_1.pkl', 'wb') as f:
#         pickle.dump(df_fightmatrix_1, f)

#     with open('soup_df_ranking_history_1.pkl', 'wb') as f:
#         pickle.dump(df_ranking_history_1, f)

# # ----- 2
#     with open('soup_df_tapology_2.pkl', 'wb') as f:
#         pickle.dump(df_tapology_2, f)
    
#     with open('soup_fighter_info_2.pkl', 'wb') as f:
#         pickle.dump(fighter_info_2, f)
    
#     with open('soup_df_fightmatrix_2.pkl', 'wb') as f:
#         pickle.dump(df_fightmatrix_2, f)

#     with open('soup_df_ranking_history_2.pkl', 'wb') as f:
#         pickle.dump(df_ranking_history_2, f)

# --- load

    with open('soup_df_tapology_1.pkl', 'rb') as f:
        df_tapology_1 = pickle.load(f)
    
    with open('soup_fighter_info_1.pkl', 'rb') as f:
        fighter_info_1 = pickle.load(f)

    with open('soup_df_fightmatrix_1.pkl', 'rb') as f:
        df_fightmatrix_1 = pickle.load(f)

    with open('soup_df_ranking_history_1.pkl', 'rb') as f:
        df_ranking_history_1 = pickle.load(f)

# ----- 2
    with open('soup_df_tapology_2.pkl', 'rb') as f:
        df_tapology_2 = pickle.load(f)
    
    with open('soup_fighter_info_2.pkl', 'rb') as f:
        fighter_info_2 = pickle.load(f)
    
    with open('soup_df_fightmatrix_2.pkl', 'rb') as f:
        df_fightmatrix_2 = pickle.load(f)

    with open('soup_df_ranking_history_2.pkl', 'rb') as f:
        df_ranking_history_2 = pickle.load(f)

# END TEMP

    # Cleaning dataframe
    def Df_cleaning(df_ranking_history,fighter_info,df_tapology,df_fightmatrix):
        df_ranking_history["Fighter Name"]=fighter_info["Name"]
        df_tapology=df_tapology.loc[df_tapology["Art"]=="MMA"]
        df_fights=pd.merge(df_tapology, df_fightmatrix,how="right",on = 'Date')
        df_fights["Fighter Name"] = fighter_info["Name"]
        return df_fights
    
    df_fights_1 = Df_cleaning(df_ranking_history_1,fighter_info_1,df_tapology_1,df_fightmatrix_1)
    df_fights_2 = Df_cleaning(df_ranking_history_2,fighter_info_2,df_tapology_2,df_fightmatrix_2)


    st.dataframe(df_tapology_1) #Temp
    st.dataframe(df_fightmatrix_1)#Temp
    st.dataframe(df_fights_1) #Temp
    st.dataframe(df_ranking_history_1) # TEMP



    df_ranking_history = pd.concat([df_ranking_history_1,df_ranking_history_2],ignore_index=True)
    df_fights = pd.concat([df_fights_1,df_fights_2],ignore_index=True)

    df_fights=df_fights.loc[df_fights["Art"]=="MMA"] # Select only MMA fights

  
    #_________Présentation_________
    # Colonnes pour les images uniquement
    def Presentation(fighter_info_1,fighter_info_2,df_fights_1,df_fights_2,df_ranking_history_1,df_ranking_history_2):
        left_img_col, center_space, right_img_col = st.columns([0.4, 0.2, 0.4])

        with left_img_col:
            st.image(fighter_info_1["Picture"], use_container_width=True)

        with right_img_col:
            st.image(fighter_info_2["Picture"], use_container_width=True)

        # Préparation des données
        streak_emojis_f1 = ''.join(['🟢' if i == 'W' else '🔴' if i == 'L' else '⚪' if i == 'D' else '❓' for i in fighter_info_1['Last 5']])
        streak_emojis_f2 = ''.join(['🟢' if i == 'W' else '🔴' if i == 'L' else '⚪' if i == 'D' else '❓' for i in fighter_info_2['Last 5']])

        # Création du tableau pour le reste des données
        html_table = f"""
        <style>
        .fighter-table {{
            width: 100%;
            border-collapse: collapse;
            table-layout: fixed;
        }}
        .fighter-table td {{
            text-align: center;
            padding: 8px;
            vertical-align: middle;
        }}
        .divider {{
            border-bottom: 1px solid #ddd;
            margin: 5px 0;
        }}
        .fighter-name {{
            font-weight: bold;
            font-size: 1.2em;
        }}
        .header {{
            font-weight: bold;
        }}
        </style>

        <table class="fighter-table">
            <tr>
                <td class="fighter-name">{df_fights_1["Fighter Name"].unique()[0]}</td>
                <td class="header">Name</td>
                <td class="fighter-name">{df_fights_2["Fighter Name"].unique()[0]}</td>
            </tr>
            <tr><td colspan="3" class="divider"></td></tr>
            <tr>
                <td>{fighter_info_1['Age']}</td>
                <td class="header">Age</td>
                <td>{fighter_info_2['Age']}</td>
            </tr>
            <tr><td colspan="3" class="divider"></td></tr>
            <tr>
                <td>{df_ranking_history_1['Ranking Category'][0]}</td>
                <td class="header">Category</td>
                <td>{df_ranking_history_2['Ranking Category'][0]}</td>
            </tr>
            <tr><td colspan="3" class="divider"></td></tr>
            <tr>
                <td>{fighter_info_1['Record']}</td>
                <td class="header">Record</td>
                <td>{fighter_info_2['Record']}</td>
            </tr>
            <tr><td colspan="3" class="divider"></td></tr>
            <tr>
                <td>{fighter_info_1['Finish %']}</td>
                <td class="header">Finish %</td>
                <td>{fighter_info_2['Finish %']}</td>
            </tr>
            <tr><td colspan="3" class="divider"></td></tr>
            <tr>
                <td>{streak_emojis_f1}</td>
                <td class="header">Last 5</td>
                <td>{streak_emojis_f2}</td>
            </tr>
            <tr><td colspan="3" class="divider"></td></tr>
            <tr>
                <td>{df_ranking_history_1['Ranking'][0]}</td>
                <td class="header">Ranking</td>
                <td>{df_ranking_history_2['Ranking'][0]}</td>
            </tr>
        </table>
        """
        return html_table
    
    html_table = Presentation(fighter_info_1,fighter_info_2,df_fights_1,df_fights_2,df_ranking_history_1,df_ranking_history_2)
    # Afficher le tableau HTML
    st.markdown(html_table, unsafe_allow_html=True)

    #_________GRAPHS_________
    # Fighter's Ranking evolution graph
    def Graph_Fighter_Ranking_Evolution(df_ranking_history):

        fighter1_name = df_ranking_history['Fighter Name'].unique()[0]
        fighter2_name = df_ranking_history['Fighter Name'].unique()[1]

        fig = go.Figure()

        fighter_colors = {
            fighter1_name: 'red',
            fighter2_name: 'blue'}
        
        fighters = df_ranking_history['Fighter Name'].unique()

        for fighter in fighters:
            df_ranking_hist_temp = df_ranking_history[df_ranking_history['Fighter Name'] == fighter] 
            fig.add_trace(go.Scatter(x = df_ranking_hist_temp['Date'],
                        y = df_ranking_hist_temp['Ranking'],
                        name=fighter,      
                        line=dict(color=fighter_colors.get(fighter, 'grey'), width=2), 
                        mode = 'lines+markers',
                        hoverinfo='text',
                        text=[f"<b>{row['Fighter Name']}</b><br>" +
                            f"Rank: #{int(row['Ranking']) if pd.notna(row['Ranking']) else 'N/A'}<br>" +
                            f"Date: {row['Date']:%Y-%m-%d}" 
                            for index, row in df_ranking_hist_temp.iterrows()]
            ))
            
        fig.update_layout(
            title="Fighters Ranking Evolution",
            xaxis_title="Date",
            yaxis_title="Ranking",
            yaxis=dict(autorange="reversed"),  # Lower rank number is better
            legend_title="Fighter",
            hovermode="closest")
        return fig
    
    graph_rank_evolution = Graph_Fighter_Ranking_Evolution(df_ranking_history)
    st.plotly_chart(graph_rank_evolution,use_container_width=True)

    # Opponent ranking graph
    def Graph_Opponent_Ranking(df_fights,fighter_info_1,fighter_info_2):

        # 1. Graphique évolution des rankings des adversaires
        df_fights_sorted = df_fights.sort_values(by=["Fighter Name", "Date"])
        fighter1_name = fighter_info_1["Name"]
        fighter2_name = fighter_info_2["Name"]

        fig = go.Figure()
        # 2. Crée le dictionnaire de couleurs
        fighter_colors = {
            fighter1_name: 'red',
            fighter2_name: 'blue'
        }

        result_colors = {'W': '#7FFF00',
                        'L': '#be1c00', 
                        'D': '#f8e716', 
                        np.nan: '#cac9c1'}
        result_symbols = {'W': 'circle',
                            'L': 'x',
                            'D': 'square',
                            np.nan: 'triangle-right'}  # Default to square for unknown results
        # Add a trace (line + markers) for each fighter
        fighters = df_fights['Fighter Name'].unique()

        # Add a trace (line + markers) for each fighter
        for fighter in fighters:
            fighter_df = df_fights[df_fights['Fighter Name'] == fighter].copy()
                    
            # Create a list of marker colors based on the 'Result' column for this fighter
            marker_color_list = fighter_df['Result'].map(result_colors).tolist()

            # Map 'Result' to marker symbols
            marker_symbol_list = fighter_df['Result'].map(result_symbols).tolist()

            fig.add_trace(go.Scatter(
                x=fighter_df['Date'],
                y=fighter_df['Opponent Ranking'],
                mode='lines+markers',  # Draw both lines and markers
                name=fighter,          # Name for the legend (fighter's name)
                line=dict(color=fighter_colors.get(fighter, 'grey'), width=2), # Line color based on fighter
                marker=dict(
                    color=marker_color_list,  # Marker color based on result
                    size=10,                  # Size of the markers
                    symbol=marker_symbol_list,          # Shape of the markers
                ),
                # Custom hover text for each point
                hoverinfo='text',
                text=[f"<b>{row['Fighter Name']}</b><br>" +
                    f"Opponent: {row['Opponent Name_x']}<br>" +
                    f"Result: {row['Result']} ({row['Outcome']})<br>" +
                    f"Opponent Rank: #{int(row['Opponent Ranking']) if pd.notna(row['Opponent Ranking']) else 'N/A'}<br>" +
                    f"Date: {row['Date']:%Y-%m-%d}" 
                    for index, row in fighter_df.iterrows()],
                connectgaps=True
            ))

        # --- Customize Layout ---
        fig.update_layout(
            title="Opponent Ranking at Time of Fight",
            xaxis_title="Date of Fight",
            yaxis_title="Opponent Ranking",
            yaxis=dict(autorange="reversed"),  # Lower rank number is better
            legend_title="Fighter",
            hovermode="closest")
        
        return fig
    
    graph_opp_rank = Graph_Opponent_Ranking(df_fights,fighter_info_1,fighter_info_2)
    st.plotly_chart(graph_opp_rank, use_container_width=True)

    # Opponents cumulated record bar chart avec hue sur Result Win/Lose/Draw 
    def Graph_Opponent_cumulated_Record():
        fig = go.Figure()
        fig.add
        return fig
    
    graph_opp_cumul_record = Graph_Opponent_cumulated_Record()
    st.plotly_chart(graph_opp_cumul_record, use_container_width=True)


    #TEMP affiche les dataframes pour une meilleure lecture pendant la rédaction du code
    st.dataframe(df_fights)
    st.dataframe(df_ranking_history)
    st.dataframe(fighter_info_1)
