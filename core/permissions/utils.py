def user_has_permission(user, permission_key):
    if not user or not getattr(user, "is_authenticated", False):
        return False
    for role in user.roles.all():
        if role.permissions.filter(key=permission_key).exists():
            return True
    return False
