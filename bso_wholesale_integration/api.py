import hashlib
import hmac
import json
import time
from zoneinfo import ZoneInfo

import frappe
from frappe import _
from frappe.utils import get_datetime


MAX_CLOCK_SKEW_SECONDS = 300


def _clean(value, maximum):
    if value is None:
        return ""
    return str(value).strip()[:maximum]


def _database_datetime(value):
    """Return a timezone-naive datetime suitable for a Frappe/MariaDB Datetime field."""
    if not value:
        return frappe.utils.now_datetime()

    parsed = get_datetime(value)
    if parsed.tzinfo is None:
        return parsed

    site_timezone = frappe.get_system_settings("time_zone") or "UTC"
    try:
        return parsed.astimezone(ZoneInfo(site_timezone)).replace(tzinfo=None)
    except (KeyError, ValueError):
        return parsed.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)


def _verify_request(raw_body):
    secret = frappe.conf.get("bso_wholesale_secret")
    if not secret or len(str(secret)) < 32:
        frappe.throw(_("Wholesale integration secret is not configured securely."), frappe.AuthenticationError)

    timestamp = frappe.get_request_header("X-BSO-Timestamp") or ""
    signature = frappe.get_request_header("X-BSO-Signature") or ""
    try:
        request_time = int(timestamp)
    except (TypeError, ValueError):
        frappe.throw(_("Invalid request timestamp."), frappe.AuthenticationError)

    if abs(int(time.time()) - request_time) > MAX_CLOCK_SKEW_SECONDS:
        frappe.throw(_("Expired request timestamp."), frappe.AuthenticationError)

    expected = hmac.new(
        str(secret).encode("utf-8"),
        timestamp.encode("utf-8") + b"." + raw_body,
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, signature):
        frappe.throw(_("Invalid request signature."), frappe.AuthenticationError)


@frappe.whitelist(allow_guest=True, methods=["POST"])
def receive_wholesale_lead():
    raw_body = frappe.request.get_data(cache=True)
    _verify_request(raw_body)

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        frappe.throw(_("The request body must be valid JSON."), frappe.ValidationError)

    source_id = _clean(payload.get("source_id"), 140)
    business = _clean(payload.get("business_name"), 140)
    contact = _clean(payload.get("contact_person"), 140)
    phone = _clean(payload.get("phone"), 40)
    email = _clean(payload.get("email"), 140)
    city = _clean(payload.get("city"), 140)
    products = _clean(payload.get("products_interested_in"), 5000)
    source_url = _clean(payload.get("source_url"), 500)
    submitted_at = _clean(payload.get("submitted_at"), 64)

    if not source_id or not business or not contact or not phone:
        frappe.throw(_("source_id, business_name, contact_person and phone are required."), frappe.ValidationError)

    existing = frappe.db.get_value("Lead", {"custom_bso_source_id": source_id}, "name")
    if existing:
        lead = frappe.get_doc("Lead", existing)
        created = False
    else:
        lead = frappe.new_doc("Lead")
        lead.custom_bso_source_id = source_id
        lead.status = "Lead"
        lead.type = "Client"
        lead.request_type = "Product Enquiry"
        created = True

    lead.company_name = business
    lead.first_name = contact
    lead.mobile_no = phone
    lead.whatsapp_no = phone
    lead.email_id = email or None
    lead.city = city
    lead.custom_bso_products_interested_in = products
    lead.custom_bso_source_url = source_url
    lead.custom_bso_submitted_at = _database_datetime(submitted_at)
    lead.flags.ignore_permissions = True
    lead.save()

    frappe.db.commit()
    return {"ok": True, "lead": lead.name, "created": created}
