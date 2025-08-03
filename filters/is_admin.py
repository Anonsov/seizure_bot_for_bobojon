from config import admin_json
def is_admin_function(tg_id):
    if tg_id in admin_json:
        return admin_json[tg_id]
    else:
        return False
