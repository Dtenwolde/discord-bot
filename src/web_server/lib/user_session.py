from flask import session, g as flaskg


def session_user():
    """
    Return the current authenticated user.
    :return: the current authenticated user.
    :return: None if no user is logged in.
    """
    username = session['username'] if 'username' in session else None
    if username is not None:
        if not hasattr(flaskg, 'session_user'):
            flaskg.session_user = username
            if flaskg.session_user is None:
                del session['username']

        return flaskg.session_user
    return None


def session_is_authed():
    """
    Checks if the session is authorized.
    :return:
    """
    if 'username' not in session:
        return False

    return session_user() is not None


def session_user_set(user):
    """
    Set the current user associated with the session.
    If not None, session_is_authed() will return True and session_user() will return the user.
    If None, session_is_authed() will return False and session_user() will raise a ValueError.
    :param user: The user or None.
    """
    if user is None:
        del session['username']
    else:
        session['username'] = user
