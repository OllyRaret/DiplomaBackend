from rest_framework import permissions


class IsFounderOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or obj.founder.user == request.user


class IsStartupFounder(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'founder_profile')