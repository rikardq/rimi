# -*- coding: utf-8 -*-
letlive = ["auth_user","auth_group","auth_membership","auth_permission","auth_event","auth_cas"]
for table_name in db.tables():
    if table_name not in letlive:
        db[table_name].drop()
db.commit()
