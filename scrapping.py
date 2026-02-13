import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import datetime
import re


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
    # pro_fights_list=soup_tapology.find_all("div",attrs={"class":"div mb-2.5 bg-tap_f2 relative rounded-sm","data-division":"pro"})
    pro_fights_list = soup_tapology.select('div.bg-tap_f2.relative.rounded-sm[data-division="pro"]')  #Modification en raison de changement dans le code source

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
