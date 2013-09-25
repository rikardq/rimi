# coding: utf8
#
# Definition of some common functions used, for now, in customer.py controller.
#
import time
import datetime



def translate_weekday(weekd):
    if weekd == 0: weekday = "Måndag"
    elif weekd == 1: weekday = "Tisdag"
    elif weekd == 2: weekday = "Onsdag"
    elif weekd == 3: weekday = "Torsdag"
    elif weekd == 4: weekday = "Fredag"
    elif weekd == 5: weekday = "Lördag"
    elif weekd == 6: weekday = "Söndag"
    return weekday

def reverse_translate_weekday(weekd):
    if weekd == "Måndag": weekday = 0
    elif weekd == "Tisdag": weekday = 1
    elif weekd == "Onsdag": weekday = 2
    elif weekd == "Torsdag": weekday = 3
    elif weekd == "Fredag": weekday = 4
    elif weekd == "Lördag": weekday = 5
    elif weekd == "Söndag": weekday = 6
    return weekday

def retrieve_current_semester():
    active_semester = db(db.active_semester).select()[0]
    return active_semester.id_semester

def get_cancelled_leasons(cust_id,leason_id):
    xleasons = []
    q=(db.cancelled_leasons.id_customer==cust_id)&(db.cancelled_leasons.id_leason==leason_id)
    s=db(q).select(db.cancelled_leasons.cancelled_date)
    if len(s) > 0:
        for entry in s:
            xleasons.append(entry["cancelled_date"])
    return xleasons

def get_leason_history(cust_id,leason_id):
    xleasons = []
    q=(db.leasons_history.id_customer==cust_id)&(db.leasons_history.id_leason==leason_id)
    s=db(q).select(db.leasons_history.leason_date)
    if len(s) > 0:
        for entry in s:
            xleasons.append(entry["leason_date"])
    return xleasons

def get_black_dates(active_semester):
    # Here we select all the black dates from the active semester
    xleasons = []
    q=(db.black_dates.id_semester==active_semester)
    s=db(q).select(db.black_dates.black_date)
    if len(s) > 0:
        for entry in s:
            xleasons.append(entry["black_date"])
    return xleasons
