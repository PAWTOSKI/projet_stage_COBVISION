#!/usr/bin/env python
# coding: utf-8

# In[60]:


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

print("importation ok")


# In[ ]:





# In[61]:


#définition de l'objet connecteur

def connector_mysql( paquets,identifiant,mot_passe, nom_serveur,nom_BD):
    connector='%s://%s:%s@%s/%s' %(paquets, identifiant, mot_passe, nom_serveur, nom_BD)
    engine=create_engine(connector)
    return engine 

connector=connector_mysql('mysql+pymysql', 'root', 'root', 'localhost', 'essai_cobtest_2' )
print( 'definition objet connector ok')


# In[ ]:





# In[77]:


app = dash.Dash(__name__, external_stylesheets = [dbc.themes.UNITED])


# In[64]:


#instanciation de la barre de navigation

nav= Navbar()


# In[65]:


#instanciation de la barre de recherche

search=html.Div([
                html.I('veuillez sélectionner la personne recherchée'),
                dcc.Input(id='input-firstname',
                          type="text",
                          value='initial_value',
                          persistence=True
                         ),
                dcc.Input(id='input-lastname',
                          type="text",
                          value='initial_value',
                          persistence=True
                         ),
                html.Button(id='submit-button', 
                                    type='submit', 
                                    children='Submit')
                ])


# In[66]:


# instanciation de la sortie

output=html.Div(id='output',children=[]
                
               )


# In[ ]:





# In[67]:


# instanciation du layer

def App():
    layout=html.Div([nav,
                    search,
                    output
                   ])
    return layout
app.layout = App()
print('layout done...')


# In[68]:


#définition de la fonction de mise en table des données pertinents relatives au sujet.

def table_(submit_button,firstname, lastname):
    statement='SELECT p.patient_key, sc.created_by, sc.center_key, '
    statement+= 'sc.date_created, sc.version, sc.test ,sc.score , sc.comment '
    statement+= 'from patients_actifs as p '
    statement+= 'INNER JOIN scores_actifs as sc ON sc.patient_key=p.patient_key '
    statement+= f'WHERE p.patient_key=(select p2.patient_key from patients as p2 '
    statement+= f'where p2.lastname like "{firstname}" AND p2.firstname like "{lastname}") '
    statement+= 'ORDER BY date_created DESC;'
    data_=pd.read_sql(statement,con=connector)
    
    table_=dash_table.DataTable(
                         id='view_table',
                         columns=[{'name':column, 'id':column} for column in data_.columns ],
                         data=data_.to_dict('records')
                            )
    return table_


# In[2]:





# In[ ]:





# In[ ]:





# In[ ]:




