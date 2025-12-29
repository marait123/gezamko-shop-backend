from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Complaint, ComplaintResponse
from .serializers import (
    ComplaintCreateSerializer,
    ComplaintResponseCreateSerializer,
    ComplaintSerializer,
    ComplaintUpdateSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List complaints",
        description="Get a list of complaints. Users see their own complaints, admins see all.",
    ),
    retrieve=extend_schema(
        summary="Get complaint details",
        description="Get detailed information about a specific complaint.",
    ),
    create=extend_schema(
        summary="Create a complaint", description="Create a new complaint ticket."
    ),
)
class ComplaintViewSet(viewsets.ModelViewSet):
    """ViewSet for managing complaints."""

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "category", "priority"]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Complaint.objects.all()
        return Complaint.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return ComplaintCreateSerializer
        if self.action in ["update", "partial_update"]:
            return ComplaintUpdateSerializer
        if self.action == "respond":
            return ComplaintResponseCreateSerializer
        return ComplaintSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        summary="Add response to complaint",
        description="Add a response message to a complaint.",
        request=ComplaintResponseCreateSerializer,
    )
    @action(detail=True, methods=["post"])
    def respond(self, request, pk=None):
        complaint = self.get_object()
        serializer = ComplaintResponseCreateSerializer(data=request.data)

        if serializer.is_valid():
            ComplaintResponse.objects.create(
                complaint=complaint,
                user=request.user,
                message=serializer.validated_data["message"],
                is_staff_response=request.user.is_staff,
            )

            if request.user.is_staff and complaint.status == Complaint.Status.OPEN:
                complaint.status = Complaint.Status.IN_PROGRESS
                complaint.save(update_fields=["status"])
            elif (
                not request.user.is_staff
                and complaint.status == Complaint.Status.WAITING_CUSTOMER
            ):
                complaint.status = Complaint.Status.IN_PROGRESS
                complaint.save(update_fields=["status"])

            return Response(ComplaintSerializer(complaint).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Close complaint",
        description="Close a complaint. Users can close their own complaints.",
    )
    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        complaint = self.get_object()

        if complaint.user != request.user and not request.user.is_staff:
            return Response(
                {"error": "You can only close your own complaints"},
                status=status.HTTP_403_FORBIDDEN,
            )

        complaint.status = Complaint.Status.CLOSED
        complaint.save(update_fields=["status"])

        return Response(ComplaintSerializer(complaint).data)

    @extend_schema(
        summary="Resolve complaint",
        description="Mark a complaint as resolved. Admin access required.",
    )
    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def resolve(self, request, pk=None):
        complaint = self.get_object()
        resolution = request.data.get("resolution", "")

        complaint.status = Complaint.Status.RESOLVED
        complaint.resolution = resolution
        complaint.save(update_fields=["status", "resolution"])

        return Response(ComplaintSerializer(complaint).data)

    @extend_schema(
        summary="Assign complaint",
        description="Assign a complaint to a staff member. Admin access required.",
    )
    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def assign(self, request, pk=None):
        complaint = self.get_object()
        assigned_to_id = request.data.get("assigned_to")

        if assigned_to_id:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            try:
                assigned_user = User.objects.get(id=assigned_to_id, is_staff=True)
                complaint.assigned_to = assigned_user
                complaint.save(update_fields=["assigned_to"])
            except User.DoesNotExist:
                return Response(
                    {"error": "Staff member not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        return Response(ComplaintSerializer(complaint).data)
