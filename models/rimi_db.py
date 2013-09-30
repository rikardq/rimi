# -*- coding: utf-8 -*-

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)


# This table contains various variables tied to the administrator interface.
# For example, the active semester, number of days a customer should be able to see rebooking leasons.


db.define_table("admin_settings",
    SQLField("variable_name", "string", notnull=True),
    SQLField("variable_value","string"),
    SQLField("description","string"))



# Correlates to a customers level of riding experience and/or type. 
# A customer is tied to a skill level by the leasons that they are in. 
# A leason is tied to a skill level directly. The skill_point works so 
# that if a customer is tied to a skill_level with a skill_point of 4, 
# they can get rebooked into any leasons with skill_point =< 4
# At skill_point of 0 for a leason, any customer can book it.

db.define_table("skill_level",
      SQLField("skill_name", "string", notnull=True, default=None),
      SQLField("skill_point", "integer", requires=IS_IN_SET(range(1,50))),
      SQLField("skill_type", "string", requires=IS_IN_SET(["Ponny","Häst","Blandad"])))

# The customer table. This will be replaced eventually with the builtin auth
# table web2py uses.

db.define_table("customer",
      SQLField("name", "string", notnull=True, default=None),
      SQLField("status", "string", requires=IS_IN_SET(['Active','Inactive']), default='Active'))


#Here we define semesters
db.define_table("semester",
      SQLField("name", "string", notnull=True, default=None),
      SQLField("start_date", "date", notnull=True, default=None),
      SQLField("end_date", "date", notnull=True, default=None))


#A leason is created in this table. It is tied to a skill level.
db.define_table("leason",
      SQLField("week_day", requires=IS_IN_SET(['Måndag','Tisdag','Onsdag','Torsdag','Fredag','Lördag','Söndag'])),
      SQLField("leason_time", "time", notnull=True, default=None),
      SQLField("leason_length", "integer", notnull=True, default=None),
      SQLField("max_customers", "integer", notnull=True, default=None),
      SQLField("skill_level", db.skill_level),
      SQLField("status", "string", requires=IS_IN_SET(['Active','Inactive']), default='Active'),
      SQLField("leason_type", "string", requires=IS_IN_SET(['Ponny','Häst','Blandad'])))


#The table that ties one customer to its leasons(one to many)
db.define_table("leasons",
      SQLField("id_customer", db.customer),
      SQLField("id_leason", db.leason))



# The history table which contains all historical leasons and their
# attributes(since attributes of a leason are allowed to change
# in the future, we keep the historical data here
db.define_table("leasons_history",
      SQLField("id_customer", "integer", notnull=True, default=None),
      SQLField("id_leason", "integer", notnull=True, default=None),
      SQLField("id_semester", "integer", notnull=True, default=None),
      SQLField("id_horse", "integer",  default=None),
      SQLField("id_rebooking", "integer", default=None),
      SQLField("leason_time", "time", notnull=True, default=None),
      SQLField("leason_length", "time", notnull=True, default=None),
      SQLField("skill_level", db.skill_level),
      SQLField("leason_type", "string", default=None),
      SQLField("leason_date", "date", notnull=True, default=None))



"""
Keeps track of any leasons that has been cancelled by the user or
an instructor. Uncertain if db.leason.id should be contained here.
"""
db.define_table("cancelled_leasons",
      SQLField("id_customer", db.customer),
      SQLField("id_leason", db.leason),
      SQLField("cancelled_date", "date", notnull=True, default=None),
      SQLField("when_cancelled", "datetime", notnull=True, default=None))


"""
Keeps track of requested, denied and confirmed rebookings.
"""
db.define_table("rebooking",
      SQLField("id_leason", db.leason),
      SQLField("id_customer", db.customer),
      SQLField("leason_date", "date", notnull=True, default=None),
      SQLField("approval", requires=IS_IN_SET(['notyet','yes','no']), default='notyet'),
      SQLField("deny_message", "string"))


"""
Storing all horses associated with the business and their status.
"""
db.define_table("horse",
      SQLField("name", "string", notnull=True, default=None),
      SQLField("status", "string", requires=IS_IN_SET(['Active','Inactive']), default='Active'),
      SQLField("horse_type", "string", requires=IS_IN_SET(['Ponny','Häst']), default=None))

"""
We store any pre-selected horses in this table for display at appropriate
views
"""
db.define_table("reserved_horses",
      SQLField("id_customer", db.customer),
      SQLField("id_horse", db.horse),
      SQLField("id_leason", db.leason),
      SQLField("reserved_date", "date", notnull=True, default=None))



"""
A black date is when the riding school is closed
"""
db.define_table("black_dates",
      SQLField("id_semester", db.semester),
      SQLField("black_date", "date", notnull=True, default=None))

      
      
db.leasons.id_customer.requires=IS_IN_DB(db, 'customer.id')
db.leasons.id_leason.requires=IS_IN_DB(db, 'leason.id')
db.reserved_horses.id_customer.requires=IS_IN_DB(db, 'customer.id')
db.reserved_horses.id_horse.requires=IS_IN_DB(db, 'horse.id')
db.reserved_horses.id_leason.requires=IS_IN_DB(db, 'leason.id')
db.black_dates.id_semester.requires=IS_IN_DB(db, 'semester.id')
db.cancelled_leasons.id_customer.requires=IS_IN_DB(db, 'customer.id')
db.cancelled_leasons.id_leason.requires=IS_IN_DB(db, 'leason.id')
db.rebooking.id_leason.requires=IS_IN_DB(db, 'leason.id')
db.rebooking.id_customer.requires=IS_IN_DB(db, 'customer.id')
db.leason.skill_level.requires=IS_IN_DB(db, 'skill_level.id')
