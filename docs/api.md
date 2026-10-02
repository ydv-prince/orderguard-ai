# API Documentation

The OrderGuard API uses standard HTTP methods and JSON payloads. It is built with FastAPI and documented interactively via OpenAPI. 
You can view the full interactive docs locally by running the server and visiting `http://localhost:8000/docs`.

## Base URL
`/api/v1`

## Authentication
Protected endpoints require a JWT token passed in the Authorization header.
`Authorization: Bearer <token>`

## Endpoints

### `POST /auth/login`
Authenticate a user or handle Google OAuth logins.

### `GET /orders/`
Retrieve a paginated list of orders associated with the authenticated merchant.
- **Response**: Array of `OrderResponse` objects including predictive metadata and status.

### `POST /orders/`
Create a new order.
- **Body**:
  ```json
  {
    "customer_details": {
      "name": "string",
      "email": "string",
      "phone": "string",
      "address": "string"
    },
    "total_amount": 0,
    "items_count": 1
  }
  ```
- **Response**: The created order object, synchronously populated with its AI risk assessment.

### `PUT /orders/{order_id}/verify`
Update the verification status of an order.
- **Body**:
  ```json
  {
    "action": "approve" | "prepaid_only",
    "notes": "Optional review notes"
  }
  ```
- **Response**: The updated order record indicating the new state (`verified` or `prepaid_required`).
