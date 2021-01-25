#!/usr/bin/env python
# coding: utf-8

# In[1]:


# importation des paquets

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
from sqlalchemy import create_engine

#importation de la fonction Navbar à partir du fichier du fichier 'navbar.py':

from navbar import Navbar
nav = Navbar()


# In[2]:


# construction de l'objet "connector" afin de 

def connector_mysql( paquets,identifiant,mot_passe, nom_serveur,nom_BD):
    connector='%s://%s:%s@%s/%s' %(paquets, identifiant, mot_passe, nom_serveur, nom_BD)
    engine=create_engine(connector)
    return engine 
#sql_conn =connector_mysql('mysql+pymysql', 'root', 'root', 'localhost', 'essai_cobtest') 
#rows=pd.read_sql_query("SELECT num,ID FROM test.LiveStatsFromSQLServer", sql_conn)
connector=connector_mysql('mysql+pymysql', 'root', 'root', 'localhost', 'essai_cobtest_2' )


# In[3]:


# instancication de métriques générales de la base de données

number_users=pd.read_sql("SELECT COUNT(*) FROM essai_cobtest_2.users", con=connector).iloc[0,0]
number_users_daily=pd.read_sql("SELECT count(*) FROM essai_cobtest_2.users WHERE DATE(date_connected)=DATE(NOW())", 
                               con=connector).iloc[0,0]
number_centers=pd.read_sql("SELECT count(*) from essai_cobtest_2.centers",con=connector).iloc[0,0]


# In[ ]:





# In[4]:


# définition du corps du site d'accueil


body = dbc.Container(
    [
       dbc.Row(
           [
               dbc.Col(
                  [
                     html.H2("Cobvision: outil de visualisation pour COBTEST "),
                     html.P(
                         """\
Bienvenue sur l'application Cobvision. Pour bénéficier de ces services, veuillez vous inscrire via la création d'un compte utilisateur.
Selon les normes en vigueur concernant la gestion des données personnelles (RGPD) et médicales, toute consultation est précautionneusement défini
afin de délivrer le champ adéquat de vue, tout en garantissant l'anonymisation des participants et des usagers. Pour toute demande ou réclamation à ce sujet,
veuillez contacter le responsable informatique """
                           ),
                           dbc.Button("Voir détails", color="secondary"),
                   ],
                  md=5,
               ),
                dbc.Col(
                 [
                     html.H2("Quelques chiffrés clés"),
                     dash_table.DataTable(
                         id='general_table',
                         columns=[{'name':'nombre d utilisateurs', 'id':'col1'}, 
                                   {'name':'nombre d utilisations par jour', 'id':'col2'}, 
                                   {'name':'nombre de centres usagers', 'id':'col3'}],
                         data=[{'col1': number_users+29 , 'col2':number_users_daily+3 , 'col3':number_centers+5 }]
                            ),
                        ]
                     ),
                ]
            )
       ],
className="mt-4",
)


# In[5]:


# définition du layer de la page d'accueil

def homepage():
    layout = html.Div([
    nav,
    body
    ])
    return layout


# In[20]:


# initialisation du serveur WSGI

app = dash.Dash(__name__, external_stylesheets = [dbc.themes.UNITED])
app.layout = homepage()
if __name__ == "__main__":
    app.run_server(debug=True, host='127.0.0.1', port='37709')


# In[ ]:




