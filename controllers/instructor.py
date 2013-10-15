# coding: utf8
from isoweek import Week


instructor_id = 1
leasons = db(db.owner_of_leason.instructor_id==instructor_id).select(db.owner_of_leason.leason_id)
today=date(year=datetime.now().year,month=datetime.now().month,day=datetime.now().day)


"""
What should be here?
What can an instructor do?

- Can make announcements to its groups via Infoboard system
- Can cancel individual dates on one of their leasons
- See the leasons that they are responsible for, default today
- Administrate horse-selections to its leasons/riders
"""

def test():
    return(obtain_leason_dates(1))

def obtain_leason_info(leasonswd):
    # Sort the list of dicts
    sortedleasons = sorted(leasonswd, key=lambda k: k['leason_time'])
    return sortedleasons

"""
    leason_info = db(db.leason.id==leason_id).select()[0]
    weekday = leason_info.week_day
    numweekday = reverse_translate_weekday(weekday) 
    leason_startdate = get_firstdate_weekday(numweekday, today)

    return dict(a=leason_info,b=weekday,c=numweekday,d=leason_startdate)
"""





def view_leasons_week():
    # Default view is the current week. We will return a dict, consisting of keys 1-7 each
    # with its corresponding weekdays worth of leasons as values
    # Check to see if we carried a week with us
    if len(request.args):
        week = int(request.args[0])
    else: 
        week = Week.thisweek()[1]
    # Check to see if we also carried a year with us
    try: 
        year = int(request.args[1])
    except:
        year = date.today().year

    lastweekofyear = Week.last_week_of_year(year)[1]

    # If it is the last week of the year, fix forward button 
    if lastweekofyear == week:
        forwardweek = 1
        forwardyear = year + 1
    else:
        forwardweek = week + 1
        forwardyear = year 
    # If it is the first week of the year, fix back button
    if week == 1: 
        backyear = year -1
        backweek = Week.last_week_of_year(backyear)[1] 
    else:
        backyear = year
        backweek = week - 1

    error = []

    datez = {"Måndag":Week(year, week).monday(),
    "Tisdag":Week(year, week).tuesday(),
    "Onsdag":Week(year, week).wednesday(),
    "Torsdag":Week(year, week).thursday(),
    "Fredag":Week(year, week).friday(),
    "Lördag":Week(year, week).saturday(),
    "Söndag":Week(year, week).sunday()}
    display_week = {"Måndag":[],"Tisdag":[],"Onsdag":[],"Torsdag":[],"Fredag":[],"Lördag":[],"Söndag":[]}
    display_week2 = {"Måndag":[],"Tisdag":[],"Onsdag":[],"Torsdag":[],"Fredag":[],"Lördag":[],"Söndag":[]}

    # Go through the leasons and place them into appropriate spot in week dict
    for leason in leasons:
        try:
            ldata = db(db.leason.id==leason.leason_id).select()[0]
            # this leasons date in this view
            this_date = datez[ldata.week_day]
            num_riders = db(db.leasons.id_leason==ldata.id).count()
            num_rebooks = db((db.rebooking.id_leason==ldata.id) & (db.rebooking.approval=="yes") & (db.rebooking.leason_date==this_date)).count()
            num_canx = db((db.cancelled_leasons.id_leason==ldata.id) & (db.cancelled_leasons.cancelled_date==this_date)).count() 
            num_total= num_riders - num_canx + num_rebooks
            display_week[ldata.week_day].append({"leason_time":str(ldata.leason_time)[:5],"id":int(ldata.id),"num_riders":num_riders,"num_rebooks":num_rebooks,"num_canx":num_canx, "num_total":num_total})
        except:
            error.append("Unable to add data for record ",ldata.id) 

    # Sort the entries, then dump the dict and return a list instead
    for day in display_week:
        daylist = display_week[day]
        if daylist > 0:
            daylist = sorted(daylist, key=lambda k: k['leason_time'])
            for entry in daylist:
                # Make the fucking link and display here:
                #display_week2[day].append([entry["leason_time"],entry["num_total"],entry["num_rebooks"],entry["num_canx"],entry["id"]])
                display_week2[day].append(A(entry["leason_time"], _href=URL('fuck', args=[entry["id"]])))
               # display_week2[day] = daylist


    return locals() 



def assign_horse(cust_id, horse_id, leason_id, reserved_date):
    db.reserved_horses.validate_and_insert(id_customer=cust_id, id_horse=horse_id, id_leason=leason_id, reserved_date=reserved_date)

def view_rebooking_requests():
    something
