# -*- coding: utf-8 -*-

# Used to sort lists
from operator import itemgetter

##### GLOBAL VARIABLES START 
#
# Lets get the active semester(function in model)
active_semester = retrieve_current_semester()[0]

# And retrieve a list of the black dates 
black_dates = get_black_dates()

# Get start and end dates for the active semester
semester_info = db(db.semester.id==active_semester).select()[0]
start_date = semester_info.start_date
end_date = semester_info.end_date
today=date.today()

# If this value is not set in the admin_settings table, use default below
max_rebook_days = 31
#


### MESSAGE VARIABLES

leason_title = "Avboka Din lektion"
rebooked_title = "Inbokad igenridning"
canx_by_instructor = "Inställd av instruktören"
canx_by_rider = "Inställd av ryttaren"
too_late_to_canx = "För sent att avboka din lektion"



##### END

def view(): 

  #return dict(leasons=list_leasondates(1),displaylist=displaylist,datelist=datelist,message=datelist)
  return dict(leasons=list_leasondates(1), rebookings=list_rebookings(1))

def rebook():
  return dict(rebookings=list_rebookings(1))


def list_leasondates(customer):
    '''
    '''
    cust_id = customer

    # Collect all leasons in this 
    master_leasons = []

    # Get the customers leasons as stored in the one-to-many table leasons
    try:
        leasons = db(db.leasons.id_customer==cust_id).select()
        for leason in leasons:
            leason_id = leason["id_leason"]
            # We need to retrieve the data for this leason from the leason table
            leason_data = db(db.leason.id==leason_id).select()[0]

            # We must translate the spelled out weekday, i.e. "Måndag" to a numeric value (0 for Monday, 
            # 6 for Sunday to follow the convention that the timetuple wday uses. This is really gay
            # but storing the weekdays as swedish in the table is pretty sweet, thanks to web2pys crud
            # feature.
            leason_weekday = reverse_translate_weekday(leason_data.week_day)

            # Is leason limited by stop/start dates?
            try:
                a=db((db.leason.id==leason_id)&(db.leason.limited=="Ja")).select(db.leason.start_date,db.leason.end_date)[0]
                leason_start_date = a.start_date
                end_date = a.end_date
            except:
                # it is not, get start_date from int function that figures out next avialable start_date from today, based on weekday of leason
                leason_start_date = get_firstdate_weekday(leason_weekday, start_date)
                end_date = semester_info.end_date

            leason_dates = []

            # We will use these lists to search through when we loop
            canx_leasons = get_cancelled_leasons(cust_id,leason_id)

            while leason_start_date < today:
            	leason_start_date = leason_start_date + timedelta(days=7)

            # The Present
            if leason_start_date == today:
                horse_name = get_horse_info(leason_data.id,leason_start_date,cust_id)

                # Test if the leason has been cancelled by admin
                if canxbyadmin(leason_start_date,leason_id):
                    title = canx_by_instructor 
                else:
                    # Check if todays leason is too late to cancel
                    if check_canx_time(leason_data.id):
                        title = leason_title 
                    else: 
                        title = too_late_to_canx
                leason_dates.append({
                "title":title,
                "horse":horse_name,
                "time":leason_data.leason_time,
                "weekday":leason_data.week_day,
                "date":leason_start_date
                })

                # Must add another week to the variable so the function can keep rolling towards da FuTuRe
                leason_start_date = leason_start_date + timedelta(days=7)

            # THe Future
            # La Futura consists of future "blank" dates, future rebookings and future cancelled leasons 
            # and of leasons cancelled by admin/instrucotr
            if leason_start_date > today:
                # Loop until we are at the end of the semester.
                while leason_start_date <= end_date:
                    horse_name = get_horse_info(leason_data.id,leason_start_date,cust_id)
                    if leason_start_date in canx_leasons:
                        title = canx_by_rider 
                    elif canxbyadmin(leason_start_date,leason_data.id):
                        title = canx_by_instructor
                    else:
                        # If we are here, its a regular leason 
                        title = leason_title
                        leason_dates.append({
                        "title":title,
                        "horse":horse_name,
                        "time":leason_data.leason_time,
                        "weekday":leason_data.week_day,
                        "date":leason_start_date
                        })

                    leason_start_date = leason_start_date + timedelta(days=7)

            # Now add the list to the master leason list
            master_leasons.append(leason_dates)
    except:
        errormessage = "Unable to select customer leasons!"

    # Now we have one list for each leason in the master_leasons. We must pop this out and make 
    # one list to rule them all. 
    newmaster = []
    no_of_lists = len(master_leasons)
    s = 0
    while s < no_of_lists: 
        for entry in master_leasons[s]:
            newmaster.append(entry)
        s = s + 1

    # Add all rebooked dates (only pressent and future ones)
    rebooked_leasons = get_rebooked_leasons(cust_id)
    for rebooked_leason in rebooked_leasons: 
        if rebooked_leason["leason_date"] >= today:
            rb_ltime = db.leason[rebooked_leason["leason_id"]]["leason_time"]
            horse_name = get_horse_info(rebooked_leason["leason_id"], rebooked_leason["leason_date"], cust_id)
        
            newmaster.append({
              "title":rebooked_title,
              "horse":horse_name,
              "time":leason_data.leason_time,
              "weekday":translate_weekday(rebooked_leason["leason_date"].weekday()) ,
              "date":rebooked_leason["leason_date"]
               })


    ########## LEFT TO DO
    #  # # Sort out any black dates out of the list

    # Try to sort this mess by date
    finalmaster= sorted(newmaster, key=itemgetter('date')) 

    return (finalmaster)

def list_rebookings(customer):
    # But this is really bad. Uberbad. Do not do this. Query the database for the currently
    # logged in users user_id variable directly instead.
    cust_id = customer 
    #Aquire customers skill level
    # At the same time, generate a list of the customers leasons ID. this will be used later to 
    # exclude the customers own leasons, since they are not available for rebookings.
    customer_leasons = []
    # Create a default variable skill_level
    skill_level = 0

    # See if the customer has any leasons assigned
    res = db(db.leasons.id_customer==cust_id).select(db.leasons.id_leason)
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

    # Attempt to get the max_rebook_days variable from the admin_settings table. IF it is not set, use the default of 31
    # (that is defined in the global at the top)
    try:
        q = db(db.admin_settings.variable_name=="max_rebook_days").select()[0]
        max_rebook_days = int(q.variable_value)
    except:
        max_rebook_days = max_rebook_days 

    # Now we can create the stop_date
    stop_date = today + timedelta(days=max_rebook_days)


    #Loop through the weekdays, lookin in the tables for suitable leasons that could perhaps offer some
    # rerides.
    iterweekday = 0 # This represents monday, for our loop.
    leasons = []
    while iterweekday < 7:
        # Translate the weekday FROM num TO swedish for db query
        weekday = translate_weekday(iterweekday)

        # Get a lists of leasons for todays weekday, based on the customers skill_level
        q = (db.leason.week_day==weekday)&(db.leason.skill_level==db.skill_level.id)&(db.skill_level.skill_point <= skill_level)
        rows = db(q).select(db.leason.max_customers,db.leason.id,db.leason.leason_time,db.leason.week_day,db.leason.leason_time)

        for row in rows:
            max_customers = row.max_customers 
            leason_id = row.id
            leason_time = row.leason_time 
            week_day = row.week_day 
            leason_time = row.leason_time 

            # if statement to make sure we do not select leasons the customer already rides regurarly in
            if leason_id not in customer_leasons:
                try:
                    customers_in_leason = len(db(db.leasons.id_leason==leason_id).select())
                except:
                    customers_in_leason = 0
                leasons.append({"weekday":weekday,"week_day":week_day,"leason_id":leason_id,"customers_in_leason":customers_in_leason,"max_customers":max_customers,"leason_time":leason_time})
        iterweekday = iterweekday + 1

    # leason_max_riders - customers_who_ride - rerides + cancellations = Available rebookable slots
    # Since all data is now gathered, lets look inside the leasons list and go through each leason
    # and generate a new list with available reride opportunities
    reride_slots = []
    for leason in leasons:
        # Translate the literal swedish weekday to a numeric one 
        weekday = reverse_translate_weekday(leason["weekday"])
        # What is the first date for this weekday, counting from today?
        first_leasondate = get_firstdate_weekday(weekday, today)
        # Now we have our starting point, and will loop through it until we hit the stop_date 
        # FOR each date available for this leason, check each leason for canx, rerides etc to get the FUUUUCK
        while first_leasondate <= stop_date:
            if first_leasondate not in black_dates:
                # Now check to see if there are any cancelled leasons for this date and leason
                cancelled_leasons = len(db((db.cancelled_leasons.cancelled_date == first_leasondate) & (db.cancelled_leasons.id_leason == leason["leason_id"])).select(db.cancelled_leasons.id))

                # Then check to see if there are any rebooked leasons for this date and leason
                rebooked_leasons = len(db((db.rebooking.leason_date == first_leasondate) & (db.rebooking.id_leason == leason["leason_id"])).select(db.rebooking.id))
                # Then do the math for the available slots
                available_rebooking_slots = leason["max_customers"] - rebooked_leasons + cancelled_leasons 
                # NO add if the leason/date combo has been canx by admin
                if not canxbyadmin(first_leasondate,leason["leason_id" ]):
                    # NO add if the customer is already booked for a reride on leason/date combo 
                    if len(db((db.rebooking.id_leason == leason["leason_id"]) & (db.rebooking.id_customer == cust_id) & (db.rebooking.leason_date == first_leasondate)).select()) != 1:
                        reride_slots.append({
                            "date":first_leasondate,
                            "weekday":leason["weekday"],
                            "time":leason["leason_time"],
                            })
            first_leasondate = first_leasondate + timedelta(days=7)

    final_rerides = sorted(reride_slots, key=itemgetter('date')) 
    return (final_rerides)


