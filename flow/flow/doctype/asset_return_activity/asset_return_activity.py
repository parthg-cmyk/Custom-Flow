# Copyright (c) 2026, Shrihari Mahabal and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AssetReturnActivity(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		asset_name: DF.Data
		asset_type: DF.Literal["Laptop", "Mobile Phone", "ID Card", "Access Card", "SIM Card", "Other"]
		linked_asset: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		remarks: DF.SmallText | None
		returned_on: DF.Date | None
		status: DF.Literal["Issued", "Returned", "Lost"]
	# end: auto-generated types

	pass