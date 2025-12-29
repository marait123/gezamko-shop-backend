from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Permission class for admin users only."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin_user)


class IsStaffUser(permissions.BasePermission):
    """Permission class for staff and admin users."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff_user)


class IsCustomer(permissions.BasePermission):
    """Permission class for customers (authenticated users)."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsAdminOrStaffOrReadOnly(permissions.BasePermission):
    """
    Allow read-only access to everyone.
    Write access only to admin and staff users.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff_user)


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Object-level permission to only allow owners or staff to access.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff_user:
            return True
        if hasattr(obj, "user"):
            return obj.user == request.user
        return False


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission to only allow owners or admins to access.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin_user:
            return True
        if hasattr(obj, "user"):
            return obj.user == request.user
        return False


class ProductPermission(permissions.BasePermission):
    """
    Permission for products:
    - Anyone can read (GET, HEAD, OPTIONS)
    - Staff and Admin can create, update, delete
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff_user)


class OrderPermission(permissions.BasePermission):
    """
    Permission for orders:
    - Customers can create and view their own orders
    - Staff can view all orders
    - Admin can do everything
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff_user:
            return True
        return obj.user == request.user


class ComplaintPermission(permissions.BasePermission):
    """
    Permission for complaints:
    - Customers can create and view their own complaints
    - Staff can view and respond to all complaints
    - Admin can do everything
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff_user:
            return True
        return obj.user == request.user
