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

def index():
    return dict(message="w00t")

def view_leason():
    leason_id = request.args(0)
    thisdate = request.args[1]
    thisdate = date(int(thisdate[:4]),int(thisdate[5:7]),int(thisdate[8:10]))
    thisweekday = translate_weekday(thisdate.weekday())
    leason_data = db(db.leason.id == leason_id).select()[0]
    num_riders,num_rebooks,num_canx,num_total,reg_riders,canx_riders,rebook_riders,leason_time = leason_info(thisdate,leason_id)
    return locals()

def view_leasons_day():
    #Check if date carried over, if not assume today
    if len(request.args) == 0: 
        thisdate = datetime.today().date()
    else:
        thisdate = request.args[0]
        thisdate = date(int(thisdate[:4]),int(thisdate[5:7]),int(thisdate[8:10]))
    thisweekday = translate_weekday(thisdate.weekday())
    leason_data = []

    # See what leasons matches this weekday for this instructor
    for leason in leasons:
        leason_id = leason["leason_id"]
        if db(db.leason.id==leason_id).select(db.leason.week_day)[0]["week_day"] == thisweekday:
            num_riders,num_rebooks,num_canx,num_total,reg_riders,canx_riders,rebook_riders,leason_time = leason_info(thisdate,leason_id)
            leason_data.append([str(leason_time)[:5],num_riders,num_total,num_rebooks,num_canx,leason_id])
            

        
    return dict(leason_data=leason_data,thisdate=thisdate,thisweekday=thisweekday)
    
    


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
    weekdays = ["Måndag","Tisdag","Onsdag","Torsdag","Fredag","Lördag","Söndag"]

    # Go through the leasons and place them into appropriate spot in week dict
    for leason in leasons:
        try:
            ldata = db(db.leason.id==leason.leason_id).select()[0]
            # this leasons date in this view
            this_date = datez[ldata.week_day]
            # Use internal function to retrieve statistics and rider details(rider details will not be used here)
            num_riders,num_rebooks,num_canx,num_total,reg_riders,canx_riders,rebook_riders,leason_time = leason_info(this_date,ldata.id)

            display_week[ldata.week_day].append({"leason_time":str(ldata.leason_time)[:5],"id":int(ldata.id),"num_riders":num_riders,"num_rebooks":num_rebooks,"num_canx":num_canx, "num_total":num_total,"this_date":this_date})
        except:
            error.append("Unable to add data for record " + str(ldata.id)) 

    # Sort the entries, then dump the dict and return a list instead
    for day in display_week:
        daylist = display_week[day]
        if daylist > 0:
            daylist = sorted(daylist, key=lambda k: k['leason_time'])
            for entry in daylist:
                # Just create a sorted list
                display_week2[day].append([entry["leason_time"],entry["num_riders"],entry["num_total"],entry["num_rebooks"],entry["num_canx"],entry["id"]])

    # Lets not do this, it will mess with the data when it is updated, and when a user uses the back button. Keep querying the db everytime. Save the display_week variable in the session
    session.display_week = display_week2
    return locals() 



def assign_horse(cust_id, horse_id, leason_id, reserved_date):
    db.reserved_horses.validate_and_insert(id_customer=cust_id, id_horse=horse_id, id_leason=leason_id, reserved_date=reserved_date)

def view_rebooking_requests():
    something
