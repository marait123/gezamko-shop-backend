from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from users.permissions import IsStaffUser, ProductPermission

from .filters import ProductFilter
from .models import Product, ProductImage
from .serializers import (
    ProductCreateUpdateSerializer,
    ProductImageSerializer,
    ProductListSerializer,
    ProductSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List all products",
        description="Get a list of all active products. Public access.",
    ),
    retrieve=extend_schema(
        summary="Get product details",
        description="Get detailed information about a specific product. Public access.",
    ),
    create=extend_schema(
        summary="Create a product",
        description="Create a new product. Staff/Admin access required.",
    ),
    update=extend_schema(
        summary="Update a product",
        description="Update a product. Staff/Admin access required.",
    ),
    partial_update=extend_schema(
        summary="Partially update a product",
        description="Partially update a product. Staff/Admin access required.",
    ),
    destroy=extend_schema(
        summary="Delete a product",
        description="Delete a product. Staff/Admin access required.",
    ),
)
class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products.

    Permissions:
    - GET (list, retrieve): Public access
    - POST, PUT, PATCH, DELETE: Staff and Admin only
    """

    queryset = Product.objects.filter(is_active=True)
    permission_classes = [ProductPermission]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ProductFilter
    search_fields = ["name", "description", "sku"]
    ordering_fields = ["price", "created_at", "name"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return ProductCreateUpdateSerializer
        return ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        if (
            not self.request.user.is_authenticated
            or not self.request.user.is_staff_user
        ):
            queryset = queryset.filter(is_active=True)
        return queryset

    @extend_schema(
        summary="Upload product image",
        description="Upload an image for a specific product. Staff/Admin access required.",
    )
    @action(
        detail=True,
        methods=["post"],
        parser_classes=[MultiPartParser, FormParser],
        permission_classes=[IsStaffUser],
    )
    def upload_image(self, request, pk=None):
        product = self.get_object()
        serializer = ProductImageSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete product image",
        description="Delete a specific image from a product. Staff/Admin access required.",
    )
    @action(
        detail=True,
        methods=["delete"],
        url_path="images/(?P<image_id>[^/.]+)",
        permission_classes=[IsStaffUser],
    )
    def delete_image(self, request, pk=None, image_id=None):
        product = self.get_object()
        try:
            image = product.images.get(id=image_id)
            image.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProductImage.DoesNotExist:
            return Response(
                {"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND
            )
