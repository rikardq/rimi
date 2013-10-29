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

