"""
Database seeding command for the Gezamko Shop.

This command populates the database with sample data including:
- Users (admin, staff, customers)
- Products with real images from the web
- Sample orders

Usage:
    python manage.py seed_database
    python manage.py seed_database --clear  # Clear existing data first
    python manage.py seed_database --products-only  # Only seed products
    python manage.py seed_database --users-only  # Only seed users
"""

import random
import uuid
from decimal import Decimal
from io import BytesIO

import requests
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from products.models import Product, ProductImage
from users.models import User


class Command(BaseCommand):
    help = "Seed the database with sample data including products with real images"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before seeding",
        )
        parser.add_argument(
            "--products-only",
            action="store_true",
            help="Only seed products",
        )
        parser.add_argument(
            "--users-only",
            action="store_true",
            help="Only seed users",
        )
        parser.add_argument(
            "--no-images",
            action="store_true",
            help="Skip downloading images (faster seeding)",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting database seeding..."))

        if options["clear"]:
            self.clear_data()

        if options["products_only"]:
            self.seed_products(skip_images=options["no_images"])
        elif options["users_only"]:
            self.seed_users()
        else:
            self.seed_users()
            self.seed_products(skip_images=options["no_images"])
            self.seed_orders()

        self.stdout.write(self.style.SUCCESS("Database seeding completed!"))

    def clear_data(self):
        """Clear existing data from the database."""
        self.stdout.write(self.style.WARNING("Clearing existing data..."))

        # Import here to avoid circular imports
        from orders.models import Order, OrderItem

        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        ProductImage.objects.all().delete()
        Product.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS("Existing data cleared."))

    def seed_users(self):
        """Create sample users."""
        self.stdout.write("Creating users...")

        users_data = [
            {
                "username": "admin",
                "email": "admin@gezamko.com",
                "password": "admin123!@#",
                "first_name": "Admin",
                "last_name": "User",
                "role": User.Role.ADMIN,
                "phone_number": "+1234567890",
                "address": "123 Admin Street",
                "city": "Cairo",
                "country": "Egypt",
                "postal_code": "11511",
            },
            {
                "username": "staff1",
                "email": "staff1@gezamko.com",
                "password": "staff123!@#",
                "first_name": "Sarah",
                "last_name": "Johnson",
                "role": User.Role.STAFF,
                "phone_number": "+1234567891",
                "address": "456 Staff Avenue",
                "city": "Alexandria",
                "country": "Egypt",
                "postal_code": "21500",
            },
            {
                "username": "staff2",
                "email": "staff2@gezamko.com",
                "password": "staff123!@#",
                "first_name": "Mohamed",
                "last_name": "Ali",
                "role": User.Role.STAFF,
                "phone_number": "+1234567892",
                "address": "789 Staff Road",
                "city": "Giza",
                "country": "Egypt",
                "postal_code": "12511",
            },
            {
                "username": "customer1",
                "email": "ahmed@example.com",
                "password": "customer123!@#",
                "first_name": "Ahmed",
                "last_name": "Hassan",
                "role": User.Role.CUSTOMER,
                "phone_number": "+1234567893",
                "address": "101 Customer Lane",
                "city": "Cairo",
                "country": "Egypt",
                "postal_code": "11311",
            },
            {
                "username": "customer2",
                "email": "fatima@example.com",
                "password": "customer123!@#",
                "first_name": "Fatima",
                "last_name": "Ibrahim",
                "role": User.Role.CUSTOMER,
                "phone_number": "+1234567894",
                "address": "202 Buyer Street",
                "city": "Luxor",
                "country": "Egypt",
                "postal_code": "85511",
            },
            {
                "username": "customer3",
                "email": "omar@example.com",
                "password": "customer123!@#",
                "first_name": "Omar",
                "last_name": "Mahmoud",
                "role": User.Role.CUSTOMER,
                "phone_number": "+1234567895",
                "address": "303 Shopping Blvd",
                "city": "Aswan",
                "country": "Egypt",
                "postal_code": "81511",
            },
        ]

        for user_data in users_data:
            password = user_data.pop("password")
            user, created = User.objects.get_or_create(
                username=user_data["username"],
                defaults=user_data,
            )
            if created:
                try:
                    validate_password(password, user=user)
                except ValidationError as exc:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  Password for {user.username} failed validation: {exc.messages}"
                        )
                    )
                user.set_password(password)
                user.save()
                self.stdout.write(f"  Created user: {user.username} ({user.role})")
            else:
                self.stdout.write(f"  User already exists: {user.username}")

        self.stdout.write(self.style.SUCCESS(f"Created {len(users_data)} users."))

    def seed_products(self, skip_images=False):
        """Create sample products with real images."""
        self.stdout.write("Creating products...")

        # Product data with real image URLs from various free sources
        products_data = [
            # Running Shoes
            {
                "name": "Nike Air Max 270",
                "description": (
                    "The Nike Air Max 270 delivers visible cushioning under every step. "
                    "Updated for modern comfort, it features Nike's biggest heel Air unit "
                    "yet for a super-soft ride that feels as impossible as it looks."
                ),
                "price": Decimal("150.00"),
                "stock": 50,
                "category": "Running",
                "brand": "Nike",
                "size": "42",
                "color": "Black/White",
                "images": [
                    "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800",
                    "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=800",
                ],
            },
            {
                "name": "Adidas Ultraboost 22",
                "description": (
                    "Experience epic energy with the Adidas Ultraboost 22. These running shoes feature "
                    "a BOOST midsole for incredible responsiveness and energy return with every stride."
                ),
                "price": Decimal("180.00"),
                "stock": 35,
                "category": "Running",
                "brand": "Adidas",
                "size": "43",
                "color": "Core Black",
                "images": [
                    "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=800",
                    "https://images.unsplash.com/photo-1605348532760-6753d2c43329?w=800",
                ],
            },
            {
                "name": "New Balance Fresh Foam 1080v12",
                "description": (
                    "The Fresh Foam 1080v12 is designed for long-distance comfort with plush Fresh Foam X "
                    "cushioning. Perfect for runners who want premium comfort mile after mile."
                ),
                "price": Decimal("165.00"),
                "stock": 40,
                "category": "Running",
                "brand": "New Balance",
                "size": "44",
                "color": "Navy Blue",
                "images": [
                    "https://images.unsplash.com/photo-1539185441755-769473a23570?w=800",
                ],
            },
            # Casual Shoes
            {
                "name": "Converse Chuck Taylor All Star",
                "description": (
                    "The iconic Chuck Taylor All Star. A timeless classic that has been a style staple since "
                    "1917. Features canvas upper and rubber sole for everyday wear."
                ),
                "price": Decimal("65.00"),
                "stock": 100,
                "category": "Casual",
                "brand": "Converse",
                "size": "41",
                "color": "Classic White",
                "images": [
                    "https://images.unsplash.com/photo-1607522370275-f14206abe5d3?w=800",
                    "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=800",
                ],
            },
            {
                "name": "Vans Old Skool",
                "description": (
                    "The Old Skool is Vans' classic skate shoe and the first to feature the iconic side stripe. "
                    "A comfortable low-top with durable suede and canvas uppers."
                ),
                "price": Decimal("70.00"),
                "stock": 75,
                "category": "Casual",
                "brand": "Vans",
                "size": "42",
                "color": "Black/White",
                "images": [
                    "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800",
                ],
            },
            {
                "name": "Puma Suede Classic",
                "description": (
                    "The PUMA Suede hit the scene in 1968 and has been an icon ever since. With its signature "
                    "suede upper and formstrip branding, it's a true original."
                ),
                "price": Decimal("75.00"),
                "stock": 60,
                "category": "Casual",
                "brand": "Puma",
                "size": "43",
                "color": "Burgundy",
                "images": [
                    "https://images.unsplash.com/photo-1600185365926-3a2ce3cdb9eb?w=800",
                ],
            },
            # Basketball Shoes
            {
                "name": "Nike Air Jordan 1 Retro High",
                "description": (
                    "The Air Jordan 1 Retro High remakes the legendary sneaker that started it all. Premium "
                    "leather construction with Nike Air cushioning for unmatched style and comfort."
                ),
                "price": Decimal("170.00"),
                "stock": 25,
                "category": "Basketball",
                "brand": "Nike",
                "size": "44",
                "color": "Chicago Red",
                "images": [
                    "https://images.unsplash.com/photo-1552346154-21d32810aba3?w=800",
                    "https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=800",
                ],
            },
            {
                "name": "Adidas Harden Vol. 6",
                "description": (
                    "James Harden's signature shoe built for explosive moves on the court. Features Boost "
                    "cushioning and a lightweight design for quick cuts and drives."
                ),
                "price": Decimal("160.00"),
                "stock": 30,
                "category": "Basketball",
                "brand": "Adidas",
                "size": "45",
                "color": "Cloud White",
                "images": [
                    "https://images.unsplash.com/photo-1579338559194-a162d19bf842?w=800",
                ],
            },
            # Formal Shoes
            {
                "name": "Cole Haan Oxford Dress Shoe",
                "description": (
                    "Classic Oxford dress shoes crafted with premium leather. Features Grand.OS technology for "
                    "lightweight comfort that lasts all day."
                ),
                "price": Decimal("200.00"),
                "stock": 20,
                "category": "Formal",
                "brand": "Cole Haan",
                "size": "42",
                "color": "British Tan",
                "images": [
                    "https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=800",
                ],
            },
            {
                "name": "Clarks Desert Boot",
                "description": (
                    "The iconic Clarks Desert Boot. Handcrafted with premium suede and crepe rubber sole. "
                    "A timeless design that works for any occasion."
                ),
                "price": Decimal("140.00"),
                "stock": 35,
                "category": "Formal",
                "brand": "Clarks",
                "size": "43",
                "color": "Sand Suede",
                "images": [
                    "https://images.unsplash.com/photo-1608256246200-53e635b5b65f?w=800",
                ],
            },
            # Training Shoes
            {
                "name": "Nike Metcon 8",
                "description": (
                    "The Nike Metcon 8 is the gold standard for weight training. Stable, durable, and "
                    "supportive for your toughest workouts."
                ),
                "price": Decimal("130.00"),
                "stock": 45,
                "category": "Training",
                "brand": "Nike",
                "size": "44",
                "color": "Wolf Grey",
                "images": [
                    "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=800",
                ],
            },
            {
                "name": "Reebok Nano X2",
                "description": (
                    "Built for versatility, the Reebok Nano X2 handles any workout. Floatride Energy Foam provides "
                    "responsive cushioning for high-intensity training."
                ),
                "price": Decimal("135.00"),
                "stock": 40,
                "category": "Training",
                "brand": "Reebok",
                "size": "43",
                "color": "Pure Grey",
                "images": [
                    "https://images.unsplash.com/photo-1584735175315-9d5df23860e6?w=800",
                ],
            },
            # Sandals
            {
                "name": "Birkenstock Arizona",
                "description": (
                    "The iconic Birkenstock Arizona sandal with contoured cork footbed. "
                    "Offers superior arch support and all-day comfort."
                ),
                "price": Decimal("100.00"),
                "stock": 55,
                "category": "Sandals",
                "brand": "Birkenstock",
                "size": "41",
                "color": "Tobacco Brown",
                "images": [
                    "https://images.unsplash.com/photo-1603487742131-4160ec999306?w=800",
                ],
            },
            {
                "name": "Teva Original Universal",
                "description": (
                    "The sandal that started it all. Quick-dry webbing upper with universal strapping "
                    "system for a secure, adjustable fit."
                ),
                "price": Decimal("50.00"),
                "stock": 70,
                "category": "Sandals",
                "brand": "Teva",
                "size": "42",
                "color": "Black",
                "images": [
                    "https://images.unsplash.com/photo-1562273138-f46be4ebdf33?w=800",
                ],
            },
            # Hiking Boots
            {
                "name": "Timberland 6-Inch Premium Boot",
                "description": (
                    "The original Timberland boot. Waterproof construction with premium leather and padded collar "
                    "for all-day comfort on any terrain."
                ),
                "price": Decimal("198.00"),
                "stock": 30,
                "category": "Boots",
                "brand": "Timberland",
                "size": "44",
                "color": "Wheat Nubuck",
                "images": [
                    "https://images.unsplash.com/photo-1520639888713-7851133b1ed0?w=800",
                ],
            },
            {
                "name": "Salomon X Ultra 4 GTX",
                "description": (
                    "Lightweight hiking shoe with GORE-TEX waterproof protection. Advanced Chassis technology "
                    "for stability on technical terrain."
                ),
                "price": Decimal("175.00"),
                "stock": 25,
                "category": "Hiking",
                "brand": "Salomon",
                "size": "43",
                "color": "Quiet Shade",
                "images": [
                    "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=800",
                ],
            },
            # Slip-Ons
            {
                "name": "TOMS Classic Alpargata",
                "description": (
                    "The shoe that started the One for One movement. Lightweight canvas slip-on with "
                    "cushioned insole for everyday comfort."
                ),
                "price": Decimal("55.00"),
                "stock": 80,
                "category": "Casual",
                "brand": "TOMS",
                "size": "41",
                "color": "Ash Grey",
                "images": [
                    "https://images.unsplash.com/photo-1512374382149-233c42b6a83b?w=800",
                ],
            },
            {
                "name": "Skechers Go Walk 6",
                "description": (
                    "Ultra-lightweight walking shoe with Goga Mat Technology insole. "
                    "Air-Cooled Memory Foam for maximum comfort."
                ),
                "price": Decimal("80.00"),
                "stock": 65,
                "category": "Walking",
                "brand": "Skechers",
                "size": "42",
                "color": "Navy",
                "images": [
                    "https://images.unsplash.com/photo-1491553895911-0055uj8161?w=800",
                ],
            },
            # Premium/Limited Edition
            {
                "name": "Nike Dunk Low Retro",
                "description": (
                    "Created for the hardwood but taken to the streets, the Nike Dunk Low Retro returns with crisp "
                    "overlays and classic team colors."
                ),
                "price": Decimal("110.00"),
                "stock": 15,
                "category": "Casual",
                "brand": "Nike",
                "size": "43",
                "color": "Panda Black/White",
                "images": [
                    "https://images.unsplash.com/photo-1597045566677-8cf032ed6634?w=800",
                    "https://images.unsplash.com/photo-1584735175315-9d5df23860e6?w=800",
                ],
            },
            {
                "name": "Yeezy Boost 350 V2",
                "description": (
                    "The Yeezy Boost 350 V2 features a Primeknit upper with distinctive center stitching. "
                    "Full-length Boost cushioning for ultimate comfort."
                ),
                "price": Decimal("230.00"),
                "stock": 10,
                "category": "Casual",
                "brand": "Adidas",
                "size": "44",
                "color": "Bone",
                "images": [
                    "https://images.unsplash.com/photo-1587563871167-1ee9c731aefb?w=800",
                ],
            },
        ]

        for product_data in products_data:
            images = product_data.pop("images", [])
            sku = f"SKU-{product_data['brand'][:3].upper()}-{uuid.uuid4().hex[:6].upper()}"

            product, created = Product.objects.get_or_create(
                name=product_data["name"],
                defaults={**product_data, "sku": sku},
            )

            if created:
                self.stdout.write(f"  Created product: {product.name}")

                if not skip_images:
                    self._download_and_save_images(product, images)
            else:
                self.stdout.write(f"  Product already exists: {product.name}")

        self.stdout.write(self.style.SUCCESS(f"Created {len(products_data)} products."))

    def _download_and_save_images(self, product, image_urls):
        """Download images from URLs and save them to the product."""
        for index, url in enumerate(image_urls):
            try:
                self.stdout.write(
                    f"    Downloading image {index + 1} for {product.name}..."
                )
                response = requests.get(url, timeout=30)
                response.raise_for_status()

                # Get the image content
                image_content = BytesIO(response.content)

                # Generate a unique filename
                ext = "jpg"  # Default to jpg for Unsplash images
                filename = f"{product.name.lower().replace(' ', '_')}_{index + 1}.{ext}"

                # Create the ProductImage
                product_image = ProductImage(
                    product=product,
                    alt_text=f"{product.name} - Image {index + 1}",
                    is_primary=(index == 0),  # First image is primary
                )
                product_image.image.save(
                    filename,
                    ContentFile(image_content.getvalue()),
                    save=True,
                )

                self.stdout.write(self.style.SUCCESS(f"    Saved image: {filename}"))

            except requests.exceptions.RequestException as e:
                self.stdout.write(
                    self.style.WARNING(f"    Failed to download image from {url}: {e}")
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"    Error saving image: {e}"))

    def seed_orders(self):
        """Create sample orders."""
        self.stdout.write("Creating sample orders...")

        from orders.models import Order, OrderItem

        # Get customers
        customers = User.objects.filter(role=User.Role.CUSTOMER)
        products = Product.objects.filter(is_active=True)

        if not customers.exists():
            self.stdout.write(
                self.style.WARNING("No customers found. Skipping order creation.")
            )
            return

        if not products.exists():
            self.stdout.write(
                self.style.WARNING("No products found. Skipping order creation.")
            )
            return

        orders_created = 0

        for customer in customers:
            # Create 1-3 orders per customer
            num_orders = random.randint(1, 3)

            for _ in range(num_orders):
                # Select random products for this order
                num_items = random.randint(1, 4)
                selected_products = random.sample(
                    list(products), min(num_items, products.count())
                )

                with transaction.atomic():
                    order = Order.objects.create(
                        user=customer,
                        status=random.choice(
                            [
                                Order.Status.PENDING,
                                Order.Status.CONFIRMED,
                                Order.Status.PROCESSING,
                                Order.Status.SHIPPED,
                                Order.Status.DELIVERED,
                            ]
                        ),
                        shipping_address=customer.address or "123 Test Street",
                        shipping_city=customer.city or "Cairo",
                        shipping_country=customer.country or "Egypt",
                        shipping_postal_code=customer.postal_code or "11511",
                        phone_number=customer.phone_number or "+1234567890",
                        notes=random.choice(
                            [
                                "",
                                "Please leave at door",
                                "Call before delivery",
                                "Gift wrap please",
                            ]
                        ),
                    )

                    for product in selected_products:
                        quantity = random.randint(1, 3)
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            product_name=product.name,
                            product_price=product.price,
                            quantity=quantity,
                        )

                    order.calculate_total()
                    orders_created += 1
                    self.stdout.write(
                        f"  Created order #{order.id} for {customer.username} "
                        f"(${order.total_amount})"
                    )

        self.stdout.write(self.style.SUCCESS(f"Created {orders_created} orders."))
