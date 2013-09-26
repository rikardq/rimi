# coding: utf8
#
# This is the controller for kund, or customer view. All administration that a end-customer can do with their leasons should reside here.
#
#
@auth.requires_login()
def index():
    message = "There is nothing here.... ALBATROSS!"
    return dict(message=message)

"""
The events is where the calendar widget retrives its events from.
We should override the call so we can send a customer id etc.
"""
@auth.requires_login()
def events():
  # Example on how the calenadar expects its JSON api. Note the "class" attribute we should change it to something like guiclass..
    return {"success":"1", "result":[{"id":123, "title":"Hopping", "class":"event-important","url":"http://dn.se", "start":1379264400000, "end":1379304060000}]}

def list_rebookings():
    # Watching execution time to try to catch resource hogs as I add them
    timez = []
    timez.append(time.time())
    ''' Define Function Here
    '''
    # The cust_id is the first argument in calling this function
    cust_id = request.args(0)

    #Aquire customers skill level
    # At the same time, generate a list of the customers leasons ID. this will be used later to 
    # exclude the customers own leasons, since they are not available for rebookings.
    customer_leasons = [] 
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
                else:
                    #Something did not work, set skill level to 0
                    skill_level = 0
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
    today=datetime.date(year=datetime.datetime.now().year,month=datetime.datetime.now().month,day=datetime.datetime.now().day)

    # Attempt to get the max_rebook_days variable from the admin_settings table. IF it is not set, use the default of 31
    try:
        q = db(db.admin_settings.variable_name=="max_rebook_days").select()[0]
        max_rebook_days = int(q.variable_value)
    except:
        max_rebook_days = 31
    
    # Now we can create the stop_date
    stop_date = today + datetime.timedelta(days=max_rebook_days)

	# Just for debugging
    timez.append(today)
    timez.append(stop_date)
    # Create the list for storing shit in
    shit_list = []
    shit_list.append(skill_level)
    
    #Loop through the weekdays, lookin in the tables for suitable leasons that could perhaps offer some
    # rerides.
    iterweekday = 0 # This represents monday, for our loop.
    leasons = []
    while iterweekday < 7:
        # Translate the weekday to swedish for db query
        weekday = translate_weekday(iterweekday)

        # Get a lists of leasons for todays weekday, based on the customers skill_level
        q = (db.leason.week_day==weekday)&(db.leason.skill_level==db.skill_level.id)&(db.skill_level.skill_point <= skill_level)
        rows = db(q).select(db.leason.id,db.leason.max_customers)
        if len(rows) > 0:
            for row in rows:
                max_customers = row["leason.max_customers"]
                leason_id = row["leason.id"]
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
                    leasons.append({"weekday":weekday,"leason_id":leason_id,"customers_in_leason":customers_in_leason,"max_customers":max_customers})
        iterweekday = iterweekday + 1

    #  leason_max_riders - customers_who_ride - rerides + cancellations = Available rebookable slots
    # Since all data is now gathered, lets look inside the leasons list and go through each leason
    # adding what we find to rebookable_dates
    rebookable_dates = []
    if len(leasons) > 0: 
        for leason in leasons:
            # Translate the literal swedish weekday to a numeric one 
            weekday = reverse_translate_weekday(leason["weekday"])
            today=datetime.date(year=datetime.datetime.now().year,month=datetime.datetime.now().month,day=datetime.datetime.now().day)
            # What is the first date for this weekday, counting from today?
            first_leasondate = get_firstdate_weekday(weekday, today)
            # Now we have our starting point, and while loop through it until we hit the stop_date 
            while first_leasondate <= stop_date:
                # Check to make sure it is not in black dates 
                if first_leasondate not in black_dates:
                    # Now check to see if there are any cancelled leasons for this date and leason
                    cancelled_leasons = len(db((db.cancelled_leasons.cancelled_date == first_leasondate) & (db.cancelled_leasons.id_leason == leason["leason_id"])).select(db.cancelled_leasons.id))

                    # Then check to see if there are any rebooked leasons for this date and leason
                    rebooked_leasons = len(db((db.rebooking.leason_date == first_leasondate) & (db.rebooking.id_leason == leason["leason_id"])).select(db.rebooking.id))
                    # Then do
                    available_rebooking_slots = leason["max_customers"] - rebooked_leasons + cancelled_leasons 
                    # Append
                    rebookable_dates.append({"Leason ID":leason["leason_id"],"Date":first_leasondate,"slots":available_rebooking_slots,"cancelled_leasons":cancelled_leasons,"rebooked_leasons":rebooked_leasons})
                #i#    
                #    
                #
                first_leasondate = first_leasondate + datetime.timedelta(days=7)
    else:
        #oekr
        arne = 1 + 2





    # End the function by returning data
    timez.append(time.time())
    return dict(message=shit_list,blackdates=black_dates,leasons=leasons,timez=timez,rebookable_dates=rebookable_dates,customer_leasons=customer_leasons)
        
def list_leasondates():
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
    cust_id = request.args(0)

    # Get start and end dates for the active semester
    semester_info = db(db.semester.id==active_semester).select()[0]
    start_date = semester_info.start_date
    end_date = semester_info.end_date

    # We also need ot know todays date, in datetime.date format to stay consistent.
    today=datetime.date(year=datetime.datetime.now().year,month=datetime.datetime.now().month,day=datetime.datetime.now().day)

    # Here we will hold the leason data
    master_leason = []

    # Get the customers leason, and retrieve the weekday
    try:
        leasons = db(db.leasons.id_customer==cust_id).select()
        for leason in leasons:
            leason_id = leason["id_leason"]
            # We need to retrieve the data from the leason table
            leason_data = db(db.leason.id==leason["id_leason"]).select()[0]

            # We must translate the spelled out weekday, i.e. "Måndag" to a numeric value (0 for Monday, 
            # 6 for Sunday to follow the convention that the timetuple wday uses. This is really gay
            # but storing the weekdays as swedish in the table is pretty sweet, thanks to web2pys crud
            # feature.
            leason_weekday = reverse_translate_weekday(leason_data.week_day)

            # Call internal function to get the first available DATE for the leasons Weekday
            leason_start_date = get_firstdate_weekday(leason_weekday, start_date)
            
            #leason_start_date = start_date + datetime.timedelta(days=days_to_add)

            #This is a list for keeping the dates for this leason
            leason_dates = []
            # Just for show
            leason_dates.append(leason_data.week_day)

            # Lets retrieve a list of cancelled leasons,
            #and one of leasons in history pertaining to this leason and customer.
            # We will use these lists to search through when we loop, so we do not hit the database a trillion times.
            canx_leasons = get_cancelled_leasons(cust_id,leason_id)
            historical_leasons = get_leason_history(cust_id,leason_id)

            # The Past, The Present and The Future

            # The Past 
            #The past consists of historical leasons and cancelled leasons(past). Beyond that, there is no past.
            while leason_start_date < today:
                if leason_start_date in historical_leasons:
                    leason_dates.append("The date below comes from the history table")
                    leason_dates.append(leason_start_date)
                else:
                    if leason_start_date in canx_leasons:
                        leason_dates.append("This one is a cancelled leason")
                        leason_dates.append(leason_start_date)
                # Adding another week to skipjump into the present(eventually)
                leason_start_date = leason_start_date + datetime.timedelta(days=7)

            # The Present
            if leason_start_date == today:
                # Do checks regarding today. I:E if there is a leason TODAY we must check the time. If it is 4 hours before leason
                # starts they can cancel it. If it is less then that, they are screwed.
                leason_dates.append("TODAY Is NOW")
                # Must add another week to the variable so the function can keep rolling with the FuTuRe
                leason_start_date = leason_start_date + datetime.timedelta(days=7)

            # THe Future
            # La Futura consists of future "blank" dates, and checkign to see if any are listed as black dates.
            if leason_start_date > today:
                leason_dates.append("The ones below are future dates")
                # Loop until we are at the end of the semester.
                while leason_start_date <= end_date:
                    #Check to see if it is ablack date
                    if leason_start_date in black_dates:
                        leason_dates.append("THIS MOTHER IS IN THE BLACK DATES SON AAW DAWG!")
                        leason_dates.append(leason_start_date)
                        leason_start_date = leason_start_date + datetime.timedelta(days=7)
                    else:
                        leason_dates.append(leason_start_date)
                        leason_start_date = leason_start_date + datetime.timedelta(days=7)

            # Now add the list to the master leason list
            master_leason.append(leason_dates)
    except:
        errormessage = "Unable to select customer leasons!"

    return dict(message=master_leason)
