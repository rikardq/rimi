# coding: utf8
from isoweek import Week


instructor_id = 1
leasons = db(db.owner_of_leason.instructor_id==instructor_id).select(db.owner_of_leason.leason_id)
today=date.today()

### DISPLAY VARIABLES
num_of_date_rows = 4 # 


"""
What should be here?
What can an instructor do?

- Can make announcements to its groups via Infoboard system
- Can cancel individual dates on one of their leasons
- See the leasons that they are responsible for, default today
- Administrate horse-selections to its leasons/riders
"""

def index():
    a = Viewleason(1)
    maindiv = "" 
    startpoint = 0 
    startdate = date(2014,11,3)

    while num_of_date_rows > startpoint: 
        a.build_divs(startdate)
        startpoint = startpoint + 1
        startdate = startdate + timedelta(+7)

    a.end_div()

    return dict(divz=XML(a.divz)) 



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

        self.divz += """
                <div class="col-md-3">
                    <div class="list-group">
                        <li class="list-group-item list-group-item-warning">%s</li>\n""" % self.leason_date

        for reg_rider in reg_riders:
            if reg_rider in canx_riders:
                divclass = "danger"
            else:
                divclass = "success"
            self.divz += "             <a href='#' class='list-group-item list-group-item-%s'>%s %s</a>\n" % (divclass, reg_rider['first_name'], reg_rider['last_name'])

        # Finish the row with empty slots
        if available_slots > 0:
            av_div = "          <a href='#' class='list-group-item list-group-item-active'>Ledig plats</a>\n"
            self.divz +=  av_div * available_slots

        # finish this column
        self.divz += """
                        </li>
                    </div>
                </div>"""
