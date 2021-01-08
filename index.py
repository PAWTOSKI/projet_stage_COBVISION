#!/usr/bin/env python
# coding: utf-8

# In[31]:


#importation des paquets nécessaires

import dash
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from home_page import homepage
from sqlalchemy import create_engine
import dash_bootstrap_components as dbc
import dash_auth
from dashboard_view import App, table_
from navbar import Navbar
print('importation done ...')


# In[32]:


#définition de l'objet connecteur

def connector_mysql( paquets,identifiant,mot_passe, nom_serveur,nom_BD):
    connector='%s://%s:%s@%s/%s' %(paquets, identifiant, mot_passe, nom_serveur, nom_BD)
    engine=create_engine(connector)
    return engine 

connector=connector_mysql('mysql+pymysql', 'root', 'root', 'localhost', 'essai_cobtest_2' )
print( 'definition objet connector ok')


# In[33]:


#importation des mots de passe et des utilisateurs
# enregistrés depuis la base de données

statement="SELECT us.name, us.pass FROM essai_cobtest_2.users as us"

list_password=pd.read_sql(statement, connector)
list_password=[[i,j] for i,j in zip(list_password['name'], list_password['pass']) ]
print('password imported')


# In[34]:


#instanciation de l'application

app= dash.Dash(__name__, 
               external_stylesheets=[dbc.themes.UNITED] )
auth=dash_auth.BasicAuth(app, list_password)


# In[35]:


#cette instruction permet de configurer les callbacks de notre application
#n'étant pas inclus dans le layer de la page d'accueil
app.config.suppress_callback_exceptions = True


# In[36]:


#instanciation de la barre de menu
app.layout = html.Div([
                        dcc.Location(id = 'url', refresh = False),
                        html.Div(id = 'page-content')
                        ])


# In[37]:


# création d'un espace renvoyant la page voulue

@app.callback(Output('page-content', 'children'),
            [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/dashboard_view.py':
        
        return App()
    else:
        return homepage()       
    


# In[38]:


# "callback" effectuées sur les composants "button-submit" et "output", à partir des entrées de nom et prénom
#,ce pour le fichier "dashboard_view"

@app.callback(dash.dependencies.Output('output', 'children'),
             [dash.dependencies.Input('submit-button', 'n_clicks')
             ],
             [dash.dependencies.State('input-firstname', 'value'),
              dash.dependencies.State('input-lastname', 'value')
             ])

def update_table_(submit_button,firstname, lastname):
    table1= table_(submit_button,firstname, lastname)
    return table1


# In[39]:


if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1', port='37709')


# In[40]:





# In[ ]:





# In[ ]:




