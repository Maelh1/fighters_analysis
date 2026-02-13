import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scrapping import retrieve_all_data

# _________________________ DATA VISUALISATION STREAMLIT _________________________

# __________Header__________

st.set_page_config(
    page_title="MMA Fighters Analysis",
    layout="centered"
)

st.header(":blue[Analyze and compare MMA fighters]",divider="gray")


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


# TEMP affiche les dataframes pour une meilleure lecture pendant la rédaction du code
# st.dataframe(df_fights)
# st.dataframe(df_ranking_history)
# st.dataframe(fighter_info_1)
# st.dataframe(df_tapology)













