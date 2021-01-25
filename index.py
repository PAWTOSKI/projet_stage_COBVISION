#!/usr/bin/env python
# coding: utf-8

# In[2]:


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
from collections import deque
from dashboard_view import App_view, table1_ , table2_
from dashboard_monitoring import App_monitoring, connector_mysql, graph1, graph2_A, graph2_B, graph3, graph4, log_e, log_t, log_proc
from navbar import Navbar
import time
from datetime import datetime
from flask import request

print('importation done ...')


# In[3]:


#définition de l'objet connecteur
connector=connector_mysql('mysql+pymysql', 'root', 'root', 'localhost', 'essai_cobtest_2' )
print( 'definition objet connector ok')


# In[4]:


#importation des mots de passe et des utilisateurs
# enregistrés depuis la base de données

statement="SELECT us.name, us.pass FROM essai_cobtest_2.users as us"

list_password=pd.read_sql(statement, connector)
list_password=[[i,j] for i,j in zip(list_password['name'], list_password['pass']) ]
print('password imported')


# In[5]:


#instanciation de l'application

app= dash.Dash(__name__, 
               external_stylesheets=[dbc.themes.UNITED] )
auth=dash_auth.BasicAuth(app, list_password)
print('authenfication succed')


# In[6]:


#cette instruction permet de configurer les callbacks de notre application
#n'étant pas inclus dans le layer de la page d'accueil
app.config.suppress_callback_exceptions = True


# In[7]:


#instanciation de la barre de menu
app.layout = html.Div([
                        dcc.Location(id = 'url', refresh = False),
                        html.Div(id = 'page-content')
                        ])


# In[8]:


# création d'un espace renvoyant la page voulue

@app.callback(Output('page-content', 'children'),
            [Input('url', 'pathname')])

def display_page(pathname):
    print('layer initated....')
    
    if pathname == '/dashboard_view.py' : 
        print('layer done')
        return App_view()
    
    if pathname=='/dashboard_monitoring.py' :
        print('layer done')
        return App_monitoring()
    
    else:
        return homepage()       
    


# In[9]:


print('containers intiated...')
liste_colonnes=('Com_delete','Com_update','Com_select','Com_insert', 'Com_revoke' ,'Com_call_procedure'
,'Com_truncate', 'Com_alter_user', 'Com_alter_table' , 'Binlog_cache_disk_use','Queries', 'Slow_queries', 'Binlog_cache_use', 'Binlog_stmt_cache_use'
,'Binlog_stmt_cache_disk_use', 'Handler_commit', 'Handler_delete', 'Handler_discover', 'Handler_external_lock'
,'Handler_mrr_init', 'Handler_prepare', 'Handler_read_first', 'Handler_read_key', 'Handler_read_last','Handler_read_next'
,'Handler_read_prev', 'Handler_read_rnd', 'Handler_read_rnd_next', 'Handler_rollback', 'Handler_savepoint', 'Handler_savepoint_rollback'
,'Handler_update', 'Handler_write', 'Innodb_buffer_pool_bytes_data', 'Innodb_buffer_pool_pages_free','Innodb_buffer_pool_pages_total'
,'Threads_connected', 'Threads_running', 'Connections', 'Connection_errors_internal', 'Bytes_received', 'Bytes_sent', 'Aborted_connects', 
                    'Innodb_buffer_pool_reads', 'Innodb_buffer_pool_read_requests')

X=deque(maxlen=30)
Y=deque(maxlen=30)
print('containers made...')


# In[ ]:





# In[10]:


# exécution du tableau de bord de surveillance

#vérification des droits d'accès de l'utilisateur

if App_monitoring() :
        print('dashboard monitiring initiated...')
    
        @app.callback(dash.dependencies.Output('graph1', 'figure'),
              dash.dependencies.Output('graph_2A', 'figure'),
              dash.dependencies.Output('graph_2B', 'figure'),
              dash.dependencies.Output('graph3', 'figure'),
              dash.dependencies.Output('graph4', 'figure'),
              dash.dependencies.Output('output5', 'children'),
              dash.dependencies.Output('output6', 'children'),
              dash.dependencies.Output('output7', 'children'),
              
              
              [
              dash.dependencies.Input('update_graph1','n_intervals'),
              dash.dependencies.Input('update_graph2A','n_intervals'),
              dash.dependencies.Input('update_graph2B','n_intervals'),
              dash.dependencies.Input('update_graph3','n_intervals'),
              dash.dependencies.Input('update_graph4','n_intervals'),
              dash.dependencies.Input('update_graph5','n_intervals'),
              dash.dependencies.Input('input_rows', 'value'),
              dash.dependencies.Input('choice_tables', 'value'),
              dash.dependencies.Input('choice_procedures', 'value'),
              dash.dependencies.Input('update_graph7','n_intervals'),
                  
              ]
              
              )
              
        

        def update_table_(update_graph1, update_graph2A, update_graph2B, update_graph3, update_graph4, update_graph5, input_rows, choice_tables, choice_procedures, update_graph7 ):
#, update_graph2A, update_graph2B, update_graph3, update_graph4, update_graph5, input_rows,choice_tables, choice_procedures ,update_graph7 ):   
    
    
    
            Y.append( pd.read_sql(f'SHOW GLOBAL STATUS WHERE VARIABLE_NAME in {liste_colonnes} or VARIABLE_NAME LIKE "%%HANDLER%%" ',con=connector )['Value'].astype(int).values )
            if len(Y)>1:
                Y[-2]=Y[-1]-Y[-2]
        
            X.append( datetime.now() )
    
    
# création du dataframe dynamique :

    
            labels= pd.read_sql(f'SHOW GLOBAL STATUS WHERE VARIABLE_NAME in {liste_colonnes} or VARIABLE_NAME LIKE "%%HANDLER%%" ',con=connector )['Variable_name'].values
            dataSQL=pd.DataFrame(data=[i for i in Y], columns=labels,  index=X)
    
    
        
# conversion des données en format 'INT' pour toutes les colonnes à l'exception d'index,
# pour les rendre exploitables par la méthode 'mean'
    
    
            dataSQL=dataSQL.astype(int)

        #Calcul de la moyenne des performances, par tranche de 30 secondes
            dataSQL=dataSQL.resample('30S').mean()  
                               
    # nettoyage des données nulles par leur remplacement avec la moyenne
            for colonne in dataSQL.columns:
                dataSQL[colonne]=dataSQL[colonne].fillna(dataSQL[colonne].mean() )


            return graph1(update_graph1, dataSQL) , graph2_A(update_graph2A, dataSQL), graph2_B(update_graph2B, dataSQL), graph3(update_graph3, dataSQL), graph4(update_graph4, dataSQL), log_e(update_graph5, input_rows), log_t(choice_tables), log_proc(update_graph7, choice_procedures)
#, graph2_B(update_graph2B, dataSQL), graph4(update_graph4, dataSQL), log_e(update_graph5, input_rows), log_t(choice_tables), log_proc(update_graph7, choice_procedures)
 
 
 


# In[11]:


# instanciation du tableau de bord de visualisation des scores
if App_view():
    print('dashboard viewing initiated...')
    
# "callback" effectuées sur les composants "button-submit" et "output", à partir des entrées de nom et prénom
#,ce pour le fichier "dashboard_view"

    @app.callback(dash.dependencies.Output('output_1', 'children'),
                  dash.dependencies.Output('output_2', 'children'),

              
                 [dash.dependencies.Input('submit-button', 'n_clicks'),
              
                 ],
              
                 [dash.dependencies.State('input-firstname', 'value'),
                  dash.dependencies.State('input-lastname', 'value')
                 ])

    def update_table_(submit_button, firstname, lastname):
    
        return table1_(submit_button,firstname, lastname), table2_(submit_button,firstname, lastname)


# In[ ]:


if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1', port='37709')


# In[ ]:





# In[ ]:




