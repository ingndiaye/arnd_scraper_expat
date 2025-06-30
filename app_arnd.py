
import pandas as pd 
from selenium import webdriver 
from selenium.webdriver.common.by import By 
import matplotlib.pyplot as plt 
import numpy as np
import streamlit as st
import streamlit.components.v1 as components 
from selenium.common.exceptions import WebDriverException
import undetected_chromedriver as uc

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# options = webdriver.ChromeOptions() 
# définir l'option d'utiliser chrome en mode headless ( utiliser afin de lancer le script en background)
# options.add_argument("--headless=new")  
try: 
    driver = uc.Chrome(options=options)
    driver_in = uc.Chrome(options=options) 
except WebDriverException as e:
    st.error("Impossible de démarrer le navigateur Chrome. Cette fonctionnalité ne fonctionne peut-être pas sur Streamlit Cloud.")
    st.stop()

st.markdown("""<style>body {background-color: #0f926d;} .stApp { background-color: #0f926d; } </style>""", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center; color: white';>🕷️ SCRAPING SUR EXPAT-DAKAR AVEC SELENIUM ET WEB-SCRAPER 🕷️</h5>", unsafe_allow_html=True) 

st.markdown(""" <style>
            .main {
                max-width: 95%;
                padding-left: 3rem;
                padding-right: 3rem;
            }
        </style>""", unsafe_allow_html=True)

st.markdown(""" <style> section[data-testid="stSidebar"] {background-color: #b2f7e9; }  
                 .sidebar-caption { position: relative; top: 200px;  font-size: 18px; text-align: center; color: #666; } 
                </style> """, unsafe_allow_html=True)

st.sidebar.markdown( """ <div style='text-align: center; bottom: 30px;font-weight: bold; font-size: 20px;'>  <b> ☰  Menu</b>  </div> """, unsafe_allow_html=True)
 
choix = st.sidebar.selectbox('Choisir une action', ['Tableau de bord','Scraper Congelo-frigo','Scraper Climatiseurs','Scraper Cuisinières', 'Scraper Machine à laver','Télécharger les données existantes', 'Formulaire évalution'])
nbre_pages = st.sidebar.selectbox('Nombre de pages', list([int(nbr) for nbr in np.arange(1, 350)]))

st.sidebar.markdown("""
<div class="sidebar-caption">
    <b><u>EXAMEN DATA COLLECTION</u></b> <br/>ABDOURAHMANE NDIAYE <br/> 📧 : ingndiaye@gmail.com
</div>
""", unsafe_allow_html=True) 

     
def charger_dataframe(dataframe,nom_fichier, titre_bt, id_bt, key_bt_dwn,type_screping) :
    st.markdown(""" <style> div.stButton {text-align:center; } </style>""", unsafe_allow_html=True)

    if st.button(titre_bt,id_bt): 

        st.write('Données "'+titre_bt+'" Scrapées avec '+type_screping)
        st.dataframe(dataframe)
        st.write('Dimension des donnée: ' + str(dataframe.shape[0]) + ' ligne et ' + str(dataframe.shape[1]) + ' colonnes.')

        st.download_button(
            label='Télécharger les données',
            data=dataframe.to_csv().encode('utf-8'),
            file_name=nom_fichier+'.csv',
            mime='text/csv',
            key = key_bt_dwn)
        
# machines-a-laver cuisinieres-fours climatisation refrigerateurs-congelateurs
#Scraper les congelo et frigo
def scraper_donnees_expat(nbrepage,produits):
    print(nbrepage)
    data = [] 
    for p in range(1,nbrepage+1):
        # obtenir l'url
        url = f'https://www.expat-dakar.com/{produits}?page={p}'   
        driver.get(url)
        # récupérer les containers 
        containers = driver.find_elements(By.CSS_SELECTOR, "[class = 'listing-card listing-card--tab listing-card--has-contact listing-card--has-content']")
        
        # Scraper les données sur une page 
        for container in containers :    
            try:
                #url de l'annonce
                url_in = container.find_element(By.TAG_NAME, 'a').get_attribute('href')
                
                driver_in.get(url_in)
                #Détail ou titre
                detail = driver_in.find_element(By.CLASS_NAME, "listing-item__header").text
                #print(detail)
                
                #Prix  
                prix = driver_in.find_element(By.CLASS_NAME, "listing-item__price").text.split('F')[0]  
                prix = prix.replace('\u202f', '')
                prix_fcfa = float(prix) 
                #print(prix_fcfa)
                
                #Adresse
                adresseL = driver_in.find_element(By.CLASS_NAME, "listing-item__address-location").text # Zone
                adresseR = driver_in.find_element(By.CLASS_NAME, "listing-item__address-region").text # Region
                adresse= adresseL+", "+adresseR 
                #print(adresse) 
        
                # Etat 
                etat = driver_in.find_element(By.CLASS_NAME, "listing-item__properties__description").text
        
                #ur de l'image 
                img_url = driver_in.find_element(By.CSS_SELECTOR, ".gallery__image__inner img").get_attribute("src")
    
                dic = {
                    'detail':detail,
                    'prix_fcfa':prix_fcfa,
                    'adresse':adresse,
                    'etat':etat,
                    'img_url':img_url
                }
                data.append(dic) 
                
            except : 
                pass   
    DF=pd.DataFrame(data)  
    driver_in.delete_all_cookies()   
    return DF 
 
def nettoyer_prix(prix_txt):
    if isinstance(prix_txt, str):
        prix_txt = prix_txt.replace('F', '').replace('Cfa', '').replace('?', '')
        prix_txt = prix_txt.replace(' ', '').replace(' ', '').replace(' ', '')
        try:
            return float(prix_txt)
        except ValueError:
            return np.nan
    return np.nan

if  choix == 'Tableau de bord':
    dtfrm_congel = pd.read_csv('donnees/congelateurs.csv', encoding='ISO-8859-1', sep=';')
    dtfrm_clim = pd.read_csv('donnees/climatisations.csv', encoding='ISO-8859-1', sep=';' )
    dtfrm_cuis = pd.read_csv('donnees/cuisinieres-fours.csv', encoding='ISO-8859-1', sep=';')
    dtfrm_malv = pd.read_csv('donnees/machines-a-laver.csv', encoding='ISO-8859-1', sep=';') 

    col_congel, col_clim= st.columns(2)

    with col_congel:        
        etat_cong_counts = dtfrm_congel['etat'].value_counts()
        plot1= plt.figure(figsize=(12,7))  
        plt.bar(etat_cong_counts.index, etat_cong_counts.values, color='red') 
        plt.title('Nombre de congélateurs-frigo par état',fontsize=18)
        plt.xlabel('Etat',fontsize=18)
        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)
        st.pyplot(plot1)

    with col_clim:
        etat_clim_counts = dtfrm_clim['etat'].value_counts()
        
        dtfrm_clim['prix_nettoye'] = dtfrm_clim['prix'].apply(nettoyer_prix)        
        prix_moyen_par_etat = dtfrm_clim.groupby('etat')['prix_nettoye'].mean() 
        plot2 = plt.figure(figsize=(12,7)) 
        explode = [0.05] * len(etat_clim_counts) 
        plt.plot(prix_moyen_par_etat.index, prix_moyen_par_etat.values, marker='o', linestyle='-', color='blue' )
        #plt.(etat_clim_counts.values, labels=etat_clim_counts.index, autopct='%1.1f%%',startangle=180, explode=explode) 
        plt.title('Prix moyen par état - Climatiseurs',fontsize=18)
        plt.xlabel('Etat',fontsize=18)
        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)
        st.pyplot(plot2)
        
    
    col3, col4= st.columns(2)

    with col3:
        dtfrm_cuis['prix_nettoye'] = dtfrm_cuis['prix'].apply(nettoyer_prix)
        # Calcul du prix moyen par état
        prix_moyen_par_etat = dtfrm_cuis.groupby('etat')['prix_nettoye'].mean() 
        plot3= plt.figure(figsize=(11,7))
        plt.bar(prix_moyen_par_etat.index, prix_moyen_par_etat.values, color='skyblue')
        #sns.lineplot(data=df1, x="annee", y="prix", hue="etat")
        plt.title('Prix moyen par état - Cuisinieres et Fours',fontsize=18)
        plt.xlabel('Etat',fontsize=18)
        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)
        st.pyplot(plot3)

    with col4:
        dtfrm_malv['prix_nettoye'] = dtfrm_malv['prix'].apply(nettoyer_prix)
        prix_moyen_par_etat_mlv = dtfrm_malv.groupby('etat')['prix_nettoye'].mean()#.sort_values(ascending=False)
        plot4 = plt.figure(figsize=(11,7)) 
        plt.bar(prix_moyen_par_etat_mlv.index, prix_moyen_par_etat_mlv.values, color='green')
        plt.title('Prix moyen par état - Machines à laver',fontsize=18)
        plt.xlabel('Etat',fontsize=18)
        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)
        st.pyplot(plot4)
elif choix=='Scraper Congelo-frigo': 
    dtfrm = scraper_donnees_expat(nbre_pages,'refrigerateurs-congelateurs') 
    charger_dataframe(dtfrm,'Congelo-frgo', 'Congélateurs et Réfrigérateurs', '1', '11','SELENIUM')

elif choix=='Scraper Climatiseurs': 
    dtfrm = scraper_donnees_expat(nbre_pages,'climatisation') 
    charger_dataframe(dtfrm, 'Climatiseurs','Climatiseurs', '2', '12','SELENIUM')   
elif choix=='Scraper Cuisinières': 
    dtfrm = scraper_donnees_expat(nbre_pages,'cuisinieres-fours') 
    charger_dataframe(dtfrm, 'Cuisinieres_fours', 'Cuisinières et Fours', '3', '13','SELENIUM')    

elif choix=='Scraper Machine à laver': 
    dtfrm = scraper_donnees_expat(nbre_pages,'machines-a-laver') 
    charger_dataframe(dtfrm,'machines_a_laver', 'Machine à laver', '4', '14','SELENIUM')

elif choix == 'Télécharger les données existantes': 
    dtfrm_congel = pd.read_csv('donnees/congelateurs.csv', encoding='ISO-8859-1', sep=';')
    dtfrm_clim = pd.read_csv('donnees/climatisations.csv', encoding='ISO-8859-1', sep=';' )
    dtfrm_cuis = pd.read_csv('donnees/cuisinieres-fours.csv', encoding='ISO-8859-1', sep=';')
    dtfrm_malv = pd.read_csv('donnees/machines-a-laver.csv', encoding='ISO-8859-1', sep=';') 


    charger_dataframe(dtfrm_clim, 'Climatiseurs','Climatiseurs', '6', '16','Web-Scraper')
    charger_dataframe(dtfrm_malv,'machines_a_laver', 'Machine à laver', '8', '18','Web-Scraper')
    charger_dataframe(dtfrm_cuis, 'Cuisinieres_fours', 'Cuisinières et Fours', '7', '17','Web-Scraper')   
    charger_dataframe(dtfrm_congel,'Congelo-frgo', 'Congélateurs et Réfrigérateurs', '5', '15','Web-Scraper')



else :
    components.html("""<iframe src="https://ee.kobotoolbox.org/single/70d6ca332ba1f4bef90ecd2d461db7a6" width="700" height="1000"</iframe>""",height=1100,width=800)
