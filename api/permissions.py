from rest_framework.permissions import BasePermission

class IsJobCreatorOrApplicant(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Only the job creator or the applicant can view/update the application
        return obj.job.creator == request.user or obj.applicant == request.user
