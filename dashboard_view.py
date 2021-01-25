#!/usr/bin/env python
# coding: utf-8

# In[1]:


#importation des paquets nécessaires

import dash
import dash.dependencies
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
from sqlalchemy import create_engine
import dash_bootstrap_components as dbc
import dash_auth
from navbar import Navbar
from flask import request


# In[ ]:





# In[8]:


#définition de l'objet connecteur

def connector_mysql( paquets,identifiant,mot_passe, nom_serveur,nom_BD):
    connector='%s://%s:%s@%s/%s' %(paquets, identifiant, mot_passe, nom_serveur, nom_BD)
    engine=create_engine(connector)
    return engine 

connector=connector_mysql('mysql+pymysql', 'root', 'root', 'localhost', 'essai_cobtest_2' )


# In[ ]:





# In[9]:


app = dash.Dash(__name__, external_stylesheets = [dbc.themes.UNITED])


# In[10]:


#instanciation de la barre de navigation

nav= Navbar()


# In[11]:


#instanciation de la barre de recherche

search=html.Div([
                html.I('veuillez sélectionner la personne recherchée'),
                dcc.Input(id='input-firstname',
                          type="text",
                          value='initial_value',
                          persistence=True,
                          placeholder="firstname"
                         ),
                dcc.Input(id='input-lastname',
                          type="text",
                          value='initial_value',
                          persistence=True,
                          placeholder="lastname"
                         ),
                html.Button(id='submit-button', 
                                    type='submit', 
                                    children='Submit')
                ])


# In[12]:


# instanciation des sorties sortie

output_1=html.Div(id='output_1',
                 children=[]
               )
output_2=html.Div(id='output_2',
                 children=[]
                )


# In[ ]:


# instanciation du titre

title=html.H1("Soignant/ utilisateur basique: outil de visualisation ")


# In[13]:


# instanciation du layer

def App_view():
    layout=html.Div([title,
                    nav,
                    search,
                    output_1,
                    output_2
                    ])
        
    return layout
app.layout = App_view()


# In[ ]:


#définition de la fonction de mise en table des données personnelles du sujet

def table1_(submit_button,firstname, lastname):
    username=request.authorization['username']
    statement=f"SELECT isadmin, isglobal FROM essai_cobtest_2.users as us WHERE us.name='{username}' ; "
    data_=pd.read_sql(statement, con=connector)
    
    # première colonne: isadmin, deuxième colonne: isglobal
    if data_.iloc[0,0]==1 and data_.iloc[0,1]==1:
        statement=f'SELECT * FROM essai_cobtest_2.patients as p WHERE p.firstname like "{firstname}" AND p.lastname like "{lastname}"  ;'
        data_=pd.read_sql(statement, con=connector)
    
       
    elif data_.iloc[0,0]==0 and data_.iloc[0,1]==1 :
        statement=f'SELECT * FROM essai_cobtest_2.patients_actifs as p WHERE p.firstname like "{firstname}" AND p.lastname like "{lastname}"  ;'
        data_=pd.read_sql(statement, con=connector)
        
    else:
        return 0
    
    table1_=dash_table.DataTable(id='view_table',
                               columns=[{'name':column, 'id':column} for column in data_.columns],
                                data=data_.to_dict('records'),
                                style_table={'margin-left': '3vw', 'margin-top': '3vw'}
                               )
    
        
    
    return table1_


# In[6]:


#définition de la fonction de mise en table des données pertinents relatives au sujet.

def table2_(submit_button,firstname, lastname):
    username=request.authorization['username']
    statement=f"SELECT isadmin, isglobal FROM essai_cobtest_2.users as us WHERE us.name='{username}' ; "
    data_=pd.read_sql(statement, con=connector)
    if data_.iloc[0,0]==0 and data_.iloc[0,1]==1:
        statement='SELECT p.patient_key, sc.created_by, p.center_key, '
        statement+= 'sc.date_created, sc.version, sc.test ,sc.score , sc.comment '
        statement+= 'from patients_actifs as p '
        statement+= 'INNER JOIN scores_actifs as sc ON sc.patient_key=p.patient_key '
        statement+= f'WHERE p.patient_key=(select p2.patient_key from patients_actifs as p2 '
        statement+= f'where p2.lastname like "{lastname}" AND p2.firstname like "{firstname}") '
        statement+= 'ORDER BY version DESC;'
        data_=pd.read_sql(statement,con=connector)
        
    
        
        
    elif data_.iloc[0,0]==1 and data_.iloc[0,1]==1: 
        statement='SELECT p.patient_key, sc.created_by, p.center_key, '
        statement+= 'sc.date_created, sc.version, sc.test ,sc.score , sc.comment, sc.last '
        statement+= 'FROM patients AS p '
        statement+= 'INNER JOIN scores as sc ON sc.patient_key=p.patient_key '
        statement+= f'WHERE p.last="True" AND p.patient_key=(select p2.patient_key from patients_actifs as p2 '
        statement+= f'where p2.lastname like "{lastname}" AND p2.firstname like "{firstname}") '
        statement+= 'ORDER BY version DESC;'
        data_=pd.read_sql(statement,con=connector)
        
    else:
        return 0
    
    table2_=dash_table.DataTable(
                                id='view_table',
                                columns=[{'name':column, 'id':column} for column in data_.columns ],
                                data=data_.to_dict('records'),   
                                style_table={'margin-left': '3vw', 'margin-top': '3vw'}
                                )
    
    return table2_


# In[17]:





# In[ ]:





# In[ ]:




