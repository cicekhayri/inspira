from inspira.requests import RequestContext


def login_user():
    request = RequestContext.get_request()
    request.set_session("logged_in", True)


def logout_user():
    request = RequestContext.get_request()
    session = request.session

    if "logged_in" in session:
        request.remove_session("logged_in")
