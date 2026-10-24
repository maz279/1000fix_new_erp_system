#!/usr/bin/env python3
"""generate_openapi_contracts.py — Author and compile the 11 Bounded Context OpenAPI 3.1.0 Contracts.

Realises IN-002 §3.1 & B-16:
1. service-delivery: M01–M06, M31
2. customer-engagement: M07, M10, M27, M32–M35
3. commercial: M08, M09, M11, M36–M40
4. marketplace: M12, M38
5. circular: M13, M14, M18
6. supply-chain: M15, M16, M41–M44
7. asset: M17, M45–M48
8. finance: M19, M20, M49–M54
9. people: M21, M22, M55–M59
10. governance: M23, M24, M60, M61, M66, M67
11. platform: M25, M26, M28–M30, M62–M65
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OPENAPI_DIR = REPO_ROOT / "contracts" / "openapi"
OPENAPI_DIR.mkdir(parents=True, exist_ok=True)

COMMON_SCHEMAS = {
    "Problem": {
        "type": "object",
        "description": "RFC 9457 Problem Details",
        "required": ["type", "title", "status"],
        "properties": {
            "type": {"type": "string", "format": "uri"},
            "title": {"type": "string"},
            "status": {"type": "integer"},
            "detail": {"type": "string"},
            "instance": {"type": "string", "format": "uri"},
            "code": {"type": "string"},
            "invalid_params": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}, "reason": {"type": "string"}},
                },
            },
        },
    },
    "PageEnvelope": {
        "type": "object",
        "required": ["total", "page", "limit", "items"],
        "properties": {
            "total": {"type": "integer"},
            "page": {"type": "integer"},
            "limit": {"type": "integer"},
            "items": {"type": "array", "items": {"type": "object"}},
        },
    },
    "Money": {
        "type": "object",
        "required": ["amount", "currency"],
        "properties": {
            "amount": {"type": "number"},
            "currency": {"type": "string", "default": "BDT"},
        },
    },
    "AuditStamp": {
        "type": "object",
        "required": ["created_at", "created_by"],
        "properties": {
            "created_at": {"type": "string", "format": "date-time"},
            "created_by": {"type": "string"},
            "updated_at": {"type": "string", "format": "date-time"},
            "updated_by": {"type": "string"},
        },
    },
}

SECURITY_SCHEMES = {
    "OAuth2": {
        "type": "oauth2",
        "description": "OAuth 2.1 via Kong Gateway",
        "flows": {
            "clientCredentials": {
                "tokenUrl": "https://api.1000fix.com/v1/oauth/token",
                "scopes": {
                    "read": "Read access to domain resources",
                    "write": "Write access to domain resources",
                    "admin": "Administrative management",
                },
            }
        },
    },
    "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
}


def build_response(desc: str, schema_ref: str | None = None) -> dict:
    resp = {"description": desc}
    if schema_ref:
        resp["content"] = {
            "application/json": {"schema": {"$ref": f"#/components/schemas/{schema_ref}"}}
        }
    return resp


def get_standard_responses(success_ref: str | None = None, is_create: bool = False) -> dict:
    code = "201" if is_create else "200"
    return {
        code: build_response("Operation successful", success_ref),
        "400": build_response("Bad Request", "Problem"),
        "401": build_response("Unauthorized", "Problem"),
        "403": build_response("Forbidden", "Problem"),
        "404": build_response("Not Found", "Problem"),
        "422": build_response("Unprocessable Entity", "Problem"),
        "500": build_response("Internal Server Error", "Problem"),
    }


def make_spec(
    title: str,
    context_id: str,
    desc: str,
    modules: list[str],
    paths_data: dict,
    extra_schemas: dict,
) -> dict:
    schemas = dict(COMMON_SCHEMAS)
    schemas.update(extra_schemas)

    formatted_paths = {}
    for path, methods in paths_data.items():
        formatted_paths[path] = {}
        for method, op in methods.items():
            formatted_paths[path][method] = {
                "summary": op.get("summary", ""),
                "description": op.get("description", ""),
                "operationId": op.get("operationId"),
                "tags": op.get("tags", [context_id]),
                "x-owning-module": op.get("x-owning-module", modules[0]),
                "x-endpoint-class": op.get("x-endpoint-class", "standard-read"),
                "parameters": op.get("parameters", []),
                "responses": op.get(
                    "responses", get_standard_responses(op.get("response_schema"), method == "post")
                ),
            }
            if "request_schema" in op:
                formatted_paths[path][method]["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": f"#/components/schemas/{op['request_schema']}"}
                        }
                    },
                }

    spec = {
        "openapi": "3.1.0",
        "info": {
            "title": f"1000FiX ERP — {title} API",
            "version": "1.0.0",
            "description": f"{desc} Covers modules: {', '.join(modules)}. Bounded context: {context_id} (IN-002 §3.1).",
        },
        "servers": [{"url": "/", "description": "1000FiX Kong API Gateway"}],
        "paths": formatted_paths,
        "components": {"schemas": schemas, "securitySchemes": SECURITY_SCHEMES},
    }
    return spec


def define_service_delivery() -> dict:
    modules = ["M01", "M02", "M03", "M04", "M05", "M06", "M31"]
    extra_schemas = {
        "ServiceOrder": {
            "type": "object",
            "required": ["id", "order_number", "customer_id", "status"],
            "properties": {
                "id": {"type": "integer"},
                "order_number": {"type": "string"},
                "customer_id": {"type": "integer"},
                "device_brand": {"type": "string"},
                "device_model": {"type": "string"},
                "issue_description": {"type": "string"},
                "status": {
                    "type": "string",
                    "enum": [
                        "draft",
                        "confirmed",
                        "dispatched",
                        "in_repair",
                        "qc",
                        "delivered",
                        "invoiced",
                        "cancelled",
                    ],
                },
            },
        },
        "FieldServiceDispatch": {
            "type": "object",
            "required": ["order_id", "technician_id", "scheduled_slot"],
            "properties": {
                "order_id": {"type": "integer"},
                "technician_id": {"type": "integer"},
                "scheduled_slot": {"type": "string", "format": "date-time"},
            },
        },
        "WorkshopJob": {
            "type": "object",
            "required": ["id", "job_number", "bench_id", "stage"],
            "properties": {
                "id": {"type": "integer"},
                "job_number": {"type": "string"},
                "bench_id": {"type": "integer"},
                "stage": {"type": "string"},
            },
        },
        "Consignment": {
            "type": "object",
            "required": ["id", "consignment_number", "type", "courier_id"],
            "properties": {
                "id": {"type": "integer"},
                "consignment_number": {"type": "string"},
                "type": {"type": "string", "enum": ["inbound", "outbound"]},
                "courier_id": {"type": "integer"},
            },
        },
    }
    paths = {
        "/service-orders": {
            "get": {
                "operationId": "listServiceOrders",
                "summary": "List service orders",
                "x-owning-module": "M01",
                "response_schema": "PageEnvelope",
            },
            "post": {
                "operationId": "createServiceOrder",
                "summary": "Create service order",
                "x-owning-module": "M01",
                "request_schema": "ServiceOrder",
                "response_schema": "ServiceOrder",
            },
        },
        "/service-orders/{id}": {
            "get": {
                "operationId": "getServiceOrder",
                "summary": "Get service order details",
                "x-owning-module": "M01",
                "response_schema": "ServiceOrder",
            }
        },
        "/service-orders/{id}/dispatch": {
            "post": {
                "operationId": "dispatchFieldService",
                "summary": "Dispatch technician for field order",
                "x-owning-module": "M02",
                "request_schema": "FieldServiceDispatch",
                "response_schema": "ServiceOrder",
            }
        },
        "/workshop/jobs": {
            "get": {
                "operationId": "listWorkshopJobs",
                "summary": "List workshop repair jobs",
                "x-owning-module": "M03",
                "response_schema": "PageEnvelope",
            },
            "post": {
                "operationId": "createWorkshopJob",
                "summary": "Create workshop repair job",
                "x-owning-module": "M03",
                "request_schema": "WorkshopJob",
                "response_schema": "WorkshopJob",
            },
        },
        "/consignments": {
            "get": {
                "operationId": "listConsignments",
                "summary": "List logistics consignments",
                "x-owning-module": "M04",
                "response_schema": "PageEnvelope",
            },
            "post": {
                "operationId": "createConsignment",
                "summary": "Create logistics consignment",
                "x-owning-module": "M04",
                "request_schema": "Consignment",
                "response_schema": "Consignment",
            },
        },
        "/msp/contracts": {
            "get": {
                "operationId": "listMspContracts",
                "summary": "List MSP service delivery contracts",
                "x-owning-module": "M05",
                "response_schema": "PageEnvelope",
            }
        },
        "/warranty/claims": {
            "get": {
                "operationId": "listWarrantyClaims",
                "summary": "List warranty claims",
                "x-owning-module": "M06",
                "response_schema": "PageEnvelope",
            }
        },
        "/work-orders": {
            "get": {
                "operationId": "listWorkOrders",
                "summary": "List work orders",
                "x-owning-module": "M31",
                "response_schema": "PageEnvelope",
            }
        },
    }
    return make_spec(
        "Service Delivery",
        "service-delivery",
        "Service order lifecycle, field dispatch, workshop execution, logistics, and warranty.",
        modules,
        paths,
        extra_schemas,
    )


def define_customer_engagement() -> dict:
    modules = ["M07", "M10", "M27", "M32", "M33", "M34", "M35"]
    extra_schemas = {
        "CustomerLead": {
            "type": "object",
            "required": ["id", "name", "phone", "channel"],
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "phone": {"type": "string"},
                "channel": {"type": "string"},
            },
        },
        "ContactTranscript": {
            "type": "object",
            "required": ["id", "session_id", "channel", "messages"],
            "properties": {
                "id": {"type": "integer"},
                "session_id": {"type": "string"},
                "channel": {"type": "string"},
                "messages": {"type": "array", "items": {"type": "object"}},
            },
        },
        "AssistantIntent": {
            "type": "object",
            "required": ["intent_code", "utterance", "confidence"],
            "properties": {
                "intent_code": {"type": "string"},
                "utterance": {"type": "string"},
                "confidence": {"type": "number"},
            },
        },
        "PartyRecord": {
            "type": "object",
            "required": ["id", "party_type", "display_name"],
            "properties": {
                "id": {"type": "integer"},
                "party_type": {"type": "string"},
                "display_name": {"type": "string"},
                "nid_bin": {"type": "string"},
            },
        },
        "LoyaltyAccount": {
            "type": "object",
            "required": ["id", "customer_id", "balance_points", "tier"],
            "properties": {
                "id": {"type": "integer"},
                "customer_id": {"type": "integer"},
                "balance_points": {"type": "integer"},
                "tier": {"type": "string"},
            },
        },
    }
    paths = {
        "/crm/leads": {
            "get": {
                "operationId": "listCrmLeads",
                "summary": "List CRM leads",
                "x-owning-module": "M07",
                "response_schema": "PageEnvelope",
            },
            "post": {
                "operationId": "createCrmLead",
                "summary": "Create CRM lead",
                "x-owning-module": "M07",
                "request_schema": "CustomerLead",
                "response_schema": "CustomerLead",
            },
        },
        "/customer/billing-profiles": {
            "get": {
                "operationId": "listCustomerBillingProfiles",
                "summary": "List customer billing profiles",
                "x-owning-module": "M10",
                "response_schema": "PageEnvelope",
            }
        },
        "/contact-centre/transcripts": {
            "get": {
                "operationId": "listContactTranscripts",
                "summary": "List contact centre transcripts",
                "x-owning-module": "M27",
                "response_schema": "PageEnvelope",
            },
            "post": {
                "operationId": "recordContactTranscript",
                "summary": "Record contact transcript",
                "x-owning-module": "M27",
                "request_schema": "ContactTranscript",
                "response_schema": "ContactTranscript",
            },
        },
        "/assistant/intents": {
            "post": {
                "operationId": "matchAssistantIntent",
                "summary": "Match conversational intent",
                "x-owning-module": "M32",
                "request_schema": "AssistantIntent",
                "response_schema": "AssistantIntent",
            }
        },
        "/parties": {
            "get": {
                "operationId": "listParties",
                "summary": "List parties in master directory",
                "x-owning-module": "M33",
                "response_schema": "PageEnvelope",
            },
            "post": {
                "operationId": "createParty",
                "summary": "Create party master record",
                "x-owning-module": "M33",
                "request_schema": "PartyRecord",
                "response_schema": "PartyRecord",
            },
        },
        "/notifications/send": {
            "post": {
                "operationId": "dispatchNotification",
                "summary": "Dispatch customer notification",
                "x-owning-module": "M34",
                "request_schema": "PartyRecord",
                "response_schema": "PartyRecord",
            }
        },
        "/loyalty/accounts": {
            "get": {
                "operationId": "listLoyaltyAccounts",
                "summary": "List loyalty reward accounts",
                "x-owning-module": "M35",
                "response_schema": "PageEnvelope",
            }
        },
    }
    return make_spec(
        "Customer Engagement",
        "customer-engagement",
        "CRM, omnichannel contact transcripts, AI virtual assistant, party master, notifications, and loyalty.",
        modules,
        paths,
        extra_schemas,
    )


def define_commercial() -> dict:
    modules = ["M08", "M09", "M11", "M36", "M37", "M39", "M40"]
    extra_schemas = {
        "Quotation": {
            "type": "object",
            "required": ["id", "quotation_number", "customer_id", "total_amount"],
            "properties": {
                "id": {"type": "integer"},
                "quotation_number": {"type": "string"},
                "customer_id": {"type": "integer"},
                "total_amount": {"$ref": "#/components/schemas/Money"},
            },
        },
        "AmcContract": {
            "type": "object",
            "required": ["id", "contract_number", "client_id", "start_date", "end_date"],
            "properties": {
                "id": {"type": "integer"},
                "contract_number": {"type": "string"},
                "client_id": {"type": "integer"},
                "start_date": {"type": "string", "format": "date"},
                "end_date": {"type": "string", "format": "date"},
            },
        },
        "PriceRule": {
            "type": "object",
            "required": ["id", "sku", "base_price"],
            "properties": {
                "id": {"type": "integer"},
                "sku": {"type": "string"},
                "base_price": {"type": "number"},
            },
        },
    }
    paths = {
        "/quotations": {
            "get": {
                "operationId": "listQuotations",
                "summary": "List quotations",
                "x-owning-module": "M08",
                "response_schema": "PageEnvelope",
            },
            "post": {
                "operationId": "createQuotation",
                "summary": "Create quotation",
                "x-owning-module": "M08",
                "request_schema": "Quotation",
                "response_schema": "Quotation",
            },
        },
        "/amc-contracts": {
            "get": {
                "operationId": "listAmcContracts",
                "summary": "List AMC contracts",
                "x-owning-module": "M09",
                "response_schema": "PageEnvelope",
            },
            "post": {
                "operationId": "createAmcContract",
                "summary": "Create AMC contract",
                "x-owning-module": "M09",
                "request_schema": "AmcContract",
                "response_schema": "AmcContract",
            },
        },
        "/pricing/rules": {
            "get": {
                "operationId": "listPriceRules",
                "summary": "List pricing rules",
                "x-owning-module": "M11",
                "response_schema": "PageEnvelope",
            }
        },
        "/subscriptions": {
            "get": {
                "operationId": "listSubscriptions",
                "summary": "List active recurring subscriptions",
                "x-owning-module": "M36",
                "response_schema": "PageEnvelope",
            }
        },
        "/rate-cards": {
            "get": {
                "operationId": "listRateCards",
                "summary": "List standard rate cards",
                "x-owning-module": "M37",
                "response_schema": "PageEnvelope",
            }
        },
        "/b2b/consolidated-invoices": {
            "get": {
                "operationId": "listB2bInvoices",
                "summary": "List B2B consolidated invoices",
                "x-owning-module": "M39",
                "response_schema": "PageEnvelope",
            }
        },
        "/partners/rebates": {
            "get": {
                "operationId": "listPartnerRebates",
                "summary": "List partner rebates and referral commissions",
                "x-owning-module": "M40",
                "response_schema": "PageEnvelope",
            }
        },
    }
    return make_spec(
        "Commercial",
        "commercial",
        "Quotations, AMC contracts, pricing rules, subscriptions, rate cards, and partner rebates.",
        modules,
        paths,
        extra_schemas,
    )


def define_marketplace() -> dict:
    modules = ["M12", "M38"]
    extra_schemas = {
        "SellerListing": {
            "type": "object",
            "required": ["id", "seller_id", "title", "price"],
            "properties": {
                "id": {"type": "integer"},
                "seller_id": {"type": "integer"},
                "title": {"type": "string"},
                "price": {"$ref": "#/components/schemas/Money"},
            },
        },
        "MarketplaceOrder": {
            "type": "object",
            "required": ["id", "order_id", "buyer_id", "seller_id", "amount"],
            "properties": {
                "id": {"type": "integer"},
                "order_id": {"type": "string"},
                "buyer_id": {"type": "integer"},
                "seller_id": {"type": "integer"},
                "amount": {"$ref": "#/components/schemas/Money"},
            },
        },
        "SellerSettlement": {
            "type": "object",
            "required": ["id", "seller_id", "net_payout", "status"],
            "properties": {
                "id": {"type": "integer"},
                "seller_id": {"type": "integer"},
                "net_payout": {"$ref": "#/components/schemas/Money"},
                "status": {"type": "string"},
            },
        },
    }
    paths = {
        "/marketplace/listings": {
            "get": {
                "operationId": "listMarketplaceListings",
                "summary": "List marketplace items",
                "x-owning-module": "M12",
                "response_schema": "PageEnvelope",
            },
            "post": {
                "operationId": "createMarketplaceListing",
                "summary": "Create marketplace item",
                "x-owning-module": "M12",
                "request_schema": "SellerListing",
                "response_schema": "SellerListing",
            },
        },
        "/marketplace/orders": {
            "get": {
                "operationId": "listMarketplaceOrders",
                "summary": "List marketplace orders",
                "x-owning-module": "M12",
                "response_schema": "PageEnvelope",
            },
            "post": {
                "operationId": "createMarketplaceOrder",
                "summary": "Place marketplace order",
                "x-owning-module": "M12",
                "request_schema": "MarketplaceOrder",
                "response_schema": "MarketplaceOrder",
            },
        },
        "/marketplace/settlements": {
            "get": {
                "operationId": "listSellerSettlements",
                "summary": "List seller settlements",
                "x-owning-module": "M12",
                "response_schema": "PageEnvelope",
            }
        },
        "/storefront/catalog": {
            "get": {
                "operationId": "getStorefrontCatalog",
                "summary": "Get published storefront catalog",
                "x-owning-module": "M38",
                "response_schema": "PageEnvelope",
            }
        },
    }
    return make_spec(
        "Marketplace",
        "marketplace",
        "Marketplace sellers, listings, digital storefront catalog, orders, and settlements.",
        modules,
        paths,
        extra_schemas,
    )


def define_circular() -> dict:
    modules = ["M13", "M14", "M18", "M37"]
    extra_schemas = {
        "RentalAsset": {
            "type": "object",
            "required": ["id", "asset_tag", "daily_rate", "deposit"],
            "properties": {
                "id": {"type": "integer"},
                "asset_tag": {"type": "string"},
                "daily_rate": {"type": "number"},
                "deposit": {"type": "number"},
            },
        },
        "TradeInOffer": {
            "type": "object",
            "required": ["id", "imei", "device_condition", "estimated_value"],
            "properties": {
                "id": {"type": "integer"},
                "imei": {"type": "string"},
                "device_condition": {"type": "string"},
                "estimated_value": {"$ref": "#/components/schemas/Money"},
            },
        },
        "EWasteIntake": {
            "type": "object",
            "required": ["id", "intake_number", "weight_kg", "triage_class"],
            "properties": {
                "id": {"type": "integer"},
                "intake_number": {"type": "string"},
                "weight_kg": {"type": "number"},
                "triage_class": {"type": "string"},
            },
        },
        "DestructionCertificate": {
            "type": "object",
            "required": ["certificate_id", "intake_id", "wipe_status", "certified_by"],
            "properties": {
                "certificate_id": {"type": "string"},
                "intake_id": {"type": "integer"},
                "wipe_status": {"type": "string"},
                "certified_by": {"type": "string"},
            },
        },
    }
    paths = {
        "/rentals/reservations": {
            "get": {
                "operationId": "listRentalReservations",
                "summary": "List rental reservations",
                "x-owning-module": "M37",
                "response_schema": "PageEnvelope",
            },
            "post": {
                "operationId": "createRentalReservation",
                "summary": "Reserve rental device",
                "x-owning-module": "M37",
                "request_schema": "RentalAsset",
                "response_schema": "RentalAsset",
            },
        },
        "/trade-in/evaluations": {
            "get": {
                "operationId": "listTradeInEvaluations",
                "summary": "List trade-in valuations",
                "x-owning-module": "M14",
                "response_schema": "PageEnvelope",
            },
            "post": {
                "operationId": "createTradeInOffer",
                "summary": "Evaluate trade-in device",
                "x-owning-module": "M14",
                "request_schema": "TradeInOffer",
                "response_schema": "TradeInOffer",
            },
        },
        "/ewaste/collections": {
            "get": {
                "operationId": "listEWasteCollections",
                "summary": "List e-waste collections",
                "x-owning-module": "M18",
                "response_schema": "PageEnvelope",
            },
            "post": {
                "operationId": "createEWasteCollection",
                "summary": "Create e-waste collection intake",
                "x-owning-module": "M18",
                "request_schema": "EWasteIntake",
                "response_schema": "EWasteIntake",
            },
        },
        "/ewaste/certificates": {
            "get": {
                "operationId": "listDestructionCertificates",
                "summary": "List data destruction & recycling certificates",
                "x-owning-module": "M18",
                "response_schema": "PageEnvelope",
            },
            "post": {
                "operationId": "issueDestructionCertificate",
                "summary": "Issue data wipe & destruction certificate",
                "x-owning-module": "M18",
                "request_schema": "DestructionCertificate",
                "response_schema": "DestructionCertificate",
            },
        },
        "/data-recovery/cases": {
            "get": {
                "operationId": "listDataRecoveryCases",
                "summary": "List forensic data recovery cases",
                "x-owning-module": "M13",
                "response_schema": "PageEnvelope",
            }
        },
    }
    return make_spec(
        "Circular Economy",
        "circular",
        "Device rental, trade-in, refurbishment, forensic data recovery, and e-waste recycling.",
        modules,
        paths,
        extra_schemas,
    )


def define_supply_chain() -> dict:
    modules = ["M15", "M16", "M41", "M42", "M43", "M44"]
    extra_schemas = {
        "StockItem": {
            "type": "object",
            "required": ["id", "sku", "quantity_on_hand", "location_id"],
            "properties": {
                "id": {"type": "integer"},
                "sku": {"type": "string"},
                "quantity_on_hand": {"type": "number"},
                "location_id": {"type": "integer"},
            },
        },
        "PurchaseOrder": {
            "type": "object",
            "required": ["id", "po_number", "supplier_id", "total_amount"],
            "properties": {
                "id": {"type": "integer"},
                "po_number": {"type": "string"},
                "supplier_id": {"type": "integer"},
                "total_amount": {"$ref": "#/components/schemas/Money"},
            },
        },
        "SupplierScorecard": {
            "type": "object",
            "required": [
                "id",
                "supplier_id",
                "composite_score",
                "on_time_delivery_rate",
                "quality_pass_rate",
            ],
            "properties": {
                "id": {"type": "integer"},
                "supplier_id": {"type": "integer"},
                "composite_score": {"type": "number"},
                "on_time_delivery_rate": {"type": "number"},
                "quality_pass_rate": {"type": "number"},
            },
        },
    }
    paths = {
        "/stock/levels": {
            "get": {
                "operationId": "listStockLevels",
                "summary": "List warehouse inventory stock levels",
                "x-owning-module": "M15",
                "response_schema": "PageEnvelope",
            }
        },
        "/purchasing/orders": {
            "get": {
                "operationId": "listPurchaseOrders",
                "summary": "List procurement purchase orders",
                "x-owning-module": "M16",
                "response_schema": "PageEnvelope",
            },
            "post": {
                "operationId": "createPurchaseOrder",
                "summary": "Create purchase order",
                "x-owning-module": "M16",
                "request_schema": "PurchaseOrder",
                "response_schema": "PurchaseOrder",
            },
        },
        "/warehouses": {
            "get": {
                "operationId": "listWarehouses",
                "summary": "List warehouse locations",
                "x-owning-module": "M41",
                "response_schema": "PageEnvelope",
            }
        },
        "/suppliers/scorecards": {
            "get": {
                "operationId": "listSupplierScorecards",
                "summary": "List supplier performance scorecards",
                "x-owning-module": "M42",
                "response_schema": "PageEnvelope",
            }
        },
        "/material/requisitions": {
            "get": {
                "operationId": "listMaterialRequisitions",
                "summary": "List material requisitions",
                "x-owning-module": "M43",
                "response_schema": "PageEnvelope",
            }
        },
        "/imports/shipments": {
            "get": {
                "operationId": "listImportShipments",
                "summary": "List customs import shipments",
                "x-owning-module": "M44",
                "response_schema": "PageEnvelope",
            }
        },
    }
    return make_spec(
        "Supply Chain",
        "supply-chain",
        "Inventory WMS, procurement POs, warehouse hierarchy, supplier ratings, and imports.",
        modules,
        paths,
        extra_schemas,
    )


def define_asset() -> dict:
    modules = ["M17", "M45", "M46", "M47", "M48"]
    extra_schemas = {
        "CustomerEquipment": {
            "type": "object",
            "required": ["id", "serial_number", "customer_id", "brand", "model"],
            "properties": {
                "id": {"type": "integer"},
                "serial_number": {"type": "string"},
                "customer_id": {"type": "integer"},
                "brand": {"type": "string"},
                "model": {"type": "string"},
            },
        },
        "FixedAsset": {
            "type": "object",
            "required": ["id", "asset_tag", "category", "capital_cost"],
            "properties": {
                "id": {"type": "integer"},
                "asset_tag": {"type": "string"},
                "category": {"type": "string"},
                "capital_cost": {"$ref": "#/components/schemas/Money"},
            },
        },
        "FleetVehicle": {
            "type": "object",
            "required": ["id", "registration_no", "type", "driver_id"],
            "properties": {
                "id": {"type": "integer"},
                "registration_no": {"type": "string"},
                "type": {"type": "string"},
                "driver_id": {"type": "integer"},
            },
        },
        "IotTelemetry": {
            "type": "object",
            "required": ["device_id", "temperature", "vibration", "timestamp"],
            "properties": {
                "device_id": {"type": "string"},
                "temperature": {"type": "number"},
                "vibration": {"type": "number"},
                "timestamp": {"type": "string", "format": "date-time"},
            },
        },
    }
    paths = {
        "/customer-assets": {
            "get": {
                "operationId": "listCustomerAssets",
                "summary": "List customer registered devices",
                "x-owning-module": "M17",
                "response_schema": "PageEnvelope",
            },
            "post": {
                "operationId": "registerCustomerAsset",
                "summary": "Register customer device",
                "x-owning-module": "M17",
                "request_schema": "CustomerEquipment",
                "response_schema": "CustomerEquipment",
            },
        },
        "/fixed-assets": {
            "get": {
                "operationId": "listFixedAssets",
                "summary": "List enterprise capital fixed assets",
                "x-owning-module": "M45",
                "response_schema": "PageEnvelope",
            }
        },
        "/fleet/vehicles": {
            "get": {
                "operationId": "listFleetVehicles",
                "summary": "List logistics vehicles",
                "x-owning-module": "M46",
                "response_schema": "PageEnvelope",
            }
        },
        "/facilities": {
            "get": {
                "operationId": "listFacilities",
                "summary": "List service branch facilities",
                "x-owning-module": "M47",
                "response_schema": "PageEnvelope",
            }
        },
        "/iot/telemetry": {
            "post": {
                "operationId": "recordIotTelemetry",
                "summary": "Ingest IoT equipment telemetry",
                "x-owning-module": "M48",
                "request_schema": "IotTelemetry",
                "response_schema": "IotTelemetry",
            }
        },
    }
    return make_spec(
        "Asset Management",
        "asset",
        "Customer devices, capital assets, fleet vehicles, branch facilities, and IoT telemetry.",
        modules,
        paths,
        extra_schemas,
    )


def define_finance() -> dict:
    modules = ["M19", "M20", "M49", "M50", "M51", "M52", "M53", "M54"]
    extra_schemas = {
        "Invoice": {
            "type": "object",
            "required": ["id", "invoice_number", "customer_id", "total_amount", "vat_amount"],
            "properties": {
                "id": {"type": "integer"},
                "invoice_number": {"type": "string"},
                "customer_id": {"type": "integer"},
                "total_amount": {"$ref": "#/components/schemas/Money"},
                "vat_amount": {"$ref": "#/components/schemas/Money"},
            },
        },
        "PaymentConfirmation": {
            "type": "object",
            "required": ["payment_reference", "invoice_id", "channel", "amount"],
            "properties": {
                "payment_reference": {"type": "string"},
                "invoice_id": {"type": "integer"},
                "channel": {
                    "type": "string",
                    "enum": ["bkash", "nagad", "sslcommerz", "beftn", "cash"],
                },
                "amount": {"$ref": "#/components/schemas/Money"},
            },
        },
        "MushakFiling": {
            "type": "object",
            "required": ["tax_period", "total_sales", "vat_payable", "status"],
            "properties": {
                "tax_period": {"type": "string"},
                "total_sales": {"$ref": "#/components/schemas/Money"},
                "vat_payable": {"$ref": "#/components/schemas/Money"},
                "status": {"type": "string"},
            },
        },
    }
    paths = {
        "/finance/general-ledger": {
            "get": {
                "operationId": "listLedgerEntries",
                "summary": "List general ledger entries",
                "x-owning-module": "M19",
                "response_schema": "PageEnvelope",
            }
        },
        "/finance/invoices": {
            "get": {
                "operationId": "listFinanceInvoices",
                "summary": "List invoices",
                "x-owning-module": "M20",
                "response_schema": "PageEnvelope",
            },
            "post": {
                "operationId": "createFinanceInvoice",
                "summary": "Create accounts receivable invoice",
                "x-owning-module": "M20",
                "request_schema": "Invoice",
                "response_schema": "Invoice",
            },
        },
        "/finance/payments": {
            "post": {
                "operationId": "confirmPayment",
                "summary": "Confirm payment receipt",
                "x-owning-module": "M50",
                "request_schema": "PaymentConfirmation",
                "response_schema": "PaymentConfirmation",
            }
        },
        "/finance/treasury/positions": {
            "get": {
                "operationId": "getTreasuryPosition",
                "summary": "Get cash and bank balances",
                "x-owning-module": "M49",
                "response_schema": "PageEnvelope",
            }
        },
        "/finance/vat/mushak-9-1": {
            "get": {
                "operationId": "getMushakFiling",
                "summary": "Get monthly Mushak 9.1 VAT return summary",
                "x-owning-module": "M51",
                "response_schema": "MushakFiling",
            }
        },
        "/finance/ap/three-way-match": {
            "get": {
                "operationId": "getThreeWayMatchStatus",
                "summary": "Get PO-GRN-Invoice three way match status",
                "x-owning-module": "M52",
                "response_schema": "PageEnvelope",
            }
        },
        "/finance/budget/fpa": {
            "get": {
                "operationId": "getFpaBudgetVariance",
                "summary": "Get financial budget vs actual variance",
                "x-owning-module": "M53",
                "response_schema": "PageEnvelope",
            }
        },
        "/finance/intercompany/transactions": {
            "get": {
                "operationId": "listIntercompanyTransactions",
                "summary": "List multi-entity intercompany eliminations",
                "x-owning-module": "M54",
                "response_schema": "PageEnvelope",
            }
        },
    }
    return make_spec(
        "Finance & Accounting",
        "finance",
        "General ledger, invoicing, treasury, statutory tax (Mushak 9.1), AP matching, and intercompany.",
        modules,
        paths,
        extra_schemas,
    )


def define_people() -> dict:
    modules = ["M21", "M22", "M55", "M56", "M57", "M58", "M59"]
    extra_schemas = {
        "Employee": {
            "type": "object",
            "required": ["id", "employee_id", "name", "department", "designation"],
            "properties": {
                "id": {"type": "integer"},
                "employee_id": {"type": "string"},
                "name": {"type": "string"},
                "department": {"type": "string"},
                "designation": {"type": "string"},
            },
        },
        "PayrollBatch": {
            "type": "object",
            "required": ["period_id", "total_gross", "total_net", "beftn_status"],
            "properties": {
                "period_id": {"type": "string"},
                "total_gross": {"$ref": "#/components/schemas/Money"},
                "total_net": {"$ref": "#/components/schemas/Money"},
                "beftn_status": {"type": "string"},
            },
        },
        "AttendanceRecord": {
            "type": "object",
            "required": ["employee_id", "timestamp", "device_type"],
            "properties": {
                "employee_id": {"type": "integer"},
                "timestamp": {"type": "string", "format": "date-time"},
                "device_type": {"type": "string"},
            },
        },
    }
    paths = {
        "/hr/employees": {
            "get": {
                "operationId": "listEmployees",
                "summary": "List employees in master directory",
                "x-owning-module": "M21",
                "response_schema": "PageEnvelope",
            },
            "post": {
                "operationId": "createEmployee",
                "summary": "Create employee record",
                "x-owning-module": "M21",
                "request_schema": "Employee",
                "response_schema": "Employee",
            },
        },
        "/hr/recruitment/jobs": {
            "get": {
                "operationId": "listJobOpenings",
                "summary": "List talent job openings",
                "x-owning-module": "M22",
                "response_schema": "PageEnvelope",
            }
        },
        "/hr/attendance/logs": {
            "post": {
                "operationId": "recordAttendance",
                "summary": "Log biometric/mobile attendance",
                "x-owning-module": "M55",
                "request_schema": "AttendanceRecord",
                "response_schema": "AttendanceRecord",
            }
        },
        "/hr/payroll/batches": {
            "get": {
                "operationId": "listPayrollBatches",
                "summary": "List monthly payroll batches",
                "x-owning-module": "M56",
                "response_schema": "PageEnvelope",
            }
        },
        "/hr/performance/reviews": {
            "get": {
                "operationId": "listPerformanceReviews",
                "summary": "List employee performance evaluations",
                "x-owning-module": "M57",
                "response_schema": "PageEnvelope",
            }
        },
        "/hr/competency/skills": {
            "get": {
                "operationId": "listCompetencies",
                "summary": "List employee technical certifications",
                "x-owning-module": "M58",
                "response_schema": "PageEnvelope",
            }
        },
        "/hr/hse/incidents": {
            "get": {
                "operationId": "listHseIncidents",
                "summary": "List workplace health and safety incidents",
                "x-owning-module": "M59",
                "response_schema": "PageEnvelope",
            }
        },
    }
    return make_spec(
        "People & Human Resources",
        "people",
        "Employee master, recruitment, attendance, statutory payroll (BEFTN), competency, and safety.",
        modules,
        paths,
        extra_schemas,
    )


def define_governance() -> dict:
    modules = ["M23", "M24", "M60", "M61", "M66", "M67"]
    extra_schemas = {
        "NcrRecord": {
            "type": "object",
            "required": ["id", "ncr_number", "severity", "source"],
            "properties": {
                "id": {"type": "integer"},
                "ncr_number": {"type": "string"},
                "severity": {"type": "string", "enum": ["minor", "major", "critical"]},
                "source": {"type": "string"},
            },
        },
        "CapaAction": {
            "type": "object",
            "required": ["id", "ncr_id", "root_cause", "action_plan", "status"],
            "properties": {
                "id": {"type": "integer"},
                "ncr_id": {"type": "integer"},
                "root_cause": {"type": "string"},
                "action_plan": {"type": "string"},
                "status": {"type": "string"},
            },
        },
        "DocumentVaultItem": {
            "type": "object",
            "required": ["id", "doc_name", "hash_sha256", "signature_status"],
            "properties": {
                "id": {"type": "integer"},
                "doc_name": {"type": "string"},
                "hash_sha256": {"type": "string"},
                "signature_status": {"type": "string"},
            },
        },
    }
    paths = {
        "/qms/ncr": {
            "get": {
                "operationId": "listNonConformanceRecords",
                "summary": "List QMS non-conformance records (NCR)",
                "x-owning-module": "M23",
                "response_schema": "PageEnvelope",
            },
            "post": {
                "operationId": "createNcrRecord",
                "summary": "Raise non-conformance record",
                "x-owning-module": "M23",
                "request_schema": "NcrRecord",
                "response_schema": "NcrRecord",
            },
        },
        "/qms/capa": {
            "get": {
                "operationId": "listCapaActions",
                "summary": "List corrective & preventive actions (CAPA)",
                "x-owning-module": "M23",
                "response_schema": "PageEnvelope",
            },
            "post": {
                "operationId": "createCapaAction",
                "summary": "Create CAPA action",
                "x-owning-module": "M23",
                "request_schema": "CapaAction",
                "response_schema": "CapaAction",
            },
        },
        "/grc/audits": {
            "get": {
                "operationId": "listGrcAudits",
                "summary": "List internal ISO compliance audits",
                "x-owning-module": "M24",
                "response_schema": "PageEnvelope",
            }
        },
        "/documents/vault": {
            "get": {
                "operationId": "listVaultDocuments",
                "summary": "List secure document vault records",
                "x-owning-module": "M60",
                "response_schema": "PageEnvelope",
            },
            "post": {
                "operationId": "storeVaultDocument",
                "summary": "Store signed document",
                "x-owning-module": "M60",
                "request_schema": "DocumentVaultItem",
                "response_schema": "DocumentVaultItem",
            },
        },
        "/projects/portfolios": {
            "get": {
                "operationId": "listProjectPortfolios",
                "summary": "List project portfolios",
                "x-owning-module": "M61",
                "response_schema": "PageEnvelope",
            }
        },
        "/legal/contracts": {
            "get": {
                "operationId": "listLegalContracts",
                "summary": "List enterprise legal contracts",
                "x-owning-module": "M67",
                "response_schema": "PageEnvelope",
            }
        },
    }
    return make_spec(
        "Governance, Risk & Compliance",
        "governance",
        "QMS ISO 9001:2015, NCR/CAPA, internal audits, document vault e-signing, and legal contracts.",
        modules,
        paths,
        extra_schemas,
    )


def define_platform() -> dict:
    modules = ["M25", "M26", "M28", "M29", "M30", "M62", "M63", "M64", "M65"]
    extra_schemas = {
        "MetricDefinition": {
            "type": "object",
            "required": ["code", "name", "calculation_formula", "cadence"],
            "properties": {
                "code": {"type": "string"},
                "name": {"type": "string"},
                "calculation_formula": {"type": "string"},
                "cadence": {"type": "string"},
            },
        },
        "MlPredictionRequest": {
            "type": "object",
            "required": ["model_id", "features"],
            "properties": {"model_id": {"type": "string"}, "features": {"type": "object"}},
        },
        "MultiEntityRule": {
            "type": "object",
            "required": ["rule_code", "primary_entity_id", "consolidation_type"],
            "properties": {
                "rule_code": {"type": "string"},
                "primary_entity_id": {"type": "integer"},
                "consolidation_type": {"type": "string"},
            },
        },
    }
    paths = {
        "/analytics/metrics": {
            "get": {
                "operationId": "listPlatformMetrics",
                "summary": "List BI & reporting canonical metrics",
                "x-owning-module": "M25",
                "response_schema": "PageEnvelope",
            }
        },
        "/ai/predict": {
            "post": {
                "operationId": "predictMlInference",
                "summary": "Execute ML model inference",
                "x-owning-module": "M26",
                "request_schema": "MlPredictionRequest",
                "response_schema": "MlPredictionRequest",
            }
        },
        "/gateway/routes": {
            "get": {
                "operationId": "listGatewayRoutes",
                "summary": "List Kong API gateway routes",
                "x-owning-module": "M28",
                "response_schema": "PageEnvelope",
            }
        },
        "/events/outbox/status": {
            "get": {
                "operationId": "getEventOutboxStatus",
                "summary": "Get event mesh outbox health status",
                "x-owning-module": "M29",
                "response_schema": "PageEnvelope",
            }
        },
        "/tenancy/entities": {
            "get": {
                "operationId": "listTenancyEntities",
                "summary": "List operating company entities",
                "x-owning-module": "M30",
                "response_schema": "PageEnvelope",
            }
        },
        "/workflow/executions": {
            "get": {
                "operationId": "listWorkflowExecutions",
                "summary": "List workflow state engine executions",
                "x-owning-module": "M62",
                "response_schema": "PageEnvelope",
            }
        },
        "/trust/keys/rotate": {
            "post": {
                "operationId": "rotateTrustKeys",
                "summary": "Trigger encryption key rotation",
                "x-owning-module": "M63",
                "response_schema": "PageEnvelope",
            }
        },
        "/telemetry/health": {
            "get": {
                "operationId": "getTelemetryHealth",
                "summary": "Get system telemetry and observability health",
                "x-owning-module": "M64",
                "response_schema": "PageEnvelope",
            }
        },
        "/multi-entity/consolidation": {
            "get": {
                "operationId": "listConsolidationRules",
                "summary": "List multi-entity consolidation rules",
                "x-owning-module": "M65",
                "response_schema": "PageEnvelope",
            }
        },
    }
    return make_spec(
        "Platform & Architecture",
        "platform",
        "BI metrics, ML model gateway, event outbox, tenancy, workflow engine, trust, and multi-entity consolidation.",
        modules,
        paths,
        extra_schemas,
    )


def main() -> int:
    context_defs = [
        ("service-delivery.json", define_service_delivery()),
        ("customer-engagement.json", define_customer_engagement()),
        ("commercial.json", define_commercial()),
        ("marketplace.json", define_marketplace()),
        ("circular.json", define_circular()),
        ("supply-chain.json", define_supply_chain()),
        ("asset.json", define_asset()),
        ("finance.json", define_finance()),
        ("people.json", define_people()),
        ("governance.json", define_governance()),
        ("platform.json", define_platform()),
    ]

    total_ops = 0
    for filename, spec in context_defs:
        target = OPENAPI_DIR / filename
        target.write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")
        ops_count = sum(len(methods) for methods in spec["paths"].values())
        total_ops += ops_count
        print(f"Generated {filename}: {len(spec['paths'])} paths, {ops_count} operations")

    print(f"\nTotal OpenAPI 3.1 bounded context specifications: {len(context_defs)}")
    print(f"Total operations generated across all 11 bounded contexts: {total_ops}")
    return 0


if __name__ == "__main__":
    main()
