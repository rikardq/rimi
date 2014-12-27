# coding: utf8
from isoweek import Week


instructor_id = 1
leasons = db(db.owner_of_leason.instructor_id==instructor_id).select(db.owner_of_leason.leason_id)
today=date.today()
today_wd = today.weekday()

dayz = ("Måndag","Tisdag","Onsdag","Torsdag","Fredag","Lördag","Söndag")

### DISPLAY VARIABLES
if session.num_of_date_rows is None:
    num_of_date_rows = 4 #default is 4.  1, 2, 3, 4 or 6 
else:
    num_of_date_rows = int(session.num_of_date_rows)

def index():
    week_display()
    ### The variable startday determines which day to base the view dates from. Default is today
    if session.startday is None:
        session.startday = today

    # Set variable from session
    startday = session.startday 
    master = {}
    # column division for bootstrap. 
    col_division = 12/num_of_date_rows


    for day in dayz:
        leasons_for_this_day = []
        for leason in leasons:
            if len(db((db.leason.id==leason.leason_id)&(db.leason.week_day==day)).select()) > 0:
                leasons_for_this_day.append(leason.leason_id)
                # Add weekday to master dict since we have a leason for it ,unless its in there already
                if day not in master:
                    master[day] = {}

        for leason in leasons_for_this_day: 
            master[day][leason] = {}
            # Find first available date for this weekday
            startdate = get_firstdate_weekday(reverse_translate_weekday(db.leason[leason].week_day), startday)

            startpoint = 0 

            while num_of_date_rows > startpoint: 
                master[day][leason][startdate] = {}
                riders, available_slots = prepped_leason_info(leason, startdate)
                master[day][leason][startdate]["available_slots"] = available_slots
                master[day][leason][startdate]["riders"] = riders 

                startpoint = startpoint + 1
                startdate = startdate + timedelta(+7)


    return dict(col_division=col_division, startday=startday,master=master) 


def prepped_leason_info(leason_id, leason_date):
    # returns a dict with available slots and 
    # returns a dict of customers with their status
    # 
    data = {}
    num_riders,num_rebooks,num_canx,num_total,reg_riders,canx_riders,rebook_riders,leason_time = leason_info(leason_date,leason_id)
    max_customers = int(db(db.leason.id==leason_id).select()[0]['max_customers'])
    available_slots = max_customers - num_riders - num_rebooks + num_canx 

    for reg_rider in reg_riders:
        if reg_rider in canx_riders:
            divclass = "danger"
        else:
            divclass = "success"
        data[reg_rider["first_name"] + " " + reg_rider["last_name"]] = divclass

    for rebook_rider in rebook_riders:
        divclass="info"
        data[rebook_rider["first_name"] + " " + rebook_rider["last_name"]] = divclass

    return data, available_slots

def change_num_of_date_rows(): 
    # Function to change how many columns or date rows should be displayed. 
    session.num_of_date_rows = request.args(0) 
    # refresh view
    redirect(URL('index'),client_side=True)

def update_week():
    session.week = int(request.args(0))
    session.year = int(request.args(1))
    # refresh view
    redirect(URL('index'),client_side=True)

def week_display():
    # Default view is the current week. 
    if session.week is None:
        session.week = Week.thisweek()[1]
        session.year = date.today().year

    week = session.week
    year = session.year

    # some years end in week 53, others in week 52
    lastweekofyear = Week.last_week_of_year(year)[1]
    # If it is the last week of the year, fix forward button
    if lastweekofyear == week:
        forward = {"week":1,"year":year + 1}
    else:
        forward = {"week":week + 1,"year":year}
    # If it is the first week of the year, fix back button
    if week == 1:
        back = {"week":Week.last_week_of_year(year - 1)[1],"year":year - 1}
    else:
        back = {"week":week - 1,"year":year}

    # Our startdate will be current week, beginning with monday
    # set remaining sessions to new values and move on
    session.startday = Week(year, week).monday()
    session.back = back
    session.forward = forward
    session.week = week
    session.year = year 
