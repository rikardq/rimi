from datetime import datetime
from datetime import date
from datetime import timedelta
from time import mktime
# coding: utf8
#
# Definition of some common functions used, for now, in customer.py controller.
#

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
    active_semester = db(db.admin_settings.variable_name=="active_semester").select()[0]
    semester_info = db(db.semester.id==active_semester.variable_value).select()[0]
    return active_semester.variable_value, semester_info.start_date, semester_info.end_date

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

# This functions usage is questionable, and will be reworked
def get_rebooked_leasons(cust_id):
    xleasons = []
    q=(db.rebooking.id_customer==cust_id)
    s=db(q).select()
    if len(s) > 0:
        for entry in s:
            xleasons.append({"leason_date":entry["leason_date"], "leason_id":entry["id_leason"]})
    return xleasons

# Gather all black dates from the active semester and return them as a list 
def get_black_dates():
    active_semester, start_date, end_date = retrieve_current_semester()
    xleasons = []
    q=(db.black_dates.black_date >= start_date) & (db.black_dates.black_date <= end_date)
    s=db(q).select(db.black_dates.black_date)
    if len(s) > 0:
        for entry in s:
            xleasons.append(entry["black_date"])
    return xleasons

# Retrieve any administrator cancelled leasons for a leason_id:
# Lets just do it regardless of date range, this table will be scarcely
# populated and performance will not suffer...
def canxbyadmin(thedate,leason_id):
    q=(db.admin_cancelled_leason.id_leason==leason_id) & (db.admin_cancelled_leason.leason_date == thedate)
    s=db(q).select(db.admin_cancelled_leason.leason_date)
    if len(s) > 0:
        return True
    else:
        return False

    

# A function to retrieve a date for the first weekday entry from start_date 
# i.e if it is september 3rd, a tuesday today and our weekday is thursday
# then return the date september 5th
# The argument are: 
# weekday, a numeric value representing a day,0=mon, 6=sun
# start_date, a datetime.date variable containing what we consider to be "today" 
def get_firstdate_weekday(weekday,start_date):
    # Figure out what the start_dates weekday is
    start_date_weekday = start_date.weekday()
    # Add 1 to the weekday we were passed. Also add 1 to the start_date_weekday
    # so they match. Math is hard when Monday is 0    
    weekday = weekday + 1
    start_date_weekday = start_date_weekday + 1
    # There are 3 possibilites, the weekday is before the start_date_weekday
    # or it is the same, or it is after. If it is the same, the start_date
    # remains the same
    if weekday == start_date_weekday:
        days_to_add = 0
    # If it is before, figure out the diff and then subtract the diff
    # from a full week. Adding this to start_date gets you the next "hit"
    # of that weekday 
    elif start_date_weekday > weekday:
        days_differ = start_date_weekday - weekday
        days_to_add = 7 - days_differ
    # If it is after, we simply subtract it
    elif start_date_weekday < weekday:
        days_to_add = weekday - start_date_weekday

    # Now we know how many days to add to start_date to get the next
    # available date that is a weekday
    start_date = start_date + timedelta(days=days_to_add)
    return start_date

# Used to convert a datetime.date object into an int representing
# epoch in milliseconds
def convert_dt_to_epoch(dt,dtt):
    # Use the combine function to combine the datetime.date and the datetime.time
    # into a datetime.datetime object. 
    dtdt = datetime.combine(dt,dtt)
    # Get epoch in seconds
    secs = mktime(dtdt.timetuple()) + dtdt.microsecond/1000000.0
    # Get epoch in millis, convert to int
    millis = int(secs * 1000)
    return millis

# Check if a cancellation request is requested within the ordered timeframe
# Returns true if request is within the timeframe specified in admin_settings 
def check_canx_time(leason_id):
    leason_time = db(db.leason.id==leason_id).select(db.leason.leason_time)[0]["leason_time"]
    hours_before_canx = int(db(db.admin_settings.variable_name=="hours_before_canx").select()[0]["variable_value"])
    last_call = datetime.today() + timedelta(hours=hours_before_canx)
    leason = (datetime.combine(date.today(), leason_time))
    if last_call > leason:
        return False
    else:
        return True

# Alters a customers credits
def alter_credit(what,who,howmuch):
    if what == "add":
        new = db.customer[who].credits + howmuch
        db.customer[who]=dict(credits=new)
    if what == "subtract":
        new = db.customer[who].credits - howmuch
        db.customer[who]=dict(credits=new)

# Obtain leason information. This function is heavily used in instructor.py
# to retrieve up-to-date info on a leason

def leason_info(this_date,leason_id):
    leason_time = db(db.leason.id==leason_id).select(db.leason.leason_time)[0]["leason_time"]
    num_riders = db((db.leasons.id_leason==leason_id)&(db.customer.id==db.leasons.id_customer)&(db.customer.status=="Active")).count()
    num_rebooks = db((db.rebooking.id_leason==leason_id) & (db.rebooking.approval=="yes") & (db.rebooking.leason_date==this_date)).count()
    num_canx = db((db.cancelled_leasons.id_leason==leason_id) & (db.cancelled_leasons.cancelled_date==this_date)).count()
    num_total= num_riders - num_canx + num_rebooks
    reg_riders = db((db.leasons.id_leason==leason_id)&
        (db.customer.id==db.leasons.id_customer)&
        (db.customer.status=="Active")).select(db.customer.first_name,db.customer.last_name)

    canx_riders = db((db.cancelled_leasons.id_leason==leason_id) &
        (db.cancelled_leasons.cancelled_date==this_date) & 
        (db.customer.id==db.cancelled_leasons.id_customer)).select(db.customer.first_name,db.customer.last_name)

    rebook_riders = db((db.rebooking.id_leason==leason_id) & 
        (db.rebooking.approval=="yes") & 
        (db.rebooking.leason_date==this_date) & 
        (db.customer.id==db.rebooking.id_customer)).select(db.customer.first_name,db.customer.last_name)

    return num_riders,num_rebooks,num_canx,num_total,reg_riders,canx_riders,rebook_riders,leason_time


def get_horse_info(leason_id,leason_date,customer_id):
    q = (db.reserved_horses.id_leason == leason_id) & (db.reserved_horses.id_customer == customer_id) & (db.reserved_horses.reserved_date == leason_date)
    try:
        horse_id = db(q).select(db.reserved_horses.id_horse)[0]["id_horse"]
        horse_name = db(db.horse.id == horse_id).select(db.horse.name)[0]["name"]
    except:
        horse_name = None
    return horse_name 

