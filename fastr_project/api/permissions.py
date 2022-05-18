from rest_framework.permissions import BasePermission


class IsSeller(BasePermission):
    message = "Failed! You have to be a seller not a buyer!"

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.type == 'seller'
        )


class IsSellerHasShop(BasePermission):
    message = "Failed! You do not have shop!"

    def has_permission(self, request, view):
        user = request.user
        if not hasattr(user, 'shop'):
            return False
        return True


class IsSellerHasNoShop(BasePermission):
    message = "Failed! You already have shop!"

    def has_permission(self, request, view):
        user = request.user
        if hasattr(user, 'shop'):
            return False
        return True


class IsBuyer(BasePermission):
    message = "Failed! You have to be a buyer not a seller!"

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.type == 'buyer'
        )
