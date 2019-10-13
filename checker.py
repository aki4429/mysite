from flask import redirect, session, flash

from functools import wraps

users=[]
users.append(['huklajapan', '561731'])
users.append(['akiyoshi', 'pass'])

def check_user(sess):
    for user in users:
        if sess['username'] == user[0]:
            if sess['password'] == user[1]:
                return 'ok'
            else:
                return 'パスワードが違います'

    return 'そのユーザー名は登録がありません。'
#    return  redirect('/login')

def check_logged_in(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            return redirect('/login')
        result = check_user(session)
        if result == 'ok' :
            return func(*args, **kwargs)
        return result 
    return wrapper


