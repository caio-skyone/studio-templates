"""A small spec exercising every rule the generator must get right."""

SPEC: dict = {
    "openapi": "3.0.0",
    "paths": {
        "/v1/customers": {
            "get": {
                "summary": "List customers",
                "parameters": [
                    {
                        "name": "limit",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "integer", "example": 10},
                        "description": "A limit on the number of objects.",
                    },
                    {
                        "name": "expand",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "array"},
                        "description": "Specifies which fields to expand.",
                    },
                    {
                        "name": "created",
                        "in": "query",
                        "required": False,
                        "style": "deepObject",
                        "schema": {"type": "object"},
                        "description": "A filter on the list based on created.",
                    },
                ],
            },
            "post": {
                "summary": "Create customer",
                "requestBody": {
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {"email": {"type": "string"}},
                                "required": ["email"],
                            }
                        }
                    }
                },
            },
        },
        "/v1/customers/{customer}": {
            "get": {"summary": "Retrieve customer"},
        },
        "/v1/payment_intents/{intent}": {
            "get": {"summary": "Retrieve payment intent"},
        },
        "/v1/setup_intents/{intent}": {
            "get": {"summary": "Retrieve setup intent"},
        },
        "/v1/accounts/{account}/people/{person}": {
            "get": {"summary": "Retrieve person"},
        },
        "/v1/accounts/{account}/persons/{person}": {
            "get": {"summary": "Retrieve person"},
        },
        "/v1/files": {
            "post": {
                "summary": "Create file",
                "servers": [{"url": "https://files.stripe.com"}],
                "requestBody": {
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "file": {"type": "string", "format": "binary"},
                                    "purpose": {"type": "string"},
                                    "note": {"type": "string"},
                                },
                                "required": ["file", "purpose"],
                            }
                        }
                    }
                },
            }
        },
        "/v1/balance/history/{id}": {
            "get": {"summary": "Retrieve balance transaction"},
        },
        "/v1/charges": {
            "get": {
                "summary": "List charges",
                "parameters": [
                    {
                        "name": "X-Required-Header",
                        "in": "header",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "A required header.",
                    },
                    {
                        "name": "X-Optional-Header",
                        "in": "header",
                        "required": False,
                        "schema": {"type": "string"},
                        "description": "An optional header.",
                    },
                    {
                        "name": "Authorization",
                        "in": "header",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Bearer token for the connected account.",
                    },
                    {
                        "name": "token",
                        "in": "header",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Auth token, rescued via config override.",
                    },
                ],
            },
        },
    },
}

CONFIG: dict = {
    "module": {
        "name": "Stripe",
        "description": "Payments",
        "authentication_type": "bearer-token",
        "strip_path_prefix": ["v1"],
    },
    "include_roots": [
        "customers",
        "payment_intents",
        "setup_intents",
        "accounts",
        "files",
        "balance",
        "charges",
    ],
    "domains": {
        "payment_intents": {"domain": "Payment Intents", "block": "core"},
        "setup_intents": {"domain": "Setup Intents", "block": "core"},
        "balance.history": {"domain": "Balance", "block": "core"},
        "files": {"domain": "Files", "block": "ops"},
    },
    "exclude": [
        {"key": "accounts.persons", "reason": "alias exato de accounts.people"}
    ],
    "headers": [
        {"key": "Stripe-Version", "param": "stripe_version"},
        {
            "key": "Idempotency-Key",
            "param": "idempotency_key",
            "methods": ["POST", "DELETE"],
        },
    ],
    "naming": {"singular": {"history": "balance_transaction"}},
    "overrides": {"auth_headers": {"remove": ["token"]}},
}
