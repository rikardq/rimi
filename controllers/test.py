# -*- coding: utf-8 -*-
# try something like
def index(): 
  from datetime import time
  from datetime import timedelta

  datelist = []
  displaylist = []
  dayz = ['Mån','Tis','Ons','Tors','Fre','Lör','Sön']

  end_date = date(2014,12,24)
  today = date.today()
  while today < end_date:
    datelist.append(today)
    displaylist.append({'Weekday': dayz[today.weekday()] + 'dag', 'Date': str(today)})
    today = today + timedelta(days=2)



  return dict(leasons=list_leasondates(1),displaylist=displaylist,datelist=datelist,message=datelist)


def list_leasondates(customer):
    '''
    '''
    # Lets get the active semester(function in model)
    active_semester = retrieve_current_semester()[0]

    # And retrieve a list of the black dates 
    black_dates = get_black_dates()

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
    #today=date(year=datetime.now().year,month=datetime.now().month,day=datetime.now().day)
    today=date.today()

    # Here we will hold all leason data that will eventually be returned as json
    master_leasons = []

    # Get the customers leasons as stored in the one-to-many table leasons
    try:
        errormessage = ""
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

            # IF it is time limited, then set start and end date from values in db, else
            # Call internal function to get the first available DATE for the leasons Weekday
            # counting from today
            try:
                a=db((db.leason.id==leason_id)&(db.leason.limited=="Ja")).select(db.leason.start_date,db.leason.end_date)[0]
                leason_start_date = a.start_date
                end_date = a.end_date
            except:
                leason_start_date = get_firstdate_weekday(leason_weekday, start_date)
                end_date = semester_info.end_date

            #This is a list for keeping the dates for this leason
            leason_dates = []

            #
            # We will use these lists to search through when we loop
            canx_leasons = get_cancelled_leasons(cust_id,leason_id)
            historical_leasons = get_leason_history(cust_id,leason_id)
            rebooked_leasons = get_rebooked_leasons(cust_id)

            # The Past, The Present and The Future
            # NO FUCKING PAST, useless. trim the fat.
	    # fast forward towards the present and the future
            while leason_start_date < today:
            	leason_start_date = leason_start_date + timedelta(days=7)


            # The Present
            if leason_start_date == today:
                # Get horse information for this leason if any 
                horse_name = get_horse_info(leason_data.id,leason_start_date,cust_id)

                # Test if the leason has been cancelled by admin
                if canxbyadmin(leason_start_date,leason_id):
                    leason_dates.append({
                        "title":"Inställd",
                        "horse":"",
                        "time":leason_data.leason_time,
                        "weekday":leason_data.week_day,
                        "date":leason_start_date
                        })
                else:
                    # Check if todays leason is too late to cancel
                    if check_canx_time(leason_data.id):
                        # We have clearance to add this to a cancellable leason
                        leason_dates.append({
                        "title":"Avboka",
                        "horse":horse_name,
                        "time":leason_data.leason_time,
                        "weekday":leason_data.week_day,
                        "date":leason_start_date
                        })
                    else: 
                        # We have no clearance to cancel this leason. Display a class
                        # indicating a leason must be cancelled within X hours before
                        # the start of the leason
                        leason_dates.append({
                        "title":"För sent att avboka",
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
                    # Get horse information for this leason if any 
                    horse_name = get_horse_info(leason_data.id,leason_start_date,cust_id)
                    # We check to make sure it is not in black_dates 
                    if leason_start_date not in black_dates:
                        # Check if its a cancelled leason
                        if leason_start_date in canx_leasons:
                            leason_dates.append({
                            "title":"Avbokad",
                            "horse":horse_name,
                            "time":leason_data.leason_time,
                            "weekday":leason_data.week_day,
                            "date":leason_start_date
                            })
                        # Check if its a leason cancelled by admin/instrucotr
                        elif canxbyadmin(leason_start_date,leason_data.id):
                            leason_dates.append({
                            "title":"Inställd",
                            "horse":horse_name,
                            "time":leason_data.leason_time,
                            "weekday":leason_data.week_day,
                            "date":leason_start_date
                            })
                        else:
                            # After all that checking its just a regular future leason that can be cancelled
                            leason_dates.append({
                            "title":"Avboka",
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
    startnum = 0
    while startnum < no_of_lists: 
        for entry in master_leasons[startnum]:
            newmaster.append(entry)
        startnum = startnum + 1

    # Add all black dates (only present and future ones)
    for black_date in black_dates:
        if black_date >= today:  
            newmaster.append({
            "title":"Inställd",
            "horse":"",
            "time":"",
            "weekday":translate_weekday(black_date.weekday()) ,
            "date":black_date
            })

    # Add all rebooked dates (only pressent and future ones)
    for rebooked_leason in rebooked_leasons: 
        if rebooked_leason["leason_date"] >= today:
            # Get the time of the leason that was rebooked...
            rb_ltime = db.leason[rebooked_leason["leason_id"]]["leason_time"]
        
            newmaster.append({
              "title":"Igenridning",
              "horse":"",
              "time":leason_data.leason_time,
              "weekday":translate_weekday(rebooked_leason["leason_date"].weekday()) ,
              "date":rebooked_leason["leason_date"]
               })


    # If the newmaster is empty, add one entry so as to not break calendar
    if len(newmaster) < 1:
        newmaster.append({
        "title":"Igenridning",
        "horse":"",
        "time":"",
        "weekday":"",
        "date":rebooked_leason["leason_date"]
        })

    # Try to sort this mess by date
    from operator import itemgetter
    finalmaster= sorted(newmaster, key=itemgetter('date')) 

    return (finalmaster)
