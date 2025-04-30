import requests
from bs4 import BeautifulSoup
import pandas as pd


top25_pages_dict={"Heavyweight":"https://www.fightmatrix.com/mma-ranks/heavyweight-265-lbs/",
                  "Light Heavyweight":"https://www.fightmatrix.com/mma-ranks/light-heavyweight-185-205-lbs/",
                  "Middleweight":"https://www.fightmatrix.com/mma-ranks/middleweight/",
                  "Welterweight":"https://www.fightmatrix.com/mma-ranks/welterweight/",
                  "Lightweight":"https://www.fightmatrix.com/mma-ranks/lightweight/",
                  "Featherweight":"https://www.fightmatrix.com/mma-ranks/featherweight/",
                  "Bantamweight":"https://www.fightmatrix.com/mma-ranks/bantamweight/",
                  "Flyweight":"https://www.fightmatrix.com/mma-ranks/flyweight/",
                  "Strawweight":"https://www.fightmatrix.com/mma-ranks/strawweight/",
                  "Women's strawweight":"https://www.fightmatrix.com/mma-ranks/womens-strawweight/",
                  "Women's flyweight":"https://www.fightmatrix.com/mma-ranks/womens-flyweight/",
                  "Women's bantamweight":"https://www.fightmatrix.com/mma-ranks/womens-bantamweight/",
                  "Women's featherweight":"https://www.fightmatrix.com/mma-ranks/womens-featheweight/",
                  }

def get_top25_fighters(url):
    headers ={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("Success")
        html_content = response.text
    else:
        print(f"Error : {response.status_code}")

    soup_top25 = BeautifulSoup(html_content, "html.parser")
    return soup_top25

def retrieve_fighters(soup):
    names_list=[]
    links_list=[]

    top_25=soup.find_all("tr",attrs={"class":"rankRowX","style":"border: 0px solid black"})

    for fighter in top_25:
        name=fighter.find("a",attrs={"class":"sherLink","style":"text-decoration: none;"})
        names_list.append(name.get('name'))
        links_list.append(name.get('href'))
    return names_list,links_list
    
names_list=[]
links_list=[]



def retrieve_alltime_fighters(url_historic_fighters):
    global names_list,links_list
    soup = get_top25_fighters(url_historic_fighters)
    fighters = soup.find_all("tr",attrs={"style":"border: 0px solid black"})
    for fighter in fighters:
        name = fighter.find("a",attrs = {'style':'text-decoration: none;'})
        if not name:
            return names_list,links_list
        names_list.append(name.get('name'))
        links_list.append(name.get('href'))
    return names_list,links_list

    
for category in top25_pages_dict:
    soup=get_top25_fighters(top25_pages_dict[category])
    names_list_temp,links_list_temp=retrieve_fighters(soup)
    names_list.extend(names_list_temp)
    links_list.extend(links_list_temp)
# print("name list:",names_list,"\n")
# print("link list:",links_list,"\n")

names_list,links_list = retrieve_alltime_fighters('https://www.fightmatrix.com/all-time-mma-rankings/all-time-absolute/')

# print("name list 2:",names_list,"\n")
# print("link list 2:",links_list,"\n")


d = {'names':names_list,'links':links_list}
# print("Dictionnaire: ",d,"\n")
df = pd.DataFrame(data=d)
# print("df 1: ",df,"\n")

df = df.sort_values(by=['names'])
# print("df sorted",df,"\n")
df = df.drop_duplicates()

df.to_csv("data/fighters_list.csv", index=False)