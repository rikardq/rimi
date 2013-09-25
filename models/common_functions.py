# coding: utf8
#
# Definition of some common functions used, for now, in customer.py controller.
#
import time
import datetime

# Used to translate results from datetime.weekday results(numeric) into what the 
# table leason stores the weekdays as, Swedish string.
def translate_weekday(weekd):
    if weekd == 0: weekday = "Måndag"
    elif weekd == 1: weekday = "Tisdag"
    elif weekd == 2: weekday = "Onsdag"
    elif weekd == 3: weekday = "Torsdag"
    elif weekd == 4: weekday = "Fredag"
    elif weekd == 5: weekday = "Lördag"
    elif weekd == 6: weekday = "Söndag"
    return weekday

# Used since we store day of the week in the leason table as a Swedish string.
# Some datemodifications and calculations requires us to replace this with 
# a numeric value instead 
def reverse_translate_weekday(weekd):
    if weekd == "Måndag": weekday = 0
    elif weekd == "Tisdag": weekday = 1
    elif weekd == "Onsdag": weekday = 2
    elif weekd == "Torsdag": weekday = 3
    elif weekd == "Fredag": weekday = 4
    elif weekd == "Lördag": weekday = 5
    elif weekd == "Söndag": weekday = 6
    return weekday

# Retrieve the currently selected semester
def retrieve_current_semester():
    active_semester = db(db.active_semester).select()[0]
    return active_semester.id_semester

# This functions usage is questionable, and will be reworked
def get_cancelled_leasons(cust_id,leason_id):
    xleasons = []
    q=(db.cancelled_leasons.id_customer==cust_id)&(db.cancelled_leasons.id_leason==leason_id)
    s=db(q).select(db.cancelled_leasons.cancelled_date)
    if len(s) > 0:
        for entry in s:
            xleasons.append(entry["cancelled_date"])
    return xleasons

# This functions usage is questionable, and will be reworked
def get_leason_history(cust_id,leason_id):
    xleasons = []
    q=(db.leasons_history.id_customer==cust_id)&(db.leasons_history.id_leason==leason_id)
    s=db(q).select(db.leasons_history.leason_date)
    if len(s) > 0:
        for entry in s:
            xleasons.append(entry["leason_date"])
    return xleasons

# Gather all black dates from the active semester and return them as a list 
def get_black_dates(active_semester):
    xleasons = []
    q=(db.black_dates.id_semester==active_semester)
    s=db(q).select(db.black_dates.black_date)
    if len(s) > 0:
        for entry in s:
            xleasons.append(entry["black_date"])
    return xleasons
