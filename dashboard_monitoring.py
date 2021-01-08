#!/usr/bin/env python
# coding: utf-8

# In[2]:


#tutoriel utilisé: https://github.com/tomaztk/Real_Time_Visualization_with_Dash_Python_and_SQLServer/blob/master/Real_TimeStatsVisualizationWithDash.py

#problème rencontré: EVENT qui a été enlevé des dernières distributions qu paquet 'Dash'. solution: -https://community.plotly.com/t/events-equivalent-in-0-39/21664
#-https://stackoverflow.com/questions/54807868/how-to-fix-importerror-cannot-import-name-event-in-dash-from-plotly-python
#problème rencontré en cours de résolution: non actualisation du graphique en ligne

#ressources: https://plotly.com/python/time-series/

import dash
import numpy as np
import dash.dependencies
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import requests
import time

import plotly
import plotly.graph_objs as go
from collections import deque
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import time
import matplotlib.pyplot as plt
import dash_auth
from navbar import Navbar


# In[3]:


def connector_mysql( paquets,identifiant,mot_passe, nom_serveur,nom_BD):
    connector='%s://%s:%s@%s/%s' %(paquets, identifiant, mot_passe, nom_serveur, nom_BD)
    engine=create_engine(connector)
    return engine 
#sql_conn =connector_mysql('mysql+pymysql', 'root', 'root', 'localhost', 'essai_cobtest') 
#rows=pd.read_sql_query("SELECT num,ID FROM test.LiveStatsFromSQLServer", sql_conn)
connector=connector_mysql('mysql+pymysql', 'root', 'root', 'localhost', 'essai_cobtest_2' )
print( 'definition objet connector ok')

# activation de l'historique des requêtes sur MySQL

connector.execute("UPDATE performance_schema.setup_instruments SET ENABLED = 'YES', TIMED = 'YES' WHERE (NAME LIKE '%%statement/%%' OR NAME LIKE '%%stage/%%') ;")
connector.execute("UPDATE performance_schema.setup_consumers SET enabled =1; ")




print('parameters done...')


# In[4]:


#importation des mots de passe et des utilisateurs
# enregistrés depuis la base de données

statement="SELECT us.name, us.pass FROM essai_cobtest_2.users as us WHERE us.isglobal=1 and us.isadmin=1 "

list_password=pd.read_sql(statement, connector)
list_password=[[i,j] for i,j in zip(list_password['name'], list_password['pass']) ]
print('password imported')


# In[39]:


X=deque(maxlen=30)
Y=deque(maxlen=30)
print('containers made...')


# In[40]:


columns_fig5=['Thread_id', 'Event_id', 'MESSAGE_TEXT', 'RETURNED_SQLSTATE', 'time_execution']
columns_fig6=['tables', 'records', 'repetitions', 'id_repetitions', 'values_null', 'id_values_null','fk_unreferenced','id_fk_un']
labels_fig6=['users', 'scores', 'patients', 'centers']
columns_fig7=['procedure','last_start', 'last_duration','duration_mean']
labels_fig7=['delete_centers', 'delete_patients', 'delete_scores', 'delete_users', 'insert_centers', 'insert_patients', 'insert_scores', 'insert_users', 'update_scores', 'update_users', 'patients_actifs', 'scores_actifs', 'select_centers']
print('variables ok')


# In[41]:


name_title = 'Stats from SQL Server'
app = dash.Dash(__name__ )

# mise en place de la fenêtre d'authenfication
print('start of athentification...') 
auth=dash_auth.BasicAuth(app, list_password)
print('authentification done')


# In[42]:


#instanciation du layer , avec configuration de l'actualisation de celui sur des périodes de 60 secondes

print('start layer...')
app.layout = html.Div([ 
            
                #titre du menu
                html.Div([
                    html.H1(children='Cobtest: Tableau de bord de l"activité de la base de données'
                           )]), 
    
                #graphique 1
                html.Div([
                    
                    dcc.Graph( id='graph1',
                                animate=False
                                 ), 
                    dcc.Interval(id='graph_update1',
                                interval=30*1000            # unité de temps: ms                            
                                    )
                        
                        ]),
    
                #graphiques 2_A  et 2_B
    
    
             html.Div([  
                    html.Div([
                        dcc.Graph( id='graph2_A',
                                    animate=False
                                  ), 
                        dcc.Interval( id='graph_update2_A',
                                        interval=30*1000,   # unité de temps: ms    
                                    )
                            ],
                        style={'width': '39%', 'display': 'inline-block'}
                            ),
                    
                    html.Div([
                        html.P("""\n 
                        Le diagramme de gauche se sert d'une unité de mesure propre à Mysql afin de quantifier la 
                               mémoire octroyé à Mysql : pages. Une page est paramétré par une portion de RAM prédéfini et alloué pour toute opération
                               \n
                               
                               le diagramme de droite représente quant à lui l'efficacité des lectures logiques via la mémoire vive , ce selon les ressources allouées. 
                               si la fréquece de l'écriture sur disque est supérieurà 5%,il est conseillé d'augmenter les ressources allouées en matière de RAM au moteur logique  """)
                            ],
                        style={'width': '17%',
                               'display': 'inline-block'
                              }
                            ),
                   
    
   
                    html.Div([
                        dcc.Graph( id='graph2_B',
                                   animate=False
                                 ), 
                        dcc.Interval( id='graph_update2_B',
                                        interval=30*1000,   # unité de temps: ms    
                                    )
                            ],
                        style={'width': '39%', 'display': 'inline-block'}
                            )
                    
                        ]),
                
                
                #graphiques 3  
               
                html.Div([
                    dcc.Graph( id='graph3',
                                animate=False
                                ), 
                     dcc.Interval(id='graph_update3',
                                    interval=30*1000   # unité de temps: ms   
                                  ) 
                        ],
                     style={'margin':'20px'}
                        ), 
                        
                    
                         
                    
                
                #graphique 4
                html.Div([
                    dcc.Graph(id='graph4',
                            animate=False
                             ),
                    
                    dcc.Interval(id='graph_update4',
                                interval=30*1000 ) 
                        ],
                        style={'margin':'20px'}
                        ),
    
    
                #figure 5
                html.Div([
                    html.Label("log events erros"
                              ),
                    dash_table.DataTable(id='log_events_errors',
                                        columns=[{'id':c, 'name':c } for c in columns_fig5 ],      
                                        data=[{'Thread_id':0,'Event_id': 0, 'MESSAGE_TEXT':0, 'RETURNED_SQLSTATE':0, 'time_execution':0 }]
                                        ),
                    dcc.Interval(id='graph_update5',
                                    interval=30*1000 ),
                    
                    html.Div([
                        html.Div(dcc.Input( id='input_rows', type='number', persistence=True)),
                        html.Button(children='number_rows',id='N_rows'),
                        html.Div(id='container-number-rows', children='entrer le nombre d enregistrements voulus'),
                            ])
                        ],
                        style={'margin':'50px'}
                        ),
    
                #figure 6
                html.Div([ 
                    html.Label("log tables metrics"
                              ),
                    dash_table.DataTable(id='log_tables_metrics',
                                                 columns=[{'id':c , 'name':c} for c in columns_fig6]
                                                ),
                    html.Div([
                            dcc.Dropdown(id='choice_tables', 
                            options=[{'label':i , 'value':i} for i in labels_fig6],
                            value=labels_fig6, multi=True
                                        )
                            ])
                        ],
                        style={'margin':'50px'}
                        ),
    
    
                #figure 7
    
                html.Div([ 
                    html.Label("log procedures common"
                              ),
                    dash_table.DataTable(id='log_procedures_common',
                                         columns=[{'id':c , 'name':c} for c in columns_fig7]
                                        
                                                ),
                    html.Div([
                            dcc.Dropdown(id='choice_procedures', 
                                        options=[{'label':i , 'value':i} for i in labels_fig7],
                                        value=labels_fig7, multi=True
                                        ),
                            dcc.Interval(id='graph_update7',
                                        interval=30*1000   # unité de temps: ms   
                                  )
                            ])
                        ],
                        style={'margin':'50px'}
                        ) 

])   
                                
print('layer done')


# In[43]:


liste_colonnes=('Com_delete','Com_update','Com_select','Com_insert', 'Com_revoke' ,'Com_call_procedure'
,'Com_truncate', 'Com_alter_user', 'Com_alter_table' , 'Binlog_cache_disk_use','Queries', 'Slow_queries', 'Binlog_cache_use', 'Binlog_stmt_cache_use'
,'Binlog_stmt_cache_disk_use', 'Handler_commit', 'Handler_delete', 'Handler_discover', 'Handler_external_lock'
,'Handler_mrr_init', 'Handler_prepare', 'Handler_read_first', 'Handler_read_key', 'Handler_read_last','Handler_read_next'
,'Handler_read_prev', 'Handler_read_rnd', 'Handler_read_rnd_next', 'Handler_rollback', 'Handler_savepoint', 'Handler_savepoint_rollback'
,'Handler_update', 'Handler_write', 'Innodb_buffer_pool_bytes_data', 'Innodb_buffer_pool_pages_free','Innodb_buffer_pool_pages_total'
,'Threads_connected', 'Threads_running', 'Connections', 'Connection_errors_internal', 'Bytes_received', 'Bytes_sent', 'Aborted_connects', 
                    'Innodb_buffer_pool_reads', 'Innodb_buffer_pool_read_requests')


# In[171]:


@app.callback(dash.dependencies.Output('graph1', 'figure'),
              dash.dependencies.Output('graph2_A', 'figure'),
              dash.dependencies.Output('graph2_B','figure'),
              dash.dependencies.Output('graph3', 'figure'),
              dash.dependencies.Output('graph4', 'figure'),
              dash.dependencies.Output('log_events_errors', 'data'),
              dash.dependencies.Output('log_tables_metrics', 'data'),
              dash.dependencies.Output('log_procedures_common', 'data'),
              
            
              
              [ 
                dash.dependencies.Input('graph_update1','n_intervals'),
                dash.dependencies.Input('graph_update2_A','n_intervals'),
                dash.dependencies.Input('graph_update2_B','n_intervals'),
                dash.dependencies.Input('graph_update3','n_intervals'),
                dash.dependencies.Input('graph_update4','n_intervals'),
                dash.dependencies.Input('graph_update5','n_intervals'),
                dash.dependencies.Input('input_rows', 'value'),
                dash.dependencies.Input('choice_tables', 'value'),
                dash.dependencies.Input('choice_procedures', 'value'),
                dash.dependencies.Input('graph_update7','n_intervals'),         
              ]
              
              
             ) # ici pour assurer le callback, l'entrée 'n_intervals' remplace la fonction Event des versions précédentes



def graph_update1 ( update1, update2_A, update2_B, update3, update4, update5 ,value, choice_tables, choice_procedures, graph_update7) :
    

# ajout dynamique des relevées de performances(Y) au moment t(X), selon une échelle de 20 valeurs maximales
    
    liste_colonnes=('Com_delete','Com_update','Com_select','Com_insert', 'Com_revoke' ,'Com_call_procedure'
,'Com_truncate', 'Com_alter_user', 'Com_alter_table' , 'Binlog_cache_disk_use','Queries', 'Slow_queries', 'Binlog_cache_use', 'Binlog_stmt_cache_use'
,'Binlog_stmt_cache_disk_use', 'Handler_commit', 'Handler_delete', 'Handler_discover', 'Handler_external_lock'
,'Handler_mrr_init', 'Handler_prepare', 'Handler_read_first', 'Handler_read_key', 'Handler_read_last','Handler_read_next'
,'Handler_read_prev', 'Handler_read_rnd', 'Handler_read_rnd_next', 'Handler_rollback', 'Handler_savepoint', 'Handler_savepoint_rollback'
,'Handler_update', 'Handler_write', 'Innodb_buffer_pool_bytes_data', 'Innodb_buffer_pool_pages_free','Innodb_buffer_pool_pages_total'
,'Threads_connected', 'Threads_running', 'Connections', 'Connection_errors_internal', 'Bytes_received', 'Bytes_sent', 'Aborted_connects', 
                    'Innodb_buffer_pool_reads', 'Innodb_buffer_pool_read_requests')

    
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
        
        
    #graphique 1
   
    
    graph1=go.Figure(layout_title_text='Circulation des flux de données')
    axe_x=list(dataSQL[0:-1].index)
    axe_y1=list(dataSQL[0:-1]['Bytes_received'].values)
    axe_y2=list(dataSQL[0:-1]['Bytes_sent'].values)
    graph1.add_trace(go.Scatter(x=axe_x, y=axe_y1 , name='Bytes_received'  ))
    graph1.add_trace(go.Scatter(x=axe_x, y=axe_y2, name= 'Bytes_sent' ))
    
 
    


       # graphique 2_A
    graph2_A=go.Figure(layout_title_text='Etat de la mémoire allouée par le moteur Innodb')
    graph2_A.add_trace(go.Pie(labels=['nombre de pages totaux','nombre de pages libres'],
                            values=[dataSQL['Innodb_buffer_pool_pages_total'].iloc[-1], dataSQL['Innodb_buffer_pool_pages_free'].iloc[-1]]))
    
    
    # graphique 2_B 
    
    efficiency_read=dataSQL['Innodb_buffer_pool_reads'].iloc[-1]/dataSQL['Innodb_buffer_pool_read_requests'].iloc[-1]*100
    graph2_B=go.Figure(layout_title_text='Efficacité de lecture sur la Base de données')
    graph2_B.add_trace(go.Pie(labels=['fréquence de lectures logiques sur disque  ', 'proportion totale lectures logiques'],
                                values=[ efficiency_read, 100-efficiency_read   ]))
    
    
        
    # graphique 3
    axe_x=list(dataSQL[0:-1].index)
    dict_temp={'Threads_connected': 'Connexions (Threads) ouvertes' ,'Threads_running':'Connexions actives'} 
    dict_temp.update({'Connections':'Nombre d établissements de connexions', 'Aborted_connects':'tentatives de connexions échouées'})
    graph3=go.Figure(layout_title_text='Etat et concurrence des connexions au serveur MySQL')
                     
    for colonne in dict_temp:
        current_total=dataSQL[colonne].iloc[-1]
        graph3.add_trace(go.Scatter(x=axe_x, y= list(dataSQL[0:-1][colonne].values)
                                ,name=f'{dict_temp[colonne]} : {current_total}' ))
    
    
    #graphique 4
    dict_temp={'Queries':'requêtes exécutées', 'Slow_queries':'requêtes lentes', 'Com_select':'requêtes "select"'}
    dict_temp.update({'Com_update':'requêtes "update"', 'Com_insert':'requêtes type "insert"' ,'Com_delete':'requêtes "delete"' })
    dict_temp.update({ 'Com_call_procedure':'procedures appelées ',  'Com_truncate':'requêtes "Truncate"', 'Com_alter_table': 'requêtes "alter_table"' })
    graph4=go.Figure(layout_title_text='Flux des requêtes')
    for i in dict_temp:
        graph4.add_trace(go.Scatter(x=axe_x,y=list(dataSQL[0:-1][i].values) 
                                ,name=dict_temp[i]))
    
    
    #journal d'évènements
  
   
    range_=int(value)
    start_='DATE_SUB(NOW(), INTERVAL (SELECT VARIABLE_VALUE FROM performance_schema.global_status WHERE VARIABLE_NAME="UPTIME") '
    start_+='- TIMER_START*10e-13 second) AS time_execution'    
    statement=f'select Thread_id , Event_id,MESSAGE_TEXT, RETURNED_SQLSTATE, {start_} from performance_schema.events_statements_history_long '
    statement+=f"WHERE (ERRORS=1 AND SQL_TEXT NOT LIKE '%%DESCRIBE%%' AND NESTING_EVENT_LEVEL=0) ORDER BY THREAD_ID DESC, EVENT_ID DESC LIMIT {range_};"
    log_events=pd.read_sql(statement, con=connector).to_dict('records')
    
    #journal de tables
    
    log_tables=pd.DataFrame(index=columns_fig6, columns=labels_fig6)
    for i in list(choice_tables):
        count=pd.read_sql(f'select count(*) from {i}', con=connector)  # ici on extrait directement de le BD le nombre total de lignes de la table
      
     #df_rep et df_null ont été formatées en 'str',afin de procéder à l'insertion de séparateurs ','
    
        df_rep=pd.read_sql(f'call check_repetitions_{i}()', con=connector).astype('str')
        df_null=pd.read_sql(f'call check_null_{i}()', con=connector).astype('str') 
        
        
        #la procédure stockée "call chek_integrity_fk_"nom table" n'est pas implémentée sur toutes les tables . Faire 
            # appel à cette procédure sur les tables ou' elle n'est pas présente  renvoit une erreur
            
        try:    
            df_fk=pd.read_sql(f'call check_integrity_fk_{i}()', con=connector)
        except:
            continue
            
        temp_=[i,count.iloc[0,0] ,df_rep.shape[0], list( df_rep.iloc[:,0].values) ]
        temp_+=[ df_null.shape[0], list(df_null.iloc[:,0].values)  ] 
        temp_+=[df_fk.shape[0], list(df_fk.iloc[:,0].values) ]
        
        #insertion des enregistrements de métriques de vérification pour lesquelles 
        #toute liste vide renvoyée est remplacée par 0
        
        log_tables[i]=[0 if not value else value for value in temp_]
        
    
    log_tables=log_tables.transpose().to_dict('records')
    
    #journal des performances des procedures
    
    log_pro=pd.DataFrame(index=labels_fig7, columns=columns_fig7).transpose()
    for procedure in choice_procedures:
        
        
        
# pour chaue procédure choisi, on extrait à partir des tables systèmes de la BD 
# la durée moyenne d'exécution, la dernirèe durée enregistrée, ainsi que l'heure de sa dernière exécution
        
        start_='DATE_SUB(NOW(), INTERVAL (SELECT VARIABLE_VALUE FROM performance_schema.global_status WHERE VARIABLE_NAME="UPTIME") - TIMER_START*10e-13 second)'
        duration_='TRUNCATE(TIMER_WAIT/1000000000000, 6)' 
        duration_mean=f'(SELECT AVG({duration_}) FROM performance_schema.events_statements_history_long WHERE OBJECT_TYPE LIKE "PROCEDURE" AND OBJECT_NAME LIKE "{procedure}" AND errors=0 )'
        statement=f'SELECT {start_} as last_start, {duration_} as last_duration, {duration_mean} as mean_duration FROM performance_schema.events_statements_history_long'
        statement+=f' WHERE OBJECT_TYPE LIKE "PROCEDURE" AND OBJECT_NAME LIKE "{procedure}" AND errors=0'
        statement+=f' ORDER BY THREAD_ID DESC, EVENT_ID DESC limit 1 ;'
        temp_=pd.read_sql(statement, con=connector)
        
    
  # instruction donnée définir la liste finale à intégrer au journal des procédures, ce ne fonction si cette dernière est 
        if not temp_.empty:
            temp_=[procedure]+list(temp_.iloc[0,:].values)
        else:
            temp_=[procedure]+[0,0,0]
        log_pro[procedure]=temp_

         
    log_pro=log_pro.transpose().to_dict('records')
    #columns_fig6=['tables', 'records', 'repetitions', 'id_repetitions',
    #'values_null', 'id_values_null', 'fk_unreferenced', 'id_fk_un']"""
        
        
    return graph1, graph2_A, graph2_B, graph3, graph4, log_events, log_tables, log_pro
  
    
    


# In[45]:


if __name__ == "__main__":
    print("server initialized....")
    app.run_server(debug=True, host='127.0.0.1', port='37709')
    
    


# In[156]:


#res=requests.get('http://127.0.0.1:37709').status_code
#res


# In[ ]:





# In[ ]:





# In[ ]:





# In[172]:





# In[ ]:



    


# In[ ]:





# In[ ]:





# In[ ]:





# In[18]:


"""graph1=go.Figure(layout_title_text='Circulation des flux de données')
axe_x=list(dataSQL[0:-1].index)
axe_y1=list(dataSQL[0:-1]['Bytes_received'].values)
axe_y2=list(dataSQL[0:-1]['Bytes_sent'].values)
graph1.add_trace(go.Scatter(x=axe_x, y=axe_y1 , name='Bytes_received'  ))
   graph1.add_trace(go.Scatter(x=axe_x, y=axe_y2, name= 'Bytes_sent' ))"""
   


# In[ ]:





# In[19]:


"""
liste_colonnes=('Binlog_cache_disk_use', 'Binlog_cache_use', 'Binlog_stmt_cache_use','Binlog_stmt_cache_disk_use', 'Handler_commit', 'Handler_delete', 'Handler_discover',
'Handler_external_lock', 'Handler_mrr_init', 'Handler_prepare', 'Handler_read_first', 'Handler_read_key', 'Handler_read_last',
'Handler_read_next', 'Handler_read_prev', 'Handler_read_rnd', 'Handler_read_rnd_next', 'Handler_rollback', 'Handler_savepoint',
'Handler_savepoint_rollback', 'Handler_update', 'Handler_write', 'Innodb_buffer_pool_bytes_data', 'Innodb_buffer_pool_pages_free','Innodb_buffer_pool_pages_total','Threads_connected', 'Threads_running', 'Connections', 'Connection_errors_internal', 'Bytes_received', 'Bytes_sent', 'Aborted_connects')
connector=connector_mysql('mysql+pymysql', 'root', 'root', 'localhost', 'essai_cobtest_2' )
Y.append( pd.read_sql(f'SHOW GLOBAL STATUS WHERE VARIABLE_NAME in {liste_colonnes} or VARIABLE_NAME LIKE "%%HANDLER%%" ',con=connector )['Value'].astype(int).values )
if len(Y)>1:
        
        Y[-2]=Y[-1]-Y[-2]
X.append( datetime.now() )

labels= pd.read_sql(f'SHOW GLOBAL STATUS WHERE VARIABLE_NAME in {liste_colonnes} or VARIABLE_NAME LIKE "%%HANDLER%%" ',con=connector )['Variable_name'].values 
dataSQL=pd.DataFrame(data=[i for i in Y], columns=labels,  index=X )
dataSQL=dataSQL.astype(int)

#Calcul de la moyenne des performances, par tranche de 10 secondes
dataSQL=dataSQL.resample('10S').mean()    
for colonne in dataSQL.columns:
    dataSQL[colonne]=dataSQL[colonne].fillna(dataSQL[colonne].mean() )
    
graph1=go.Figure(layout_title_text='Circulation des flux de données')
axe_x=list(dataSQL[0:-1].index)
axe_y1=list(dataSQL[0:-1]['Bytes_received'].values)
axe_y2=list(dataSQL[0:-1]['Bytes_sent'].values)
graph1.add_trace(go.Scatter(x=axe_x, y=axe_y1 , name='Bytes_received'  ))
graph1.add_trace(go.Scatter(x=axe_x, y=axe_y2, name= 'Bytes_sent' ))
graph1"""


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[320]:


"""# création de la classe 'graph' pour modéliser le graphique entre 2 variables
class graph():
    
    def __init__(self, type_graph, titre):
        
        self.dataSQL=dataSQL
        self.axeX=dataSQL.index
        self.axeY=dataSQL
        self.type_graph=type_graph
        self.figure_=go.Figure(layout_title_text=titre)
        
        
# définition des opérations mathématiques possibles entre les variables

    def operation(self, type_op, variable_initiale, variable_modifiante):
        if type_op=='+':
            self.axeY[variable_initiale]=self.axeY[variable_initiale]+self.axeY[variable_modifiante]
        elif type_op=='-':
            self.axeY[variable_initiale]=self.axeY[variable_initiale]-self.axeY[variable_modifiante]
        elif type_op=='*':
            self.axeY[variable_initiale]=self.axeY[variable_initiale]*self.axeY[variable_modifiante]
        else:
            self.axeY[variable_initiale]=self.axeY[variable_initiale]/self.axeY[variable_modifiante]      
        
# définition des listes de variables et des légendes

    def courbe (self, liste_variables, liste_legende):
        variables=[i for i in liste_variables]
        legende={i:le for le,i in zip(liste_legende, variables)}
        
        
#sélection des enregistrements correspondants aux variables voulues de la table SQL "Status Global
                
        if  self.type_graph=='Scatter':
            for v in variables:
                 self.axeX=list(self.axeX[0:-1])
                 liste_Y=list(self.axeY[0:-1][v])
                 self.figure_.add_trace(go.Scatter(x=self.axeX , y=liste_Y,  name=legende[v]))
                # ici le dernier 
#enregistrement est ignoré vu que ce dernier n'a pas été pondéré au reste des enregistrements antérieurs    
                
        elif self.type_graph=='Pie':    
        #sélection de l'enregistrements la plus récente et non pondérée aux enregistrements antérieurs, 
        #ce pour les  variables voulues de la table SQL "Status Global".
            
            self.axeY=list(self.axeY[variables].iloc[-1].values)  # utilisation de list() car la commande df.valeurs renvoie un array
            self.figure_.add_trace( go.Pie ( labels=liste_legende,values=self.axeY))
    
    
    def show_(self):
        return self.figure_.show()
 


    
print('graphic definition done....') 
print('graphic definition"s beginning...')"""


# In[321]:


"""ressources: -création de multiples graphiques dynamiques: https://medium.com/analytics-vidhya/plotting-multiple-figures-with-live-data-using-dash-and-plotly-4f5277870cd7
-https://medium.com/@ooly/create-a-dynamic-dashboard-using-plotly-dash-and-python-absolute-beginner-guide-aa379a259cd2
-https://tomaztsql.wordpress.com/2018/06/18/real-time-data-visualization-with-sql-server-and-python-dash/
-https://plotly.com/python/creating-and-updating-figures/
-https://plotly.com/python/line-and-scatter/
-https://plotly.com/python-api-reference/generated/plotly.graph_objects.Scatter.html
-https://community.plotly.com/t/create-traces-dynamically-for-scatter-plot/8860/4
-https://medium.com/analytics-vidhya/plotting-multiple-figures-with-live-data-using-dash-and-plotly-4f5277870cd7
-https://medium.com/@lowweihong/simple-steps-to-build-a-live-stream-dashboard-using-python-dash-23562dea9d3f

"""


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




