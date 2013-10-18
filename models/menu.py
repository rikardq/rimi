# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A(B('rimi',SPAN(69),'AB'),XML('&trade;&nbsp;'),
                  _class="brand",_href="http://static2.fjcdn.com/comments/and+this+is+why+I+hate+bronies+_203739da12cc5a9f5f9916419dbcf2b7.jpg")
response.title = request.application.replace('_',' ').title()
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Your Name <you@example.com>'
response.meta.description = 'a cool new app'
response.meta.keywords = 'web2py, python, framework'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
    (T('Home'), False, URL(c='default',f='index'), []),
    (T('Customer'), False, URL(c='customer', f='index'), []),
    (SPAN('Instructor'), False, URL(c='instructor'), [
        (T('View Week'), False, URL(c='instructor', f='view_leasons_week'), []),
        (T('View Day'), False, URL(c='instructor', f='view_leasons_day'), [])
    
    ])
]


if "auth" in locals(): auth.wikimenu() 
