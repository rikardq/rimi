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
      SQLField("skill_name", "string", label="Namn", notnull=True, default=None),
      SQLField("skill_point", "integer", requires=IS_IN_SET(range(1,50)), label="Poäng"),
      SQLField("skill_type", "string", requires=IS_IN_SET(["Ponny","Häst","Blandad"]), label="Typ"))

# The customer table. This will be replaced eventually with the builtin auth
# table web2py uses.

db.define_table("customer",
      SQLField("name", "string", label="Namn", notnull=True, default=None),
      SQLField("status", "string", requires=IS_IN_SET(['Active','Inactive']), default='Active'),
      format="%(name)s")


#Here we define semesters
db.define_table("semester",
      SQLField("name", "string", label="Termin", notnull=True, default=None),
      SQLField("start_date", "date", label="När börjar terminen?", notnull=True, default=None),
      SQLField("end_date", "date", label="När slutar terminen?", notnull=True, default=None),
      format="%(name)s")


#A leason is created in this table. It is tied to a skill level.
db.define_table("leason",
      SQLField("week_day", requires=IS_IN_SET(['Måndag','Tisdag','Onsdag','Torsdag','Fredag','Lördag','Söndag']), label="Veckodag" ),
      SQLField("leason_time", "time", label="Tid när lektionen börjar", notnull=True, default=None),
      SQLField("leason_length", "integer", label="Längd på lektion, i minuter", notnull=True, default=None),
      SQLField("max_customers", "integer", label="Max antal ryttare i gruppen", notnull=True, default=None),
      SQLField("skill_level", db.skill_level, label="Välj nivå på gruppen"),
      SQLField("status", "string", requires=IS_IN_SET(['Aktiv','Inaktiv']), default='Aktiv'),
      SQLField("leason_type", "string", label="Lektionstyp", requires=IS_IN_SET(['Ponny','Häst','Blandad'])))


#The table that ties one customer to its leasons(one to many)
db.define_table("leasons",
      SQLField("id_customer", db.customer),
      SQLField("id_leason", db.leason))



# The history table which contains all historical leasons and their
# attributes(since attributes of a leason are allowed to change
# in the future, we keep the historical data here
db.define_table("leasons_history",
      SQLField("id_customer", "integer", notnull=True),
      SQLField("id_leason", "integer", notnull=True),
      SQLField("id_semester", "integer", notnull=True),
      SQLField("id_horse", "integer",  default=None),
      SQLField("id_rebooking", "integer", default=None),
      SQLField("leason_time", "time", default=None),
      SQLField("leason_length", "integer", notnull=True),
      SQLField("skill_level", db.skill_level),
      SQLField("leason_type", "string", default=None),
      SQLField("leason_date", "date", notnull=True))



#Keeps track of any leasons that has been cancelled by the user or
#an instructor. Uncertain if db.leason.id should be contained here.
db.define_table("cancelled_leasons",
      SQLField("id_customer", db.customer),
      SQLField("id_leason", db.leason),
      SQLField("cancelled_date", "date", notnull=True, default=None),
      SQLField("when_cancelled", "datetime", notnull=True, default=None))


#Keeps track of requested, denied and confirmed rebookings.
db.define_table("rebooking",
      SQLField("id_leason", db.leason),
      SQLField("id_customer", db.customer),
      SQLField("leason_date", "date", notnull=True, default=None),
      SQLField("approval", requires=IS_IN_SET(['notyet','yes','no']), default='notyet'),
      SQLField("deny_message", "string"))


#Storing all horses associated with the business and their status.
db.define_table("horse",
      SQLField("name", "string", label="Namn", notnull=True, default=None),
      SQLField("status", "string", requires=IS_IN_SET(['Aktiv','Inaktiv']), default='Inaktiv'),
      SQLField("horse_type", "string", label="Typ av häst", requires=IS_IN_SET(['Ponny','Häst']), default=None))

#We store any pre-selected horses in this table for display at appropriate
#views
db.define_table("reserved_horses",
      SQLField("id_customer", db.customer),
      SQLField("id_horse", db.horse),
      SQLField("id_leason", db.leason),
      SQLField("reserved_date", "date", notnull=True, default=None))



#A black date is when the riding school is closed
db.define_table("black_dates",
      SQLField("id_semester", db.semester, label="Termin"),
      SQLField("black_date", "date", label="Datum", notnull=True, default=None))

# A table for storing our instructors in. This will most likely be migrated
# to auth_user at a later point
db.define_table("instructor",
      SQLField("name", "string", label="Namn", notnull=True))

# Define the one to many table for instructor(s) and leason
db.define_table("owner_of_leason",
      SQLField("leason_id", db.leason),
      SQLField("instructor_id", db.instructor))

db.owner_of_leason.instructor_id.requires=IS_IN_DB(db, "instructor.id", 'Instruktör: %(name)s')
db.leasons.id_customer.requires=IS_IN_DB(db, "customer.id", 'Namn: %(name)s')
db.leasons.id_leason.requires=IS_IN_DB(db, 'leason.id', '%(week_day)s %(leason_time)s')
db.reserved_horses.id_customer.requires=IS_IN_DB(db, 'customer.id', '%(name)s')
db.reserved_horses.id_horse.requires=IS_IN_DB(db, 'horse.id', '%(name)s')
db.reserved_horses.id_leason.requires=IS_IN_DB(db, 'leason.id', '%(week_day)s %(leason_time)s')
db.black_dates.id_semester.requires=IS_IN_DB(db, 'semester.id', '%(name)s')
db.cancelled_leasons.id_customer.requires=IS_IN_DB(db, 'customer.id')
db.cancelled_leasons.id_leason.requires=IS_IN_DB(db, 'leason.id')
db.rebooking.id_leason.requires=IS_IN_DB(db, 'leason.id')
db.rebooking.id_customer.requires=IS_IN_DB(db, 'customer.id')
db.leason.skill_level.requires=IS_IN_DB(db, 'skill_level.id', '%(skill_name)s')
db.owner_of_leason.leason_id.requires=IS_IN_DB(db, "leason.id", '%(week_day)s %(leason_time)s')
db.owner_of_leason.instructor_id.requires=IS_IN_DB(db, "instructor.id", 'Instruktör: %(name)s')
