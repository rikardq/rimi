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

def obtain_leason_dates(leason_id):
    leason_info = db(db.leason.id==leason_id).select()[0]
    weekday = leason_info.week_day
    numweekday = reverse_translate_weekday(weekday) 
    leason_startdate = get_firstdate_weekday(numweekday, today)
    return dict(a=leason_info,b=weekday,c=numweekday,d=leason_startdate)





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
        #If we did not carry, assume current year


    # Check to see if this si the last week and prep the carryovers
    lastweekofyear = Week.last_week_of_year(year)[1]

    if lastweekofyear == week:
        forward = 1
        forwardyear = year + 1
    else:
        forward = week + 1
    backz = week - 1

    error = []
    firstdayinweek = Week(year, week).monday()

    datez = {"Måndag":Week(year, week).monday(),
    "Tisdag":Week(year, week).tuesday(),
    "Onsdag":Week(year, week).wednesday(),
    "Torsdag":Week(year, week).thursday(),
    "Fredag":Week(year, week).friday(),
    "Lördag":Week(year, week).saturday(),
    "Söndag":Week(year, week).sunday()}
    display_week = {"Måndag":[],"Tisdag":[],"Onsdag":[],"Torsdag":[],"Fredag":[],"Lördag":[],"Söndag":[]}

    # Go through the leasons and place them into appropriate spot in week dict
    for leason in leasons:
        try:
            ldata = db(db.leason.id==leason.leason_id).select()[0]
            display_week[ldata.week_day].append({"leason_time":ldata.leason_time,"id":ldata.id,"week_day":ldata.week_day,"status":ldata.status})
        except:
            error.append("Unable to add data for record ",ldata.id) 
    return locals() 



def assign_horse(cust_id, horse_id, leason_id, reserved_date):
    db.reserved_horses.validate_and_insert(id_customer=cust_id, id_horse=horse_id, id_leason=leason_id, reserved_date=reserved_date)

def view_rebooking_requests():
    something
