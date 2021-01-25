#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# In[1]:


# définition de la barre de navigation
import dash_bootstrap_components as dbc
import dash_auth

def Navbar():
    navbar = dbc.NavbarSimple(
           children=[
              dbc.DropdownMenu(
                 nav=True,
                 in_navbar=True,
                 label="Menu",
                 children=[
                    dbc.DropdownMenuItem('tableau de monitoring',href='/dashboard_monitoring.py'),
                    dbc.DropdownMenuItem('tableau de visionnage',href='/dashboard_view.py'),
                    dbc.DropdownMenuItem(divider=True),
                          ],
                      ),
                    ],
          brand='page d accueil',
          brand_href='/homepage.py',
          sticky="top",
        )
    return navbar


# In[ ]:





# In[ ]:




