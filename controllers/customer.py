# coding: utf8
import json
from datetime import datetime
from datetime import date
from datetime import timedelta
from datetime import time as dttime
from time import time
#
# This is the controller for kund, or customer view. All administration that a end-customer can do with their leasons should reside here.
#
#
#@auth.requires_login()
def index():
    cust_id = 1
    helper = "Denna kalender visar dom lektionerna du rider. Du kan även se avbokade lektioner och dina igenridningar. För att boka av en lektion så väljer du det datum och lektion som du vill avboka, och tryck sedan Avboka lektion."
    return dict(helper=helper,cust_id=cust_id)

def rebook():
    message = "Rebooking calendar is displayed here!"
    return dict(message=message)

"""
The events is where the calendar widget retrives its events from.
We should override the call so we can send a customer id etc.
"""
#@auth.requires_login()
def rebookdates():
    # This function returns the json values. The calendar calls this function
    return list_rebookings(1)

def leasondates():
    # This function returns the json values. The calendar calls this function
    return list_leasondates(1)

def list_rebookings(customerid):
    # Watching execution time to try to catch resource hogs as I add them
    # The cust_id is the first argument in calling this function
    # But this is really bad. Uberbad. Do not do this. Query the database for the currently
    # logged in users user_id variable directly instead.
    #cust_id = request.args(0)
    cust_id = customerid
    #Aquire customers skill level
    # At the same time, generate a list of the customers leasons ID. this will be used later to 
    # exclude the customers own leasons, since they are not available for rebookings.
    customer_leasons = []
    # Create a default variable skill_level
    skill_level = 0
    try:
        # See if the customer has any leasons assigned
        res = db(db.leasons.id_customer==cust_id).select(db.leasons.id_leason)
        if len(res) > 0:
            # While we have this data , generate a list of the customers leasons ID. this will be used later to 
            # exclude the customers own leasons, since they are not available for rebookings.
            for row in res:
                customer_leasons.append(row.id_leason)

            # Defining the query here, not running it yet.
            # Select the customer from leasons, the leasons from leason and the skill_level from skill_Level....!
            q = (db.leasons.id_customer==cust_id)&(db.leasons.id_leason==db.leason.id)&(db.leason.skill_level==db.skill_level.id)
            try:
                # Try selecting all the skill points from the leasons this customer is associated with. Do a 
                # reverse order(note the tilde after orderby=) and select skill level as the first entry, which 
                # will be the highest
                rows = db(q).select(db.skill_level.skill_point,orderby=~db.skill_level.skill_point)
                if len(rows) > 0:
                    skill_level = int(rows[0]["skill_point"])
            except:
                #Something did not work, set skill level to 0
                skill_level = 0
    except:
        #Something did not work, set skill level to 0
        skill_level = 0



    # Lets get the active semester
    active_semester = retrieve_current_semester()

    # Retrieve a list of the black dates for that semester
    black_dates = get_black_dates(active_semester)

    # Todays date, in datetime.date format to stay consistent.
    today=date(year=datetime.now().year,month=datetime.now().month,day=datetime.now().day)

    # Attempt to get the max_rebook_days variable from the admin_settings table. IF it is not set, use the default of 31
    try:
        q = db(db.admin_settings.variable_name=="max_rebook_days").select()[0]
        max_rebook_days = int(q.variable_value)
    except:
        max_rebook_days = 31

    # Now we can create the stop_date
    stop_date = today + timedelta(days=max_rebook_days)


    #Loop through the weekdays, lookin in the tables for suitable leasons that could perhaps offer some
    # rerides.
    iterweekday = 0 # This represents monday, for our loop.
    leasons = []
    while iterweekday < 7:
        # Translate the weekday to swedish for db query
        weekday = translate_weekday(iterweekday)

        # Get a lists of leasons for todays weekday, based on the customers skill_level
        q = (db.leason.week_day==weekday)&(db.leason.skill_level==db.skill_level.id)&(db.skill_level.skill_point <= skill_level)
        rows = db(q).select(db.leason.max_customers,db.leason.id,db.leason.leason_time,db.leason.week_day,db.leason.leason_time)

        if len(rows) > 0:
            for row in rows:
                max_customers = row.max_customers 
                leason_id = row.id
                leason_time = row.leason_time 
                week_day = row.week_day 
                leason_time = row.leason_time 
                # For each leason, find out the active number of riders in this group
                # Except if this leason is one that the customer already rides in, he can 
                # not rebook in a leason he already rides in(how coudl you ride twice
                # in one leason? It is impossible.
                if leason_id not in customer_leasons:
                    try:
                        customers_in_leason = len(db(db.leasons.id_leason==leason_id).select())
                    except:
                        #Assume it is 0
                        customers_in_leason = 0
                    leasons.append({"weekday":weekday,"week_day":week_day,"leason_id":leason_id,"customers_in_leason":customers_in_leason,"max_customers":max_customers,"leason_time":leason_time})
        iterweekday = iterweekday + 1

    #  leason_max_riders - customers_who_ride - rerides + cancellations = Available rebookable slots
    # Since all data is now gathered, lets look inside the leasons list and go through each leason
    # This is our list for the calender, output in json format
    json_leasons = []
    if len(leasons) > 0: 
        for leason in leasons:
            # Translate the literal swedish weekday to a numeric one 
            weekday = reverse_translate_weekday(leason["weekday"])
            today=date(year=datetime.now().year,month=datetime.now().month,day=datetime.now().day)
            # What is the first date for this weekday, counting from today?
            first_leasondate = get_firstdate_weekday(weekday, today)
            # Now we have our starting point, and will loop through it until we hit the stop_date 
            while first_leasondate <= stop_date:
                # Check to make sure it is not in black dates 
                if first_leasondate not in black_dates:
                    # Prepare an EPOCH for the date and time of the leason
                    leason_time_epoch = convert_dt_to_epoch(first_leasondate,leason["leason_time"])
                    # Now check to see if there are any cancelled leasons for this date and leason
                    cancelled_leasons = len(db((db.cancelled_leasons.cancelled_date == first_leasondate) & (db.cancelled_leasons.id_leason == leason["leason_id"])).select(db.cancelled_leasons.id))

                    # Then check to see if there are any rebooked leasons for this date and leason
                    rebooked_leasons = len(db((db.rebooking.leason_date == first_leasondate) & (db.rebooking.id_leason == leason["leason_id"])).select(db.rebooking.id))
                    # Then do
                    available_rebooking_slots = leason["max_customers"] - rebooked_leasons + cancelled_leasons 
                    # Append
                    if len(db((db.rebooking.id_leason == leason["leason_id"]) & (db.rebooking.id_customer == cust_id) & (db.rebooking.leason_date == first_leasondate)).select()) == 1:
                        json_leasons.append({
                        "title":"Bokad igenridning",
                        "url":"",
                        "type":"rebooking",
                        "date":str(leason_time_epoch),
                        "description":"Du är inbokad på en igenridning. Status:?"  
                        })
                    else:
                        json_leasons.append({
                        "title":"Boka en igenridning",
                        "url":URL('book_rebooking.html', args=[cust_id, leason["leason_id"], first_leasondate]),
                        "type":"rebooking",
                        "date":str(leason_time_epoch),
                        "description":""})
                #    
                #
                first_leasondate = first_leasondate + timedelta(days=7)
            # Now we add in all black dates, so they will display in the calendar. This is
            # regardless if the customer can ride, or rebook - all black days are displayed.
    for black_date in black_dates:
        json_leasons.append({
        "title":"Ridskolan Stängd",
        "url":"",
        "type":"blackdate",
        "date":str(convert_dt_to_epoch(black_date,dttime(12,0))),
        "description":"Ridskolan är stängd denna dag"
        })
    if len(json_leasons) < 1:
        json_leasons.append({"title":"empty","url":"empty","type":"empty","date":0,"description":"AAA"})

    json_leasons = json.dumps(json_leasons)
    return str(json_leasons)

def list_leasondates(customer):
    '''
    This function will be used by the customers calender, called via AJAX. Its purpose is to find the
    leasons a customer has, compile a list of dates for the active semester. Past dates from today will
    be looked for in the leason_history table, since they have happened. Future dates will be calculated
    via datetime functions and displayed with an option to cancel that leason. Leasons that have already
    been cancelled should be hightlighted as such, data for that is retrieved from table cancelled_leasons
    '''
    # Lets get the active semester(function in model)
    active_semester = retrieve_current_semester()

    # And retrieve a list of the black dates for that semester
    black_dates = get_black_dates(active_semester)

    # The cust_id is the first argument in calling this function
    # But this is really bad. Uberbad. Do not do this. Query the database for the currently
    # logged in users user_id variable directly instead.
    #cust_id = request.args(0)
    cust_id = customer

    # Get start and end dates for the active semester
    semester_info = db(db.semester.id==active_semester).select()[0]
    start_date = semester_info.start_date
    end_date = semester_info.end_date

    # We also need ot know todays date, in datetime.date format to stay consistent.
    today=date(year=datetime.now().year,month=datetime.now().month,day=datetime.now().day)

    # Here we will hold all leason data that will eventually be returned as json
    master_leasons = []

    # Get the customers leasons as stored in the one-to-many table leasons
    try:
        leasons = db(db.leasons.id_customer==cust_id).select()
        for leason in leasons:
            leason_id = leason["id_leason"]
            # We need to retrieve the data for this leason from the leason table
            leason_data = db(db.leason.id==leason["id_leason"]).select()[0]

            # We must translate the spelled out weekday, i.e. "Måndag" to a numeric value (0 for Monday, 
            # 6 for Sunday to follow the convention that the timetuple wday uses. This is really gay
            # but storing the weekdays as swedish in the table is pretty sweet, thanks to web2pys crud
            # feature.
            leason_weekday = reverse_translate_weekday(leason_data.week_day)

            # Call internal function to get the first available DATE for the leasons Weekday
            # counting from today
            leason_start_date = get_firstdate_weekday(leason_weekday, start_date)

            #This is a list for keeping the dates for this leason
            leason_dates = []

            #
            # We will use these lists to search through when we loop
            canx_leasons = get_cancelled_leasons(cust_id,leason_id)
            historical_leasons = get_leason_history(cust_id,leason_id)
            rebooked_leasons = get_rebooked_leasons(cust_id)

            # The Past, The Present and The Future

            # The Past 
            #The past consists of historical leasons and cancelled leasons(past). Beyond that, there is no past.
            while leason_start_date < today:
                if leason_start_date in historical_leasons:
                    leason_dates.append({
                    "description":"",
                    "title":"Du red kl. " + str(leason_data.leason_time), 
                    "url":"",
                    "type":"viewhistorical",
                    "date":str(convert_dt_to_epoch(leason_start_date,leason_data.leason_time))
                    })
                else:
                    if leason_start_date in canx_leasons:
                        leason_dates.append({
                        "description":"Din lektion är avbokad.",
                        "title":"Avbokad",
                        "url":URL('viewleasondetails',args=[leason_data.id,leason_start_date]),
                        "type":"viewhistorical",
                        "date":str(convert_dt_to_epoch(leason_start_date,leason_data.leason_time))
                        })
                # Adding another week to skipjump into the present(eventually)
                leason_start_date = leason_start_date + timedelta(days=7)

            # The Present
            if leason_start_date == today:
                # Do checks regarding today. I:E if there is a leason TODAY we must check the time. If it is 4 hours before leason
                # starts they can cancel it. If it is less then that, they are screwed.
                # function check_canx_time(leasonid) created ot check this, but it
                # is not tested all the way yet
                if check_canx_time(leason_data.id):
                    # We have clearance to add this to a cancellable leason
                    leason_dates.append({
                    "description":"",
                    "title":"Avboka denna lektion",
                    "url":URL('cancel_leason.html', args=[cust_id, leason["leason_id"], leason_start_date]),
                    "type":"viewfuture",
                    "date":str(convert_dt_to_epoch(leason_start_date,leason_data.leason_time))
                    })
                else: 
                    # We have no clearance to cancel this leason. Display a class
                    # indicating a leason must be cancelled within X hours before
                    # the start of the leason
                    leason_dates.append({
                    "title":"En lektion måste avbokas minst 4 timmar innan lektionen börjar.",
                    "description":"",
                    "url":"",
                    "type":"lastcall",
                    "date":str(convert_dt_to_epoch(leason_start_date,leason_data.leason_time))
                    })

                # Must add another week to the variable so the function can keep rolling towards da FuTuRe
                leason_start_date = leason_start_date + timedelta(days=7)

            # THe Future
            # La Futura consists of future "blank" dates, future rebookings and future cancelled leasons 
            if leason_start_date > today:
                # Loop until we are at the end of the semester.
                while leason_start_date <= end_date:
                    # We check to make sure it is not in black_dates 
                    if leason_start_date not in black_dates:
                        if leason_start_date in canx_leasons:
                            leason_dates.append({
                            "description":"",
                            "title":"Avbokad",
                            "url":"",
                            "type":"viewfuture",
                            "date":str(convert_dt_to_epoch(leason_start_date,leason_data.leason_time))})
                        else:
                            leason_dates.append({
                            "description":"",
                            "title":"Avboka denna lektion",
                            "url":URL('cancel_leason.html', args=[cust_id, leason_data.id, leason_start_date]),
                            "type":"viewfuture",
                            "date":str(convert_dt_to_epoch(leason_start_date,leason_data.leason_time))})

                    leason_start_date = leason_start_date + timedelta(days=7)

            # Now add the list to the master leason list
            master_leasons.append(leason_dates)
    except:
        errormessage = "Unable to select customer leasons!"

    # Add all black dates
    for black_date in black_dates:
        leason_dates.append({"title":"Ridskolan Stängd","url":"","type":"blackdate","date":str(convert_dt_to_epoch(black_date,dttime(12,0))),"description":"Ridskolan är stängd denna dag"})

    # Add all rebooked dates
    for rebooked_leason in rebooked_leasons: 
        # Get the time of the leason that was rebooked...
        rb_ltime = db.leason[rebooked_leason["leason_id"]]["leason_time"]
        leason_dates.append({
        "title":"Igenridning",
        "url":"",
        "type":"rebooking",
        "date":str(convert_dt_to_epoch(rebooked_leason["leason_date"],rb_ltime)),"description":"Du har bokat en igenridning"})



    # Now we have one list for each leason in the master_leasons. We must pop this out and make 
    # one list to rule them all. 
    newmaster = []
    no_of_lists = len(master_leasons)
    startnum = 0
    while startnum < no_of_lists: 
        for entry in master_leasons[startnum]:
            newmaster.append(entry)
        startnum = startnum + 1

    if len(newmaster) < 1:
        newmaster.append({"description":"ASSA","title":"empty","url":"empty","type":"empty","date":"1381766400000"})

    #json_newmaster = json.dumps({"success":1,"result":newmaster},sort_keys=True,indent=4, separators=(',', ': '))
    #return json_newmaster
    newmaster = json.dumps(newmaster)
    return str(newmaster)


def book_rebooking():
    # The function to book a rebooking. This URL is created in the list_rebookings function. The user id is for now 
    # passed here as a request.args but should obviously be migrated into the greater auth scheme
    cust_id = request.args(0)
    leason_id = request.args(1)
    leason_date = request.args(2)

    helper = "När du har bokat en igenridning så är din kredit förbrukad. En bokad igenridning går inte att boka om, eller avbokas."
    
    form = FORM.confirm("Jag förstår, boka min igenridning!")
    if form.accepted:
        if db.rebooking.validate_and_insert(id_leason=leason_id, id_customer=cust_id, leason_date=leason_date):
            session.flash=("Igenridningen är bokad!")
            redirect(URL('index.html'))
    return dict(form=form, helper=helper)

def cancel_leason():
    # The function to cancel a leason. This URL is created in list_leasondates function. The user id is for now passed here as a request.args but should obviously be migrated into the greater auth scheme
    cust_id = request.args(0)
    leason_id = request.args(1)
    leason_date = request.args(2)

    helper = "När du har avbokat en lektion så får du en igenridnings kredit. Den kan du använda för att rida igen din lektion som du nu avbokar. Tänk på att en avbokad lektion inte går att ångra."
    form = FORM.confirm("Jag förstår reglerna, avboka min lektion.")
    if form.accepted:
        if db.cancelled_leasons.validate_and_insert(id_leason=leason_id, cancelled_date=leason_date, id_customer=cust_id, when_cancelled=datetime.now()):
            session.flash=("Lektionen är avbokad!")
            redirect(URL('index.html'))
    return dict(form=form, helper=helper)

    

