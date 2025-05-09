from app.auths.auth import RoleChecker


admin_only = RoleChecker(allowed_roles=['admin'])
staff_only = RoleChecker(allowed_roles=['staff'])
manager_only = RoleChecker(allowed_roles=['manager'])