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
    html_res = ""
    for day in dayz:
        leasons_for_this_day = []
        for leason in leasons:
            if len(db((db.leason.id==leason.leason_id)&(db.leason.week_day==day)).select()) > 0:
                leasons_for_this_day.append(leason.leason_id)

        if len(leasons_for_this_day) > 0:
            html_res += """
    <div class="dg" data-toggle="collapse" data-target="#%s" aria-expanded="true" aria-controls="%s">
        <h4>%s</h4> 
    </div>
    <div id="%s" class="collapse">\n""" % (day, day, day, day)
            for leason in leasons_for_this_day: 
                # Find first available date for this weekday
                startdate = get_firstdate_weekday(reverse_translate_weekday(db.leason[leason].week_day), today)

                a = Viewleason(leason)
                startpoint = 0 

                while num_of_date_rows > startpoint: 
                    a.build_divs(startdate)
                    startpoint = startpoint + 1
                    startdate = startdate + timedelta(+7)

                a.end_div()
                # add to html variable
                html_res += a.divz
            # finish the div
            html_res += "</div>"
    


    return dict(html_res=XML(html_res)) 

def change_num_of_date_rows(): 
    session.num_of_date_rows = request.args(0) 
    # refresh view
    redirect(URL('index'),client_side=True)

    


class Viewleason:
    'Common class to prepare the view for a leason'
    def __init__(self, leason_id):
        self.leason_id = leason_id
        self.time = str(db(db.leason.id == leason_id).select(db.leason.leason_time)[0]['leason_time'])[:5]
        # start to construct the div
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
        riders = []

        for reg_rider in reg_riders:
            if reg_rider in canx_riders:
                reg_rider["type"] = "danger"
                riders.append(reg_rider)
            else:
                reg_rider["type"] = "success"
                riders.append(reg_rider)

        for rebook_rider in rebook_riders:
            rebook_rider["type"] = "info"
            riders.append(rebook_rider)

        # Finish the row with empty slots
        if available_slots > 0:
            av_div = "          <a href='#' class='list-group-item list-group-item-active'>Ledig plats</a>\n"
            self.divz +=  av_div * available_slots

        # finish this column
        self.divz += """
                        </li>
                    </div>
                </div>"""
