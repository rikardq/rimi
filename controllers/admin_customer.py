# coding: utf8

# Administrate customers

helper_rideraccount = "En ryttare måste kopplas till ett användarkonto. Ett användarkonto är en email adress och ett lösenord som kan användas för att logga in i systemet. När en ryttare är kopplad till ett användarkonto, så kan det kontot administrera ryttarens lektioner. Detta betyder att vi kan använda ett användarkonto för att administrera flera ryttare."

def index():
    return dict(message="")

def add():
    # Adding a new customer consists of adding personal information, then requesting
    # if a new auth_user should be created or if it should be linked to an existing one
    step = int(request.args(0) or 1)
    auth_fields = ('email')
    choice = ""

    # Step 1, name and such
    if step == 1:
        session.wizard = {}
        form = SQLFORM.factory(*[db.customer.first_name,db.customer.last_name,db.customer.status])
    if step == 2:
        form = ""
        choice = P(helper_rideraccount) +  A("Nytt användarkonto",callback=URL(args=[3,"new"]), target="content") + BR() + A("Lägg till under existerande andvändarkonto",_href=URL(args=[3,"already"])) 
    if step == 3:
        switch = request.args(1)
        if switch == "new":
            form = SQLFORM.factory(db.auth_user.email)
            if form.process().accepted:
                new_authid = db.auth_user.validate_and_insert(first_name=session.wizard["first_name"],
                    last_name=session.wizard["last_name"],
                    email=form.vars.email)
                session.wizard["auth_user_id"] = new_authid["id"]
                redirect(URL(args=[4]))
        if switch == "already":
            form = SQLFORM.factory(db.customer.auth_user_id)
            if form.process().accepted:
                session.wizard.update(form.vars)
                redirect(URL(args=step+1))

    if step == 4:
        form = session.wizard 
        db.customer.insert(**session.wizard)
        session.flash = T("Wizard CompleteZ")
        redirect(URL(args=1))

    if step < 2: 
        if form.accepts(request,session):
            session.wizard.update(form.vars)
            redirect(URL(args=step+1))

    return dict(choice=choice,form=form,step=step)
