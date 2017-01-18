from __future__ import unicode_literals

import json
import traceback
import frappe

from frappe import _
from frappe.utils import cint
from erpnext.shopping_cart import cart

from . import dbug

@frappe.whitelist(xss_safe=True)
def stored_payments(start=0, limit=5, action="query", payment_id=None):
	
	if action == "query":
		return fetch_stored_payments(start, limit)

	if action == "remove":
		return delete_stored_payment(payment_id)

def fetch_stored_payments(start, limit):

	result = {
		"success": True,
		"data": [],
		"total": 0
	}

	return result

def delete_stored_payment(payment_id):

	result = {
		"msg": "Not Implemented",
		"success": False
	}

	return result

@frappe.whitelist(xss_safe=True)
def addresses(start=0, limit=5, action="query", address_id=None):
	if action == "query":
		return fetch_addresses(start, limit, "is_primary_address DESC, is_shipping_address DESC, address_type DESC")
	
	if action == "remove":
		return delete_address(address_id)

def delete_address(address_id):

	result = {
		"success": False,
		"msg": "",
	}

	if not address_id:
		result['success'] = False
		result['msg'] = 'Missing address_id'
		return result

	session_user = frappe.get_user()
	user = frappe.get_doc("User", session_user.name)
	
	if user and user.email[-12:] == "@guest.local":
		return []
	
	quotation = cart.get_cart_quotation()["doc"]
	customer = frappe.get_doc("Customer", quotation.customer)

	address = frappe.get_doc("Address", address_id)

	# sanity check to make sure we only delete addresses which belong
	# to the customer in session
	if address and address.customer == customer.name:
		frappe.delete_doc("Address", address_id, ignore_permissions=True)
		result["success"] = True
	else:
		result["msg"] = "Address Not Found"

	return result

def fetch_addresses(start, limit, order_by):
	result = {
		"success": False
	}

	try:
		session_user = frappe.get_user()
		user = frappe.get_doc("User", session_user.name)
		
		if user and user.email[-12:] == "@guest.local":
			return []

		quotation = cart.get_cart_quotation()["doc"]
		customer = frappe.get_doc("Customer", quotation.customer)

		count_query = frappe.db.sql("SELECT COUNT(*) FROM tabAddress where customer='{}'".format(customer.name), as_list=1)[0][0];

		addresses = frappe.get_list("Address", 
			fields=["address_title", "address_type", "address_line1", "address_line2", "city", "country", "state", "county", "pincode", "is_primary_address", "is_shipping_address", "name"], 
			filters={"customer": customer.name},
			order_by=order_by,
			limit_start=start,
			limit=limit, ignore_permissions=True)

		result['data'] = addresses
		result['total'] = cint(count_query)
	except Exception as ex:
		result['exception'] = traceback.format_exc()
		result['success'] = False

	return result
