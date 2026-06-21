import streamlit as st
import pandas as pd
import os
import base64

st.set_page_config(layout="wide")

hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .viewerBadge_container__1QS1Y, [data-testid="stViewerBadge"] {display: none !important;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# Логотип F1 ______________________________________________________________________________________________________________________
st.markdown(
    '<div style="text-align: right; padding-right: 40px; padding-top: 35px;">'
    '<img src="data:image/png;base64,' + base64.b64encode(open("logo_team/f1_logo.png", "rb").read()).decode() + '" width="130">'
    '</div>', 
    unsafe_allow_html=True
)

# Функції та Логотипи Команд ______________________________________________________________________________________________________
LOGOS_DICT = {
        "rbr": "logo_team/rbr.png", "fer": "logo_team/fer.png",
        "mer": "logo_team/mer.png", "mcl": "logo_team/mcl.png",
        "alpine": "logo_team/alpine.png", "amr": "logo_team/amr.png",
        "at": "logo_team/at.png", "alfa": "logo_team/alfa.png",
        "williams": "logo_team/williams.png", "haas": "logo_team/haas.png"
    }
ENCODED_LOGOS = {}
for code, file_path in LOGOS_DICT.items():
    if os.path.exists(file_path):
        with open(file_path, "rb") as img_f:
            ENCODED_LOGOS[code] = base64.b64encode(img_f.read()).decode()

def format_team_logo(team_code, width=35, height=25):
    if pd.isna(team_code):
        return ""
    code = str(team_code).strip().lower()
    if code in ENCODED_LOGOS:
        return f'<img src="data:image/png;base64,{ENCODED_LOGOS[code]}" style="width: {width}px; height: {height}px; object-fit: contain; vertical-align: middle;">'
    return team_code

def format_driver_name(full_name):
    if pd.isna(full_name):
        return full_name
    parts = str(full_name).split()
    if len(parts) >= 3:
        last_name = " ".join(parts[2:])
        return f"{parts[0]} <i>{parts[1]}</i> <b>{last_name}</b>"
    return full_name


# ТВІЙ БЕКЕНД: ГОЛОВНА ФУНКЦІЯ ОБРОБКИ ТА СОРТУВАННЯ ДАНИХ _____________________________________________________________________________
def get_sorted_standings(sheet_id):
    POINTS_SYSTEM_RACE = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
    POINTS_SYSTEM_SPRINT = {1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1}

    csv_url_races = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Races"
    csv_url_status = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Status_race"
    
    df_races_raw = pd.read_csv(csv_url_races, dtype=str)
    df_status = pd.read_csv(csv_url_status)

    base_columns = ['ID', 'TEAM']
    active_race = df_status[df_status['STATUS'] == 1]['RACE'].tolist()
    
    columns_to_keep = []
    for col in df_races_raw.columns:
        if col in base_columns + active_race:
            columns_to_keep.append(col)
            
    df_filtered = df_races_raw[columns_to_keep]

    # Створення карток пілотів
    pilot_list = []
    for index, row in df_filtered.iterrows():
        pilot_card = {
            "ID" : row["ID"],
            "TEAM" : row["TEAM"],
            "PTS." : 0
        }
        for i in range(1, 21):  # ТУТ ВИПРАВЛЕНО: тепер створює від P1 до P20 залізобетонно
            pilot_card[f"P{i}"] = 0      
        pilot_list.append(pilot_card)

    # Підрахунок очок та місць
    for pilot in pilot_list:
        pilot_row = df_filtered[df_filtered["ID"] == pilot["ID"]].iloc[0]
        
        for col in df_filtered.columns:
            if col in base_columns:
                continue

            val = str(pilot_row[col]).strip()
            if val not in ["nan", "None", "-", "0", "DNF", ""]:

                fastest_lap = False
                if '*' in val:
                    fastest_lap = True
                    val = val.replace("*", "").strip()

                pos = int(float(val))

                if 1 <= pos <= 20:
                    if col.endswith("sprint"):
                        if pos in POINTS_SYSTEM_SPRINT:
                            pilot["PTS."] += POINTS_SYSTEM_SPRINT[pos]
                    else:
                        pilot[f"P{pos}"] += 1
                        if pos in POINTS_SYSTEM_RACE:
                            pilot["PTS."] += POINTS_SYSTEM_RACE[pos]
                        
                        if fastest_lap and 1 <= pos <= 10:
                            pilot["PTS."] += 1

    # Перетворення списку у DataFrame та сортування
    df_sorted = pd.DataFrame(pilot_list)
    sorting_columns = ["PTS."] + [f"P{i}" for i in range(1, 21)]
    df_sorted = df_sorted.sort_values(by=sorting_columns, ascending=False).reset_index(drop=True)
    df_sorted.insert(0, "POS.", range(1, len(df_sorted) + 1))
    
    return df_sorted, df_filtered, active_race, base_columns


# Оптимізовані глобальні стилі CSS _______________________________________________________________________________________________
st.html(
    """
    <style>
    .stAppHeader, [data-testid="stAppHeader"] { height: 0px !important; min-height: 0px !important; background: transparent !important; }    
    .stMain, [data-testid="stMain"], .block-container, [data-testid="stBlockContainer"], .stTabs, [data-testid="stTabs"] { padding-top: 0px !important; margin-top: 0px !important; }
    .stAppToolbar, .stHeading a { display: none !important; }
    .stHeading h2 { text-align: center !important; } 
    .table-container { margin: 20px auto !important; width: 100% !important; max-width: 600px !important; border: 1px solid black; border-radius: 10px; overflow: hidden; }
    table { border-collapse: collapse !important; width: 100% !important; border: none !important; margin: 0px !important; table-layout: fixed !important; }
    th, td { border: none !important; padding: 8px 4px !important; text-align: center !important; vertical-align: middle !important; word-wrap: break-word !important; }
    th { font-size: 10px !important; font-weight: normal !important; color: #8E8E93 !important; text-transform: uppercase; letter-spacing: 0.5px; padding: 6px 4px !important; }
    </style>
    """
)

SHEET_ID = "11Hz0Vghyi6s3znwhw0s6c97k66vEpLgP-b5Obaqsg8s"

# ТВІЙ ОДИН РЯДОК, ЯКИЙ РОБИТЬ ВСЮ МАГІЮ НАПОЧАТКУ ______________________________________________________________________________
df_sorted_results, df_filtered_races, active_race, base_columns = get_sorted_standings(SHEET_ID)


tab1, tab2, tab3 = st.tabs(["Drivers", "Races", "Teams"])


# ВКЛАДКА 1: DRIVERS ____________________________________________________________________________________________________________
with tab1:
    st.header("*Drivers' Standings*")
    st.html(
        """
        <style>
        .drivers-table th:nth-child(1), .drivers-table td:nth-child(1) { width: 12% !important; } /* POS. */
        .drivers-table th:nth-child(2), .drivers-table td:nth-child(2) { width: 12% !important; } /* ID */
        .drivers-table th:nth-child(4), .drivers-table td:nth-child(4) { width: 15% !important; } /* TEAM */
        .drivers-table th:nth-child(5), .drivers-table td:nth-child(5) { width: 18% !important; } /* POINTS */
        .drivers-table th:nth-child(3), .drivers-table td:nth-child(3) { width: 43% !important; text-align: left !important; padding-left: 10px !important; }
        </style>
        <div style="height: 2px; width: 90%; margin: 10px auto 10px auto; background: linear-gradient(to right, transparent, #FF4B4B, transparent);"></div>
        """
    )
    # Завантажуємо повні імена з вкладки Drivers
    csv_url_drivers = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Drivers"
    df_drivers = pd.read_csv(csv_url_drivers)
    
    # Поєднуємо імена з нашими розрахованими результатами через ID і сортуємо по POS.
    df_drivers = pd.merge(df_drivers, df_sorted_results[['ID', 'POS.', 'PTS.']], on='ID', how='left')
    df_drivers = df_drivers.sort_values(by='POS.').reset_index(drop=True)
    
    if 'TEAM' in df_drivers.columns:
        df_drivers['TEAM'] = df_drivers['TEAM'].apply(format_team_logo)
    if 'DRIVER' in df_drivers.columns:
        df_drivers['DRIVER'] = df_drivers['DRIVER'].apply(format_driver_name)

    # Показуємо тільки потрібні колонки користувачу
    df_drivers_visible = df_drivers[['POS.', 'ID', 'DRIVER', 'TEAM', 'PTS.']]
    
    html_table = df_drivers_visible.to_html(escape=False, index=False)
    st.markdown(f'<div class="table-container drivers-table">{html_table}</div>', unsafe_allow_html=True)



# ВКЛАДКА 2: RACES ______________________________________________________________________________________________________________
with tab2:
    st.header("*Race Results*")
    st.html(
        """
        <style>
        /* Головний контейнер таблиці */
        .races-container table { 
            table-layout: fixed !important; 
            width: auto !important;         /* Таблиця не розтягується штучно на весь екран */
            min-width: 100% !important;     
            border-collapse: separate !important; 
            border-spacing: 0; 
        }
        .races-container th, .races-container td { 
            font-size: 11px !important; 
            padding: 6px 4px !important; 
            white-space: nowrap !important; 
            vertical-align: middle !important; 
        }
        .races-container td sup { font-size: 9px !important; color: #FF4B4B !important; font-weight: bold !important; margin-left: 1px; }
        
        /* Заморожування стовпців ліворуч (Sticky) */
        .races-container th:nth-child(1), .races-container td:nth-child(1) { position: sticky !important; width: 35px !important; min-width: 35px !important; max-width: 35px !important; left: 0px !important; background-color: #0E1117 !important; z-index: 3 !important; text-align: center !important; }
        .races-container th:nth-child(2), .races-container td:nth-child(2) { position: sticky !important; width: 45px !important; min-width: 45px !important; max-width: 45px !important; left: 35px !important; background-color: #0E1117 !important; z-index: 3 !important; font-size: 13px !important; font-weight: bold !important; text-align: center !important; }
        .races-container th:nth-child(3), .races-container td:nth-child(3) { position: sticky !important; width: 45px !important; min-width: 45px !important; max-width: 45px !important; left: 80px !important; background-color: #0E1117 !important; z-index: 3 !important; }
        .races-container th:nth-child(4), .races-container td:nth-child(4) { position: sticky !important; width: 50px !important; min-width: 50px !important; max-width: 50px !important; left: 125px !important; background-color: #0E1117 !important; z-index: 3 !important; font-size: 13px !important; font-weight: bold !important; }

        /* 🛠️ ФІКСАТОР ШИРИНИ ДЛЯ ВСІХ СТОВПЦІВ ГОНОК (замість універсальних виключень) */
        .races-container th:nth-child(n+5):not(:last-child),
        .races-container td:nth-child(n+5):not(:last-child) {
            width: 85px !important;
            min-width: 85px !important;
            max-width: 85px !important;
            text-align: center !important;
        }

        /* Останній порожній стовпець-заглушка */
        .races-container th:last-child, .races-container td:last-child {
            width: auto !important;
            min-width: 0px !important;
            padding: 0 !important;
        }
        </style>
        <div style="height: 2px; width: 90%; margin: 10px auto; background: linear-gradient(to right, transparent, #FF4B4B, transparent);"></div>
        """
    )
    
    # Беремо за основу відсортованих лідерів
    df_races_display = df_sorted_results[['POS.', 'ID', 'TEAM', 'PTS.']].copy()
    
    race_names_mapping = {
        "Bahrain": "🇧🇭<br>Bahrain",
        "Saudi Arabian": "🇸🇦<br>Saudi Arabian",
        "Australia": "🇦🇺<br>Australia",
        "Emilia Romagna sprint": "🇮🇹<br>Emilia Romagna",  # Перевір, чи у таблиці немає дефіса: "Emilia-Romagna"
        "Miami": "🇺🇸<br>Miami",
        "Spain": "🇪🇸<br>Spain",
        "Monaco": "🇲🇨<br>Monaco",
        "Azerbaijan": "🇦🇿<br>Azerbaijan",
        "Canada": "🇨🇦<br>Canada",
        "Great Britain": "🇬🇧<br>Great Britain",          # Перевір, як саме в таблиці (може бути Great Britain або UK)
        "Austria sprint": "🇦🇹<br>Austria",
        "France": "🇫🇷<br>France",
        "Hungary": "🇭🇺<br>Hungary",
        "Belgium": "🇧🇪<br>Belgium",
        "Netherlands": "🇳🇱<br>Netherlands",
        "Italy": "🇮🇹<br>Italy",
        "Singapore": "🇸🇬<br>Singapore",
        "Japan": "🇯🇵<br>Japan",
        "United States": "🇺🇸<br>United States",
        "Mexico": "🇲🇽<br>Mexico",
        "Sao Paulo sprint": "🇧🇷<br>Sao Paulo",
        "Abu Dhabi": "🇦🇪<br>Abu Dhabi"
    }

    # Очищаємо сирі результати гонок для відображення
    df_clean_races = df_filtered_races.copy()
    for col in df_clean_races.columns:
        if col not in base_columns:
            df_clean_races[col] = df_clean_races[col].apply(lambda x: str(x)[:-2] if str(x).endswith('.0') else str(x))
            df_clean_races[col] = df_clean_races[col].apply(lambda x: "-" if x in ['nan', 'None'] else x)
            df_clean_races[col] = df_clean_races[col].apply(lambda x: "DNF" if str(x).strip() == "0" else x)

            df_clean_races[col] = df_clean_races[col].apply(lambda x: f"{str(x).replace('*', '')} <sup>⏱️</sup>" if str(x).endswith('*') else x)


    # Склеюємо Спринт та Гонку (sup індекс)
    original_columns = list(df_clean_races.columns)
    columns_to_drop = []

    for i in range(len(original_columns)):
        col_name = str(original_columns[i]).strip()
        if col_name.lower().endswith('race') and i > 1:
            sprint_col = original_columns[i-1]
            race_col = original_columns[i]
            
            combined_values = []
            for idx, row in df_clean_races.iterrows():
                sprint_val = str(row[sprint_col]).strip()
                race_val = str(row[race_col]).strip()
                
                if sprint_val == "" and race_val == "":
                    combined_values.append("")
                elif sprint_val == "-" and race_val == "-":
                    combined_values.append("-")
                elif sprint_val and sprint_val != "-":
                    combined_values.append(f"{race_val}<sup>{sprint_val}</sup>")
                else:
                    combined_values.append(race_val)
            
            df_clean_races[sprint_col] = combined_values
            columns_to_drop.append(race_col)

    df_clean_races = df_clean_races.drop(columns=columns_to_drop)

    # Об'єднуємо відсортованих водіїв з результатами етапів
    df_races_display = pd.merge(df_races_display, df_clean_races.drop(columns=['TEAM']), on='ID', how='left')

    if 'TEAM' in df_races_display.columns:
        df_races_display['TEAM'] = df_races_display['TEAM'].apply(format_team_logo, width=30, height=15)
        
    # Переставляємо стовпці у зручному порядку для Sticky: POS -> ID -> TEAM -> PTS. -> ГОНКИ
    cols_order = ['POS.', 'ID', 'TEAM', 'PTS.'] + [c for c in df_races_display.columns if c not in ['POS.', 'ID', 'TEAM', 'PTS.']]
    df_races_display = df_races_display[cols_order]
    
    # 🛠️ Створюємо стовпець-заглушку в самому кінці
    df_races_display[' '] = ''

    # Перейменовуємо системні заголовки для перших стовпців під Sticky-ефект
    df_races_display = df_races_display.rename(columns={'POS.': ' ', 'ID': '  ', 'TEAM': '   ', 'PTS.': 'PTS.'})
    df_races_display = df_races_display.rename(columns=race_names_mapping)
    html_table_races = df_races_display.to_html(escape=False, index=False)
    st.markdown(
        f'<div class="table-container" style="max-width: 100% !important;"> <div class="races-container" style="overflow-x: auto; width: 100%;"> {html_table_races} </div> </div>',
        unsafe_allow_html=True
    )

# ВКЛАДКА 3: TEAMS ______________________________________________________________________________________________________________
with tab3:
    st.header("*Teams' Standings*")
    st.html(
        """
        <style>
        /* Суворе керування шириною стовпців */
        .teams-table th:nth-child(1), .teams-table td:nth-child(1) { width: 15% !important; } /* POS. */
        .teams-table th:nth-child(2), .teams-table td:nth-child(2) { width: 46% !important; text-align: left !important; padding-left: 10px !important; } /* TEAM */
        .teams-table th:nth-child(3), .teams-table td:nth-child(3) { width: 18% !important; } /* LOGO */
        .teams-table th:nth-child(4), .teams-table td:nth-child(4) { width: 21% !important; } /* POINTS */
        </style>
        <div style="height: 2px; width: 90%; margin: 10px auto 10px auto; background: linear-gradient(to right, transparent, #FF4B4B, transparent);"></div>
        """
    )
    team_names_mapping = {
        "amr" : "Aston Martin F1 Team",
        "alfa" : "Alfa Romeo F1 Team",
        "at" : "Scuderia AlphaTauri",
        "alpine" : "Alpine F1 Team",
        "fer" : "Scuderia Ferrari",
        "haas" : "Haas F1 Team",
        "mcl" : "McLaren F1 Team",
        "mer" : "Mercedes-AMG Petronas F1 Team",
        "rbr" : "Red Bull Racing",
        "williams" : "Williams Racing"
    }
    # 1. Створюємо список стовпців, які треба додати (PTS. + всі місця від P1 до P20)
    aggregation_columns = ['PTS.'] + [f'P{i}' for i in range(1, 21)]
    
    # 2. Групуємо дані: додаємо очки та кількість фінішів на кожній позиції для обох пілотів команди
    df_teams_calculated = df_sorted_results.groupby('TEAM', as_index=False)[aggregation_columns].sum()
    
    # 3. Складне сортування FIA (тай-брейк): спочатку за PTS., якщо рівно — за P1, якщо рівно — за P2 і так далі
    df_teams_calculated = df_teams_calculated.sort_values(by=aggregation_columns, ascending=False).reset_index(drop=True)
    
    # 4. Вставляємо правильну нову позицію команди (POS.) після сортування за правилами FIA
    df_teams_calculated.insert(0, 'POS.', range(1, len(df_teams_calculated) + 1))
    
    # 5. Генеруємо логотип та робимо назву команди красивою
    df_teams_calculated['LOGO'] = df_teams_calculated['TEAM'].apply(format_team_logo, width=45, height=30)
    df_teams_calculated['TEAM'] = df_teams_calculated['TEAM'].replace(team_names_mapping)
    
    
    # 6. Залишаємо для користувача лише потрібні видимі стовпці (приховуючи технічні P1-P20)
    df_teams_visible = df_teams_calculated[['POS.', 'TEAM', 'LOGO', 'PTS.']]
    
    # Перейменовуємо стовпець LOGO в порожній заголовок ' ', як у тебе в дизайні
    df_teams_visible = df_teams_visible.rename(columns={'LOGO': ' '})
    
    html_table_teams = df_teams_visible.to_html(escape=False, index=False)
    st.markdown(f'<div class="table-container teams-table">{html_table_teams}</div>', unsafe_allow_html=True)
