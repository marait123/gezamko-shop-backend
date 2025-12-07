# Gezamko Shop API Documentation

**Base URL:** `/api/v1/`

**Documentation UI:**
- Swagger: `/api/docs/`
- ReDoc: `/api/redoc/`

---

## Authentication

- **Development:** Session / Basic Auth
- **Production:** Keycloak Bearer Token

**User Roles:** `admin`, `staff`, `customer`

---

## Products

### List Products
```
GET /products/
```
**Auth:** None (Public)

**Query Params:**
| Param | Description |
|-------|-------------|
| `category` | Filter by category |
| `brand` | Filter by brand |
| `size` | Filter by size |
| `color` | Filter by color |
| `search` | Search name, description, SKU |
| `ordering` | `price`, `-price`, `name`, `created_at` |

**Response:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/v1/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Nike Air Max 270",
      "price": "150.00",
      "stock": 50,
      "category": "Running",
      "brand": "Nike",
      "is_in_stock": true,
      "primary_image": {
        "id": 1,
        "image": "/media/products/nike_air_max.jpg",
        "alt_text": "Nike Air Max 270",
        "is_primary": true
      }
    }
  ]
}
```

### Get Product
```
GET /products/{id}/
```
**Auth:** None (Public)

**Response:**
```json
{
  "id": 1,
  "name": "Nike Air Max 270",
  "description": "The Nike Air Max 270 delivers visible cushioning...",
  "price": "150.00",
  "stock": 50,
  "sku": "SKU-NIK-ABC123",
  "category": "Running",
  "brand": "Nike",
  "size": "42",
  "color": "Black/White",
  "is_active": true,
  "is_in_stock": true,
  "images": [
    {
      "id": 1,
      "image": "/media/products/nike_air_max.jpg",
      "alt_text": "Nike Air Max 270",
      "is_primary": true,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Create Product
```
POST /products/
```
**Auth:** Staff/Admin

**Request:**
```json
{
  "name": "Nike Air Max 270",
  "description": "The Nike Air Max 270 delivers...",
  "price": "150.00",
  "stock": 50,
  "sku": "SKU-NIK-ABC123",
  "category": "Running",
  "brand": "Nike",
  "size": "42",
  "color": "Black/White",
  "is_active": true
}
```

### Update Product
```
PUT /products/{id}/
PATCH /products/{id}/
```
**Auth:** Staff/Admin

### Delete Product
```
DELETE /products/{id}/
```
**Auth:** Staff/Admin

**Response:** `204 No Content`

### Upload Product Image
```
POST /products/{id}/upload_image/
```
**Auth:** Staff/Admin

**Content-Type:** `multipart/form-data`

**Request:**
| Field | Type | Required |
|-------|------|----------|
| `image` | file | Yes |
| `alt_text` | string | No |
| `is_primary` | boolean | No |

### Delete Product Image
```
DELETE /products/{id}/images/{image_id}/
```
**Auth:** Staff/Admin

---

## Users

### Get Profile
```
GET /users/profile/
```
**Auth:** Required

**Response:**
```json
{
  "id": 1,
  "username": "ahmed",
  "email": "ahmed@example.com",
  "role": "customer",
  "first_name": "Ahmed",
  "last_name": "Hassan",
  "phone_number": "+1234567890",
  "address": "123 Main St",
  "city": "Cairo",
  "country": "Egypt",
  "postal_code": "11511",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Update Profile
```
PUT /users/profile/
PATCH /users/profile/
```
**Auth:** Required

**Request:**
```json
{
  "first_name": "Ahmed",
  "last_name": "Hassan",
  "phone_number": "+1234567890",
  "address": "123 Main St",
  "city": "Cairo",
  "country": "Egypt",
  "postal_code": "11511"
}
```

### List Users
```
GET /users/
```
**Auth:** Admin only

### Get User
```
GET /users/{id}/
```
**Auth:** Admin only

---

## Orders

### List Orders
```
GET /orders/
```
**Auth:** Required (customers see own, staff see all)

**Query Params:**
| Param | Description |
|-------|-------------|
| `status` | `pending`, `confirmed`, `processing`, `shipped`, `delivered`, `cancelled` |

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "user": 1,
      "user_email": "ahmed@example.com",
      "status": "pending",
      "total_amount": "300.00",
      "shipping_address": "123 Main St",
      "shipping_city": "Cairo",
      "shipping_country": "Egypt",
      "shipping_postal_code": "11511",
      "phone_number": "+1234567890",
      "notes": "",
      "items": [
        {
          "id": 1,
          "product": 1,
          "product_name": "Nike Air Max 270",
          "product_price": "150.00",
          "quantity": 2,
          "subtotal": "300.00"
        }
      ],
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Get Order
```
GET /orders/{id}/
```
**Auth:** Required (owner or staff)

### Create Order
```
POST /orders/
```
**Auth:** Customer

**Request:**
```json
{
  "shipping_address": "123 Main St",
  "shipping_city": "Cairo",
  "shipping_country": "Egypt",
  "shipping_postal_code": "11511",
  "phone_number": "+1234567890",
  "notes": "Please call before delivery",
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    },
    {
      "product_id": 3,
      "quantity": 1
    }
  ]
}
```

### Update Order Status
```
PATCH /orders/{id}/update_status/
```
**Auth:** Staff/Admin

**Request:**
```json
{
  "status": "confirmed"
}
```

**Status Options:** `pending`, `confirmed`, `processing`, `shipped`, `delivered`, `cancelled`, `refunded`

### Cancel Order
```
POST /orders/{id}/cancel/
```
**Auth:** Owner (pending only) or Staff/Admin

---

## Payments

### List Payments
```
GET /payments/
```
**Auth:** Required (customers see own, staff see all)

**Response:**
```json
{
  "results": [
    {
      "id": 1,
      "order_id": 1,
      "payment_method": "card",
      "amount": "300.00",
      "status": "completed",
      "transaction_id": "txn_123456",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Get Payment
```
GET /payments/{id}/
```
**Auth:** Required (owner or staff)

### Initiate Payment
```
POST /payments/initiate/
```
**Auth:** Customer

**Request:**
```json
{
  "order_id": 1,
  "payment_method": "card"
}
```

**Payment Methods:** `card`, `wallet`, `cash`

**Response (Card/Wallet):**
```json
{
  "payment_id": 1,
  "iframe_url": "https://paymob.com/iframe/..."
}
```

**Response (Cash):**
```json
{
  "payment_id": 1,
  "message": "Cash on delivery payment created"
}
```

### Payment Callback (Webhook)
```
POST /payments/callback/?hmac={hmac}
```
**Auth:** None (Paymob webhook)

---

## Shipments

### List Shipments
```
GET /shipments/
```
**Auth:** Required (customers see own, staff see all)

**Query Params:**
| Param | Description |
|-------|-------------|
| `status` | `pending`, `processing`, `shipped`, `in_transit`, `out_for_delivery`, `delivered`, `returned`, `failed` |
| `shipping_method` | `standard`, `express`, `same_day` |

**Response:**
```json
{
  "results": [
    {
      "id": 1,
      "order_id": 1,
      "status": "shipped",
      "shipping_method": "standard",
      "tracking_number": "TRK123456",
      "shipping_address": "123 Main St",
      "shipping_city": "Cairo",
      "shipping_country": "Egypt",
      "shipping_postal_code": "11511",
      "recipient_name": "Ahmed Hassan",
      "recipient_phone": "+1234567890",
      "estimated_delivery": "2024-01-20T10:00:00Z",
      "actual_delivery": null,
      "shipping_cost": "25.00",
      "weight": "0.50",
      "notes": "",
      "tracking_updates": [
        {
          "id": 1,
          "status": "shipped",
          "location": "Cairo Hub",
          "description": "Package shipped",
          "timestamp": "2024-01-15T10:30:00Z"
        }
      ],
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Get Shipment
```
GET /shipments/{id}/
```
**Auth:** Required (owner or staff)

### Create Shipment
```
POST /shipments/
```
**Auth:** Admin only

**Request:**
```json
{
  "order_id": 1,
  "shipping_method": "standard",
  "recipient_name": "Ahmed Hassan",
  "recipient_phone": "+1234567890",
  "weight": "0.50",
  "notes": ""
}
```

### Update Shipment Status
```
PATCH /shipments/{id}/update_status/
```
**Auth:** Admin only

**Request:**
```json
{
  "status": "shipped"
}
```

### Get Tracking
```
GET /shipments/{id}/tracking/
```
**Auth:** Required (owner or staff)

**Response:**
```json
{
  "tracking_number": "TRK123456",
  "status": "shipped",
  "updates": [
    {
      "id": 1,
      "status": "shipped",
      "location": "Cairo Hub",
      "description": "Package shipped",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Get Shipping Rates
```
POST /shipments/rates/
```
**Auth:** Required

**Request:**
```json
{
  "destination": {
    "country": "Egypt",
    "city": "Cairo"
  },
  "weight": 1.0
}
```

**Response:**
```json
{
  "rates": [
    {
      "method": "standard",
      "cost": "25.00",
      "estimated_days": 5,
      "courier": "Posta"
    },
    {
      "method": "express",
      "cost": "50.00",
      "estimated_days": 2,
      "courier": "Posta"
    }
  ]
}
```

---

## Complaints

### List Complaints
```
GET /complaints/
```
**Auth:** Required (customers see own, staff see all)

**Query Params:**
| Param | Description |
|-------|-------------|
| `status` | `open`, `in_progress`, `waiting_customer`, `resolved`, `closed` |
| `category` | `order`, `product`, `shipping`, `payment`, `refund`, `other` |
| `priority` | `low`, `medium`, `high`, `urgent` |

**Response:**
```json
{
  "results": [
    {
      "id": 1,
      "user": 1,
      "user_email": "ahmed@example.com",
      "order": 1,
      "subject": "Wrong size delivered",
      "description": "I ordered size 42 but received size 40",
      "category": "order",
      "status": "open",
      "priority": "medium",
      "assigned_to": null,
      "assigned_to_email": null,
      "resolution": null,
      "responses": [],
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Get Complaint
```
GET /complaints/{id}/
```
**Auth:** Required (owner or staff)

### Create Complaint
```
POST /complaints/
```
**Auth:** Required

**Request:**
```json
{
  "order": 1,
  "subject": "Wrong size delivered",
  "description": "I ordered size 42 but received size 40",
  "category": "order"
}
```

**Categories:** `order`, `product`, `shipping`, `payment`, `refund`, `other`

### Update Complaint
```
PATCH /complaints/{id}/
```
**Auth:** Admin only

**Request:**
```json
{
  "status": "in_progress",
  "priority": "high",
  "assigned_to": 2,
  "resolution": null
}
```

### Add Response
```
POST /complaints/{id}/respond/
```
**Auth:** Required (owner or staff)

**Request:**
```json
{
  "message": "We apologize for the inconvenience. We will send the correct size."
}
```

### Resolve Complaint
```
POST /complaints/{id}/resolve/
```
**Auth:** Admin only

**Request:**
```json
{
  "resolution": "Replacement sent. Tracking: TRK789012"
}
```

### Close Complaint
```
POST /complaints/{id}/close/
```
**Auth:** Owner or Staff/Admin

### Assign Complaint
```
POST /complaints/{id}/assign/
```
**Auth:** Admin only

**Request:**
```json
{
  "assigned_to": 2
}
```

---

## Error Responses

**400 Bad Request:**
```json
{
  "field_name": ["Error message"]
}
```

**401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**404 Not Found:**
```json
{
  "detail": "Not found."
}
```
