# coding: utf8
from isoweek import Week


instructor_id = 1
leasons = db(db.owner_of_leason.instructor_id==instructor_id).select(db.owner_of_leason.leason_id)
today=date.today()
today_wd = today.weekday()

dayz = ["Måndag","Tisdag","Onsdag","Torsdag","Fredag","Lördag","Söndag"]

### DISPLAY VARIABLES
if session.num_of_date_rows is None:
    num_of_date_rows = 4 #default is 4.  1, 2, 3, 4 or 6 
else:
    num_of_date_rows = int(session.num_of_date_rows)


"""
What should be here?
What can an instructor do?

- Can make announcements to its groups via Infoboard system
- Can cancel individual dates on one of their leasons
- See the leasons that they are responsible for, default today
- Administrate horse-selections to its leasons/riders
"""

def index():
    ### The variable startday determines which day to base the view dates from. Default is today
    if session.startday is None:
        session.startday = today
    # Set variable from session
    startday = session.startday 

    week_display()

    # Start the Tab list
    tablist = """<ul class="nav nav-tabs" role="tablist">"""
    # Start the Tab panes
    tabpanes = """<div class="tab-content">"""
    for day in dayz:
        leasons_for_this_day = []
        for leason in leasons:
            if len(db((db.leason.id==leason.leason_id)&(db.leason.week_day==day)).select()) > 0:
                leasons_for_this_day.append(leason.leason_id)

        if len(leasons_for_this_day) > 0:
            tablist += """
            <li role="presentation"><a href="#%s" aria-controls="%s" role="tab" data-toggle="tab">%s</a></li> 
            \n""" % (day, day, day)
            # add display tab for this day
            tabpanes += """<div role="tabpanel" class="tab-pane" id="%s">""" % (day)

            for leason in leasons_for_this_day: 
                # Find first available date for this weekday
                startdate = get_firstdate_weekday(reverse_translate_weekday(db.leason[leason].week_day), startday)

                a = Viewleason(leason)
                startpoint = 0 

                while num_of_date_rows > startpoint: 
                    # Build a column for this particular weekday, leason and finally actual date
                    a.build_divs(startdate)
                    startpoint = startpoint + 1
                    startdate = startdate + timedelta(+7)

                a.end_div()
                # add to Tab pane 
                tabpanes += a.divz
            # End display tab for this day 
            tabpanes += "</div>"

    # Finish the Tab pane
    tabpanes += "</div>"

    # Finish the tablist
    tablist += "</ul>"


    return dict(startday=startday,tablist=XML(tablist),tabpanes=XML(tabpanes)) 

def change_num_of_date_rows(): 
    # Function to change how many columns or date rows should be displayed. 
    session.num_of_date_rows = request.args(0) 
    # refresh view
    redirect(URL('index'),client_side=True)

def set_master_startdate():
    # Function to skip x weeks forward. We do this by setting the variable startday
    session.startday = session.startday + timedelta(+int(request.args(0))) 
    #session.startday = date(1999,11,1)
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
        back = {"week":Week.last_week_of_year(backyear)[1],"year":year - 1}
    else:
        back = {"week":week - 1,"year":year}

    # Our startdate will be current week, beginning with monday
    # set remaining sessions to new values and move on
    session.startdate = Week(year, week).monday()
    session.back = back
    session.forward = forward
    session.week = week
    session.year = year 


class Viewleason:
    'Common class to prepare the view for a leason'
    def __init__(self, leason_id):
        self.leason_id = leason_id
        self.time = str(db(db.leason.id == leason_id).select(db.leason.leason_time)[0]['leason_time'])[:5]
        # start to construct the div, first heading is the time
        # 
        self.divz = """
        <div class="dg" data-toggle="collapse" data-target="#%s" aria-expanded="true" aria-controls="%s">
            <h4>%s</h4>
        </div>

        <div id="%s" class="collapse">
            <div class="row">\n""" % (self.leason_id, self.leason_id, self.time, self.leason_id)

    def end_div(self):
        self.divz += """
            </div>
        </div>"""

    def build_divs(self, leason_date):
        self.leason_date = leason_date
        num_riders,num_rebooks,num_canx,num_total,reg_riders,canx_riders,rebook_riders,leason_time = leason_info(self.leason_date,self.leason_id)
        max_customers = int(db(db.leason.id==self.leason_id).select()[0]['max_customers'])
        available_slots = max_customers - num_riders - num_rebooks + num_canx 
        col_division = 12/num_of_date_rows 

        self.divz += """
                <div class="col-md-%s">
                    <div class="list-group">
                        <li class="list-group-item list-group-item-warning">%s</li>\n""" % (col_division, self.leason_date)
        for reg_rider in reg_riders:
            if reg_rider in canx_riders:
                divclass = "danger"
            else:
                divclass = "success"

            self.divz += " <a href='#' class='list-group-item list-group-item-%s'>%s %s</a>\n" % (divclass, reg_rider['first_name'], reg_rider['last_name'])

        for rebook_rider in rebook_riders:
            divclass="info"
            self.divz += " <a href='#' class='list-group-item list-group-item-%s'>%s %s</a>\n" % (divclass, rebook_rider['first_name'], rebook_rider['last_name'])

        # Finish the row with empty slots
        if available_slots > 0:
            av_div = "          <a href='#' class='list-group-item list-group-item-active'>Ledig plats</a>\n"
            self.divz +=  av_div * available_slots

        # finish this column
        self.divz += """
                        </li>
                    </div>
                </div>"""
