# -*- coding: utf-8 -*-
from datetime import datetime

db.admin_settings.insert(variable_name="max_rebook_days",variable_value=28,description="Sets the max number of days forward an enduser can see rebookable dates")
db.admin_settings.insert(variable_name="active_semester",variable_value=1,description="Stores the active semester, changed by user")
db.admin_settings.insert(variable_name="hours_before_canx",variable_value=4,description="Set the time 4 hours before the leason beginsit is cancellable. ")
db.semester.insert(name="Hostterminen 2013",start_date="2013-08-12",end_date="2013-12-22")
db.skill_level.insert(skill_name="Nivå 1",skill_point=1,skill_type="Ponny")
db.skill_level.insert(skill_name="Nivå 2",skill_point=2,skill_type="Ponny")
db.leason.insert(week_day="Måndag",leason_time="18:00:00",leason_length=60,max_customers=6, skill_level=1,status="Active",leason_type="Ponny")
db.leason.insert(week_day="Tisdag",leason_time="18:00:00",leason_length=60,max_customers=6, skill_level=1,status="Active",leason_type="Ponny")
db.leason.insert(week_day="Onsdag",leason_time="18:00:00",leason_length=60,max_customers=6, skill_level=2,status="Active",leason_type="Ponny")
db.leason.insert(week_day="Torsdag",leason_time="18:00:00",leason_length=60,max_customers=6, skill_level=1,status="Active",leason_type="Ponny")
db.leason.insert(week_day="Fredag",leason_time="18:00:00",leason_length=60,max_customers=6, skill_level=2,status="Active",leason_type="Ponny")
db.leason.insert(week_day="Lördag",leason_time="18:00:00",leason_length=60,max_customers=6, skill_level=2,status="Active",leason_type="Ponny")
db.leason.insert(week_day="Söndag",leason_time="18:00:00",leason_length=60,max_customers=6, skill_level=1,status="Active",leason_type="Ponny")
db.customer.insert(first_name="Rikard", last_name="Rikardsson",status="Active")
db.leasons.insert(id_customer=1,id_leason=1)
db.leasons.insert(id_customer=1,id_leason=2)
db.leasons.insert(id_customer=1,id_leason=4)
db.leasons.insert(id_customer=1,id_leason=6)

db.instructor.insert(name="Johnny Jönsson")
db.instructor.insert(name="Svullo Svinsta")
db.owner_of_leason.insert(leason_id=1,instructor_id=1)
db.owner_of_leason.insert(leason_id=2,instructor_id=2)
db.owner_of_leason.insert(leason_id=3,instructor_id=1)
db.owner_of_leason.insert(leason_id=4,instructor_id=2)
db.owner_of_leason.insert(leason_id=4,instructor_id=1)

db.rebooking.insert(id_leason=3,id_customer=1,leason_date="2013-10-30",approval="notyet")
db.rebooking.insert(id_leason=3,id_customer=1,leason_date="2013-9-4",approval="notyet")

db.cancelled_leasons.insert(id_customer=1,id_leason=6,cancelled_date="2013-09-14",when_cancelled="2013-10-06 11:33:57")
db.cancelled_leasons.insert(id_customer=1,id_leason=6,cancelled_date="2013-11-02",when_cancelled="2013-10-06 11:33:57")

db.leasons_history.insert(id_customer=1,id_leason=6,id_semester=1,leason_length=60,leason_date="2013-08-17")
db.leasons_history.insert(id_customer=1,id_leason=6,id_semester=1,leason_length=60,leason_date="2013-08-24")
db.leasons_history.insert(id_customer=1,id_leason=6,id_semester=1,leason_length=60,leason_date="2013-08-31")
db.leasons_history.insert(id_customer=1,id_leason=6,id_semester=1,leason_length=60,leason_date="2013-09-07")
db.leasons_history.insert(id_customer=1,id_leason=6,id_semester=1,leason_length=60,leason_date="2013-09-21")
db.leasons_history.insert(id_customer=1,id_leason=6,id_semester=1,leason_length=60,leason_date="2013-09-28")

db.black_dates.insert(black_date="2013-08-20")
db.black_dates.insert(black_date="2013-09-16")
db.black_dates.insert(black_date="2013-11-28")

db.horse.insert(name="Balder",status="Aktiv",horse_type="Ponny")
db.horse.insert(name="Fanta",status="Aktiv",horse_type="Ponny")
db.horse.insert(name="Sandra",status="Aktiv",horse_type="Ponny")

db.reserved_horses.insert(id_customer=1,id_horse=2,id_leason=4,reserved_date="2013-10-31")
db.reserved_horses.insert(id_customer=1,id_horse=1,id_leason=4,reserved_date="2013-11-14")

db.messages.insert(subject="Ny ponny", body="Nu har vi fått en ny ponny som heter Stina i stallet", created=datetime.now())
db.messages.insert(subject="Junior tävling", body="Söndagen den 5 januari 2014 har vi tävling i junior hoppning kom gärna och titta.", created=datetime.now())

db.message_reference.insert(message_id=1, to_id=1, from_id=2, end_date=datetime.now())
db.message_reference.insert(message_id=2, to_id=1, from_id=2, end_date=datetime.now())

db.commit()
