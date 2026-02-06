import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import datetime
import re
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit.components.v1 as components


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
        result_list.append(result.text if result else np.nan)

        outcome=fight.find("div",class_=lambda x: x in ["div text-[#29b829] -rotate-90", "div text-[#c1320c] -rotate-90"])
        outcome_list.append(outcome.text if outcome else np.nan)

        name=fight.find("a",attrs={"class":"border-b border-dotted border-tap_6 hover:border-solid"})
        name_list.append(name.text if name else np.nan)

        opp_record=fight.find("span",attrs={"class":"cursor-zoom-in","title":"Opponent Record Before Fight"})
        opp_record_list.append(opp_record.text if opp_record else np.nan) 

        if opp_record and opp_record.text != "N/A":
            opp_record_split=opp_record.text.split('-')  # Split le record en liste pour pouvoir distinguer win, lose, draw: X-Y-Z ->[X,Y,Z]
            opp_win_list.append(int(opp_record_split[0]))
            opp_lose_list.append(int(opp_record_split[1]))
            opp_draw_list.append(int(opp_record_split[2]) if len(opp_record_split)==3 else 0)
        else:
            opp_record_split=[np.nan,np.nan,np.nan] # Prends en compte le cas où aucun record n'est affiché pour l'adversaire (Pas de page tapology, autre art martial,...)
            opp_win_list.append(opp_record_split[0])
            opp_lose_list.append(opp_record_split[1])
            opp_draw_list.append(opp_record_split[2]) 
    
        


        record=fight.find("span",attrs={"class":"cursor-zoom-in","title":"Fighter Record Before Fight"})
        record_list.append(record.text if record else np.nan)
        
        if record and record.text != 'N/A':
            record_split=record.text.split('-')  # Split le record en liste pour pouvoir distinguer win, lose, draw: X-Y-Z ->[X,Y,Z]
            win_list.append(int(record_split[0]))
            lose_list.append(int(record_split[1]))
            draw_list.append(int(record_split[2]) if len(record_split)==3 else 0) 
        else:
            record_split=[np.nan,np.nan,np.nan] # Prends en compte le cas où aucun record n'est affiché pour l'adversaire (Pas de page tapology, autre art martial,...)
            win_list.append(record_split[0])
            lose_list.append(record_split[1])
            draw_list.append(record_split[2]) 


        details=fight.find("div",class_="div text-tap_3 text-[13px] leading-[16px]")
        detail= details.text.replace("\n","") if details else np.nan
        details_list.append(detail)

        year=fight.find("span",class_="text-[13px] md:text-xs text-tap_3 font-bold")
        year_list.append(year.text if year else np.nan)

        month_to_number_dict = {"Jan": "1 ","Feb": "2 ","Mar": "3 ","Apr":  "4 ","May": "5 ","Jun":  "6 ","Jul":  "7 ","Aug":  "8 ","Sep":  "9 ","Oct":  "10 ","Nov":  "11 ","Dec":  "12 "}
        date=fight.find("span",class_="text-xs11 text-neutral-600")
        if date:
            date_split=date.text.split()
            date_split[0]=month_to_number_dict[date_split[0]]
            date="".join(date_split)
        date_list.append(date if date else np.nan)


        org_img = fight.find('img', class_='opacity-70')
        organization_list.append(org_img['alt'] if org_img and 'alt' in org_img.attrs else np.nan)

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
    try:
        fighter_birthday = soup_tapology.find("span", attrs={"data-controller":"age-calc"})
        fighter_birthday = fighter_birthday.text if fighter_birthday else np.nan
        fighter_birthday = datetime.strptime(str(fighter_birthday), '%Y-%m-%d')
        fighter_info["Birthday"] = fighter_birthday
    except:
        fighter_info["Birthday"] = np.nan
        
    try:    
        fighter_age = today.year - fighter_birthday.year - ((today.month, today.day) < (fighter_birthday.month, fighter_birthday.day))
        fighter_info["Age"] = fighter_age
    except:
        fighter_info["Age"] = np.nan
        
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
    ranking=ranking.text if ranking else np.nan
    fighter_info["Ranking"]=ranking

    finish_perc_div=soup_fightmatrix.find_all(string=re.compile('Win Finish %: '))
    finish_perc_div = [i.parent for i in finish_perc_div]
    finish_perc=finish_perc_div[0].find("strong")
    finish_perc=finish_perc.text if finish_perc else np.nan
    fighter_info["Finish %"]=finish_perc

    streak_div=soup_tapology.find("strong",string="Current MMA Streak:")
    streak_div=streak_div.parent
    streak=streak_div.find("span")
    streak=streak.text if streak else np.nan
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
        opponent_name_list.append(opponent_name.text if opponent_name else np.nan)

        opponent_ranking = fight.find("em")
        opponent_ranking_list.append(opponent_ranking.text if opponent_ranking else np.nan)


    fights_div = soup_body.find_all("td",class_=lambda x: x and ("tdRank" in x),attrs={"style":"text-align: left; padding-top: 5px; padding-left: 2px; padding-right: 2px; padding-bottom: 5px;"})

    for fight in fights_div:

        if fight.find("a",class_="sherLink"):
            date=fight.find("em")
            date_list.append(date.text.split(",")[1].strip().replace("1st", "1").replace("2nd", "2").replace("3rd", "3").replace("th", "") if date else np.nan)

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
            date_list.append(date.text if date else np.nan)

            ranking=rank.find("td",string=lambda x:x and "#" in x)
            rank_list.append(ranking.text if ranking else np.nan)

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
import streamlit as st

st.set_page_config(
    page_title="MMA Fighters Analysis",
    layout="wide"
)

st.markdown("""
<style>

/* Hide default header */
header[data-testid="stHeader"] {
    display: none;
}

/* Custom header */
#mma-header {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 96px;
    background: linear-gradient(90deg, #f4f6f8, #e9edf2);
    color: #1f2933;
    padding: 10px 24px;
    z-index: 999999;

    display: flex;
    flex-direction: column;
    justify-content: center;

    box-shadow: 0 2px 8px rgba(0,0,0,0.3);

    transition: transform 0.3s ease;
}

/* Hidden */
#mma-header.hidden {
    transform: translateY(-100%);
}

#mma-header h1 {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
}

#mma-header p {
    margin: 0;
    font-size: 12px;
    opacity: 0.8;
}

#mma-header a {
    color: #4fc3f7;
    text-decoration: none;
}

#mma-header a:hover {
    text-decoration: underline;
}

/* Push content */
section.main > div {
    padding-top: 70px !important;
}

</style>

<div id="mma-header">
    <h1>Analyze and compare MMA fighters</h1>
    <p>
        Thank you to
        <a href="https://www.fightmatrix.com" target="_blank">FightMatrix</a>
        and
        <a href="https://www.tapology.com" target="_blank">Tapology</a>
    </p>
</div>

<script>
let lastScroll = 0;
const header = document.getElementById("mma-header");

window.addEventListener("scroll", () => {

    const current = window.pageYOffset;

    if (current > lastScroll && current > 80) {
        header.classList.add("hidden");
    } else {
        header.classList.remove("hidden");
    }

    lastScroll = current;
});
</script>
""", unsafe_allow_html=True)


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
    fighter1_selectbox = st.selectbox("Select fighter 1", fighter_propositions)
    if fighter1_selectbox == "URL Fightmatrix":
        st.markdown("""
        <style>
        .info-tooltip {
        display: inline-block;
        position: relative;
        font-size: 16px;
        margin-left: 6px;
        color: #888;
        cursor: pointer;
        }

        .info-tooltip .video-popup {
        visibility: hidden;
        width: 900px;
        position: absolute;
        top: 200%;
        left: -10px;
        z-index: 1000;
        border-radius: 8px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        transition: opacity 0.3s;
        opacity: 0;
        }

        .info-tooltip:hover .video-popup {
        visibility: visible;
        opacity: 1;
    

        video {
        width: 100%;
        height: auto;
        pointer-events: none;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("""
        <label for="fighter_input">
        Or paste their fightmatrix page url
        <span class="info-tooltip">💡
            <span class="video-popup">
            <video autoplay muted loop>
                <source src="https://raw.githubusercontent.com/Maelh1/fighters_analysis/main/video/tuto.mp4" type="video/mp4">
                Your browser does not support the video tag.
            </video>
            </span>
        </span>
        </label>
        """, unsafe_allow_html=True)

        fighter1_url = st.text_input("",key="fighter_input")
    else:
        fighter1_url =  "https://www.fightmatrix.com"+name_link_dict[fighter1_selectbox]

with right_col:
    fighter2_selectbox = st.selectbox("Select fighter 2", fighter_propositions)
    if fighter2_selectbox == "URL Fightmatrix":
        st.markdown("""
        <style>
        .info-tooltip {
        display: inline-block;
        position: relative;
        font-size: 16px;
        margin-left: 6px;
        color: #888;
        cursor: pointer;
        }

        .info-tooltip .video-popup {
        visibility: hidden;
        width: 600px;
        position: absolute;
        top: 100%;
        left: -10px;
        z-index: 1000;
        border-radius: 8px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        transition: opacity 0.3s;
        opacity: 0;
        }

        .info-tooltip:hover .video-popup {
        visibility: visible;
        opacity: 1;
        }
        #video-container {
        position: relative;
        display: inline-block;
        }

        #tooltip-video {
        display: none;
        position: absolute;
        left: 100%;
        top: -20px;
        z-index: 10;
        width: 300px;
        border: 1px solid #ccc;
        border-radius: 10px;
        overflow: hidden;
        }

        #video-container:hover #tooltip-video {
        display: block;
        }

        video {
        width: 100%;
        height: auto;
        pointer-events: none;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("""
        <label for="fighter_input">
        Or paste their fightmatrix page url
        <span class="info-tooltip">💡
            <span class="video-popup">
            <video width="100%" autoplay muted loop>
                <source src="https://raw.githubusercontent.com/Maelh1/fighters_analysis/main/video/tuto.mp4" type="video/mp4">
                Your browser does not support the video tag.
            </video>
            </span>
        </span>
        </label>
        """, unsafe_allow_html=True)
        fighter2_url = st.text_input("")
    else:
        fighter2_url = "https://www.fightmatrix.com"+name_link_dict[fighter2_selectbox]

compare_button=st.button("Compare" if fighter1_url and fighter2_url else "Present")




# _________Display results_________
if compare_button:
    # Get data 
    try:
        df_tapology_1,fighter_info_1,df_fightmatrix_1,df_ranking_history_1 = dict_url_to_df[fighter1_url][0],dict_url_to_df[fighter1_url][1],dict_url_to_df[fighter1_url][3],dict_url_to_df[fighter1_url][4]
    except:
        df_tapology_1,fighter_info_1,df_fightmatrix_1,df_ranking_history_1 =retrieve_all_data(fighter1_url)
        dict_url_to_df[fighter1_url] = [df_tapology_1.copy(),fighter_info_1.copy(),df_fightmatrix_1.copy(),df_ranking_history_1.copy()]
    try:
        df_tapology_2,fighter_info_2,df_fightmatrix_2,df_ranking_history_2 = dict_url_to_df[fighter2_url][0],dict_url_to_df[fighter2_url][1],dict_url_to_df[fighter2_url][3],dict_url_to_df[fighter2_url][4]
    except:
        df_tapology_2,fighter_info_2,df_fightmatrix_2,df_ranking_history_2 =retrieve_all_data(fighter2_url)
        dict_url_to_df[fighter2_url] =[df_tapology_2.copy(),fighter_info_2.copy(),df_fightmatrix_2.copy(),df_ranking_history_2.copy()]


    # Cleaning dataframe
    def Df_cleaning(df_ranking_history,fighter_info,df_tapology,df_fightmatrix):
        df_ranking_history["Fighter Name"]=fighter_info["Name"]
        df_tapology=df_tapology.loc[df_tapology["Art"]=="MMA"]
        df_fights=pd.merge(df_tapology, df_fightmatrix,how="right",on = 'Date')
        df_fights["Fighter Name"] = fighter_info["Name"]
        return df_fights, df_tapology
    
    df_fights_1, df_tapology_1 = Df_cleaning(df_ranking_history_1,fighter_info_1,df_tapology_1,df_fightmatrix_1)
    df_fights_2, df_tapology_2 = Df_cleaning(df_ranking_history_2,fighter_info_2,df_tapology_2,df_fightmatrix_2)


    # st.dataframe(df_tapology_1) #Temp
    # st.dataframe(df_fightmatrix_1)#Temp
    # st.dataframe(df_fights_1) #Temp
    # st.dataframe(df_ranking_history_1) # TEMP



    df_ranking_history = pd.concat([df_ranking_history_1,df_ranking_history_2],ignore_index=True)
    df_fights = pd.concat([df_fights_1,df_fights_2],ignore_index=True)

    df_fights=df_fights.loc[df_fights["Art"]=="MMA"] # Select only MMA fights
    df_tapology = pd.concat([df_tapology_1,df_tapology_2],ignore_index = True)
  
    #_________Présentation_________
    # Colonnes pour les images uniquement
    def Presentation(fighter_info_1,fighter_info_2,df_fights_1,df_fights_2,df_ranking_history_1,df_ranking_history_2):
        left_img_col, right_img_col = st.columns([0.2, 0.2],gap="large",vertical_alignment= "bottom",border = True)

        with left_img_col:
            st.image(fighter_info_1["Picture"], use_container_width=True)

        with right_img_col:
            st.image(fighter_info_2["Picture"], use_container_width=True)

        # Préparation des données
        streak_emojis_f1 = ''.join(['🟢' if i == 'W' else '🔴' if i == 'L' else '⚪' if i == 'D' else '❓' for i in fighter_info_1['Last 5']])
        streak_emojis_f2 = ''.join(['🟢' if i == 'W' else '🔴' if i == 'L' else '⚪' if i == 'D' else '❓' for i in fighter_info_2['Last 5']])

        def Opponent_Cumulated_Record(df_tapology):
            df_tapology = df_tapology[df_tapology['Result'].isin( ['W','L','D'])]
            wins = int(df_tapology["Opponent Win"].sum())
            loss = int(df_tapology["Opponent Lose"].sum())
            draws = int(df_tapology["Opponent draw"].sum())
            record = f"{wins}-{loss}-{draws}"
            win_rate = round(wins/(wins+loss+draws)*100,1)
            win_rate = f"({win_rate}%)"
            return record, win_rate
        
        f1_opp_cumul_record, f1_opp_winrate = Opponent_Cumulated_Record(df_tapology_1)
        f2_opp_cumul_record, f2_opp_winrate = Opponent_Cumulated_Record(df_tapology_2)

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
            <tr><td colspan="3" class="divider"></td></tr>
            <tr>
                <td>{f1_opp_cumul_record} <BR> {f1_opp_winrate}</td>
                <td class="header">Opponents cumulated record <BR> (% Win) </td>
                <td>{f2_opp_cumul_record} <BR> {f2_opp_winrate}</td>
            </tr>
        </table>
        """
        return html_table
    
    html_table = Presentation(fighter_info_1,fighter_info_2,df_fights_1,df_fights_2,df_ranking_history_1,df_ranking_history_2)

    # Afficher le tableau HTML
    st.markdown(html_table, unsafe_allow_html=True)

    #_________GRAPHS_________

    # Fighters Win methods proportions
    def create_victory_defeat_pie_charts(df_tapology1, df_tapology2,df_fight1,df_fight2):
        fighter1_name = df_fight1["Fighter Name"].unique()[0]
        fighter2_name = df_fight2["Fighter Name"].unique()[0]

        # Créer une figure avec 2x2 sous-graphiques
        fig = make_subplots(
            rows=2, cols=2,
            specs=[[{'type': 'pie'}, {'type': 'pie'}],
                [{'type': 'pie'}, {'type': 'pie'}]],
            subplot_titles=(
                f"{fighter1_name} Victories", 
                f"{fighter2_name} Victories",
                f"{fighter1_name} Defeats", 
                f"{fighter2_name} Defeats"
            )
        )
        
        # Filtrer les données pour les victoires et défaites de chaque combattant
        wins_f1 = df_tapology1[df_tapology1['Result'] == 'W']
        losses_f1 = df_tapology1[df_tapology1['Result'] == 'L']
        wins_f2 = df_tapology2[df_tapology2['Result'] == 'W']
        losses_f2 = df_tapology2[df_tapology2['Result'] == 'L']
        
        # Compter les méthodes de victoire pour fighter1
        win_methods_f1 = wins_f1['Outcome'].value_counts()
        win_methods_f1_labels = win_methods_f1.index.tolist()
        win_methods_f1_values = win_methods_f1.values.tolist()
        
        # Compter les méthodes de défaite pour fighter1
        loss_methods_f1 = losses_f1['Outcome'].value_counts()
        loss_methods_f1_labels = loss_methods_f1.index.tolist()
        loss_methods_f1_values = loss_methods_f1.values.tolist()
        
        # Compter les méthodes de victoire pour fighter2
        win_methods_f2 = wins_f2['Outcome'].value_counts()
        win_methods_f2_labels = win_methods_f2.index.tolist()
        win_methods_f2_values = win_methods_f2.values.tolist()
        
        # Compter les méthodes de défaite pour fighter2
        loss_methods_f2 = losses_f2['Outcome'].value_counts()
        loss_methods_f2_labels = loss_methods_f2.index.tolist()
        loss_methods_f2_values = loss_methods_f2.values.tolist()
        
        # Couleurs pour les méthodes de victoire/défaite
        victory_colors = {
            'TKO': '#264653',  # Rouge pour TKO
            'SUB': '#2A9D8F',  # Bleu pour soumission
            'DEC': '#E9C46A',  # Vert pour décision
            }
        
        # Pour assurer que toutes les méthodes ont une couleur
        all_methods = set(
            win_methods_f1_labels + loss_methods_f1_labels +
            win_methods_f2_labels + loss_methods_f2_labels
        )
        
        # Couleurs par défaut pour les méthodes non listées
        colors = ['#FF4136', '#FF851B', '#0074D9', '#2ECC40', '#AAAAAA', '#B10DC9', '#FF6EFF', '#FFDC00']
        method_colors = {method: victory_colors.get(method, colors[i % len(colors)]) 
                        for i, method in enumerate(all_methods)}
        
        # Ajouter les camemberts
        # Victoires Fighter 1 [0][0]
        fig.add_trace(
            go.Pie(
                labels=win_methods_f1_labels, 
                values=win_methods_f1_values,
                name=f"{fighter1_name} Wins",
                marker=dict(colors=[method_colors[method] for method in win_methods_f1_labels]),
                textinfo='label+percent',
                hoverinfo='label+value+percent',
                textfont_size=12,
                hole=.3,
            ),
            row=1, col=1
        )
        
        # Victoires Fighter 2 [0][1]
        fig.add_trace(
            go.Pie(
                labels=win_methods_f2_labels, 
                values=win_methods_f2_values,
                name=f"{fighter2_name} Wins",
                marker=dict(colors=[method_colors[method] for method in win_methods_f2_labels]),
                textinfo='label+percent',
                hoverinfo='label+value+percent',
                textfont_size=12,
                hole=.3,
            ),
            row=1, col=2
        )
        
        # Défaites Fighter 1 [1][0]
        fig.add_trace(
            go.Pie(
                labels=loss_methods_f1_labels, 
                values=loss_methods_f1_values,
                name=f"{fighter1_name} Losses",
                marker=dict(colors=[method_colors[method] for method in loss_methods_f1_labels]),
                textinfo='label+percent',
                hoverinfo='label+value+percent',
                textfont_size=12,
                hole=.3,
            ),
            row=2, col=1
        )
        
        # Défaites Fighter 2 [1][1]
        fig.add_trace(
            go.Pie(
                labels=loss_methods_f2_labels, 
                values=loss_methods_f2_values,
                name=f"{fighter2_name} Losses",
                marker=dict(colors=[method_colors[method] for method in loss_methods_f2_labels]),
                textinfo='label+percent',
                hoverinfo='label+value+percent',
                textfont_size=12,
                hole=.3,
            ),
            row=2, col=2
        )
        
        # Mise à jour de la mise en page
        fig.update_layout(
            title={
                'text': f"Victory & Defeat Methods: {fighter1_name} vs {fighter2_name}",
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 22}
            },
            # Ajuster les annotations (titres des sous-graphiques)
            annotations=[
                dict(x=0.25, y=0.995, showarrow=False, text=f"{fighter1_name} Victories", font_size=16),
                dict(x=0.75, y=0.995, showarrow=False, text=f"{fighter2_name} Victories", font_size=16),
                dict(x=0.25, y=0.475, showarrow=False, text=f"{fighter1_name} Defeats", font_size=16),
                dict(x=0.75, y=0.475, showarrow=False, text=f"{fighter2_name} Defeats", font_size=16)
            ],
            height=800,  # Hauteur en pixels
            width=1000,  # Largeur en pixels
            showlegend=False,  # Masquer la légende globale car les étiquettes sont sur les camemberts
        )
        
        # Ajouter une annotation pour indiquer les couleurs des méthodes
        method_colors_list = list(method_colors.items())
        for i, (method, color) in enumerate(method_colors_list):
            fig.add_annotation(
                x=1.1,  # Position horizontale (à droite du graphique)
                y=0.5 - i * 0.1,  # Position verticale
                xref="paper",
                yref="paper",
                text=f"{method}",
                showarrow=False,
                font=dict(color=color, size=12),
                align="left"
            )
        
        return fig

    fig = create_victory_defeat_pie_charts(df_tapology_1, df_tapology_2, df_fights_1, df_fights_2)
    st.plotly_chart(fig, use_container_width=True)

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
                title={'text' : "Fighters Ranking Evolution",
                    'x' : 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                xaxis_title="Date",
                yaxis_title="Ranking",
                yaxis=dict(autorange="reversed"),  # Lower rank number is better
                legend = {'yanchor' : 'bottom',
                        'y' : -0.2,
                        'xanchor' : 'left',
                        'x' : 0,
                        'orientation' : 'h'
                        },
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
            title={'text' : "Opponent Ranking at Time of Fight",
                   "xanchor": 'center',
                   "yanchor": 'top',
                   "x": 0.5},
            xaxis_title="Date of Fight",
            yaxis_title="Opponent Ranking",
            yaxis=dict(autorange="reversed"),  # Lower rank number is better
            legend = {'yanchor' : 'bottom',
                    'y' : -0.2,
                    'xanchor' : 'left',
                    'x' : 0,
                    'orientation' : 'h'
                    },
            hovermode="closest")
        
        return fig
    
    graph_opp_rank = Graph_Opponent_Ranking(df_fights,fighter_info_1,fighter_info_2)
    st.plotly_chart(graph_opp_rank, use_container_width=True)

    # Opponents cumulated record bar chart avec hue sur Result Win/Lose/Draw 

    def create_opponent_stats_comparison(df_tapology1, df_tapology2, df_fights1, df_fights2):
        # Calculer les sommes pour chaque combattant
        sum_f1 = df_tapology1[['Opponent Win', 'Opponent Lose', 'Opponent draw']].sum()
        sum_f2 = df_tapology2[['Opponent Win', 'Opponent Lose', 'Opponent draw']].sum()

        fighter1_name = df_fights1['Fighter Name'].unique()[0]
        fighter2_name = df_fights2['Fighter Name'].unique()[0]

        # Créer la figure
        fig = go.Figure()
        
        # Catégories
        categories = ['Opponent Win', 'Opponent Lose', 'Opponent Draw']
        
        # Positions des barres sur l'axe x
        x_positions = np.arange(len(categories))
        bar_width = 0.35
        
        # Ajouter les barres pour Fighter 1
        fig.add_trace(go.Bar(
            x=x_positions - bar_width/2,
            y=[sum_f1['Opponent Win'], sum_f1['Opponent Lose'], sum_f1['Opponent draw']],
            width=bar_width,
            name=fighter1_name,
            marker_color='red',
            text=[int(sum_f1['Opponent Win']), int(sum_f1['Opponent Lose']), int(sum_f1['Opponent draw'])],
            textposition='auto'
        ))
        
        # Ajouter les barres pour Fighter 2
        fig.add_trace(go.Bar(
            x=x_positions + bar_width/2,
            y=[sum_f2['Opponent Win'], sum_f2['Opponent Lose'], sum_f2['Opponent draw']],
            width=bar_width,
            name=fighter2_name,
            marker_color='blue',
            text=[int(sum_f2['Opponent Win']), int(sum_f2['Opponent Lose']), int(sum_f2['Opponent draw'])],
            textposition='auto'
        ))
        
        # Mise en page
        fig.update_layout(
            title={
                'text': "Opponent Records Comparison",
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis=dict(
                tickmode='array',
                tickvals=x_positions,
                ticktext=categories,
                title=""
            ),
            yaxis=dict(
                title="Sum"
            ),
            legend={
                'orientation': 'h',
                'yanchor': 'bottom',
                'y': -0.2,
                'xanchor': 'left',
                'x': 0
            },
            barmode='group'
        )
        
        return fig

    # Utilisation
    fig = create_opponent_stats_comparison(df_tapology_1, df_tapology_2, df_fights_1, df_fights_2)
    st.plotly_chart(fig, use_container_width=True)
    

st.markdown("""
<style>
.tooltip-icon {
  position: fixed;
  bottom: 20px;
  left: 20px;
  font-size: 22px;
  color: #666;
  cursor: pointer;
  z-index: 1000;
}

.tooltip-icon .tooltiptext {
  visibility: hidden;
  width: 340px;
  background-color: #fefefe;
  color: #333;
  text-align: left;
  border-radius: 8px;
  padding: 14px;
  position: absolute;
  bottom: 125%;
  left: 0;
  opacity: 0;
  transition: opacity 0.3s;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  font-size: 13px;
}

.tooltip-icon:hover .tooltiptext {
  visibility: visible;
  opacity: 1;
}
</style>

<div class="tooltip-icon">ℹ️
  <div class="tooltiptext">
    This application is developed strictly for educational and non-commercial purposes.<br><br>
    It does not collect, store, or share any personal user data. No cookies or analytics are used.<br><br>
    All data shown is from public sources (e.g., FightMatrix, Tapology) and is used for learning only.<br><br>
    The developer claims no ownership of third-party data or trademarks.<br><br>
    Provided “as is”, without warranties. Contact via GitHub for removal requests.
  </div>
</div>
""", unsafe_allow_html=True)


    #TEMP affiche les dataframes pour une meilleure lecture pendant la rédaction du code
    # st.dataframe(df_fights)
    # st.dataframe(df_ranking_history)
    # st.dataframe(fighter_info_1)
    # st.dataframe(df_tapology)












