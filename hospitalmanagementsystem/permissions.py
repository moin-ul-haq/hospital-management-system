from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role=='admin'
    
class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return request.user.role =='patient'
    

class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return request.user.role =='doctor'
    
class IsReceptionist(BasePermission):
    def has_permission(self, request, view):
        return request.user.role =='receptionist'
    
class IsAdminOrReceptionist(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['admin', 'receptionist']