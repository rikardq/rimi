# coding: utf8

from gluon.tools import Crud
crud = Crud(db)

formaccepted = "Informationen har lagts in."

def index():
    form = ""
    return dict(form=form)

def add_horse():
    form = SQLFORM(db.horse)
    if form.process().accepted:
        response.flash = formaccepted 
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill out the form'
    return dict(form=form)

def horses():
    form = crud.create(db.horse, next=URL('horses'),
        message=T("Hästen inlagd"))
    horses = crud.select(db.horse, fields=["name","status","horse_type"])
    return dict(form=form,horses=horses)

def customers():
    form = crud.create(db.customer, next=URL('customers'),
        message=T("Kunden inlagd"))
    customers = crud.select(db.customer, fields=["first_name", "last_name","auth_user_id","credits","status"])
    return dict(form=form,customers=customers)

def leasons():
    form = crud.create(db.leason, next=URL('leasons'),
        message=T("Lektionen inlagd"))
    leasons = crud.select(db.leason, fields=["week_day","leason_time","leason_length","max_customers","skill_level","status","leason_type"])
    return dict(form=form,leasons=leasons)

def levels():
    form = crud.create(db.skill_level, next=URL('levels'),
        message=T("Ny nivå inlagd"))
    levels = crud.select(db.skill_level, fields=["skill_name","skill_point","skill_type"])
    return dict(form=form,levels=levels)

def blackdates():
    form = crud.create(db.black_dates, next=URL('blackdates'),
        message=T("Datum inlagt"))
    blackdates = crud.select(db.black_dates, fields=["black_date"])
    return dict(form=form,blackdates=blackdates)

def link_c2a():
    #Handles linking auth_user to actual customer. One auth_user can be linked to multiple 
    # customers to handle family accounts etc
    # Default view should be any auth_user not linked to a customer
    # Passed argument request.args(0) should be customer_id
    try:
        customers_with_authuser = []
        s = db(db.customer.auth_user_id!=None).select(db.customer.auth_user_id)
        for e in s:
            customers_with_authuser.append(e.auth_user_id)
    except:
        error = "Inga registrerade användare finns som inte är linkade till en kund."

    authusers_without_customer = []

    au = db(db.auth_user).select(db.auth_user.id)
    for e in au:
        if e.id not in customers_with_authuser:
            authusers_without_customer.append(e.id)

    message = []
    for auid in authusers_without_customer:
        authuser = db(db.auth_user.id==auid).select()[0]
        message.append(authuser.first_name)
    return dict(message=message)

