app_name = "flow"
app_title = "Flow"
app_publisher = "Shrihari Mahabal"
app_description = "Frappe Flow — native AI agents, tools, and triggers for Frappe"
app_email = "shriharimahabal08@gmail.com"
app_license = "agpl-3.0"

export_python_type_annotations = True

# Vite-built (frontend/) AI panel bundle. Served directly from public/ — the
# /assets path bypasses the desk's esbuild pipeline. Run `yarn build` in frontend/.
# /assets URLs get no cache-busting query from Frappe, so append ?v=<mtime>:
# the stable filename keeps the hook simple while a rebuild invalidates the cache.
import os as _os


def _flow_panel_asset(filename: str) -> str:
	path = _os.path.join(_os.path.dirname(__file__), "public", "flow_panel", filename)
	try:
		version = int(_os.path.getmtime(path))
	except OSError:
		version = 0
	return f"/assets/flow/flow_panel/{filename}?v={version}"


app_include_js = [_flow_panel_asset("flow_panel.js")]
app_include_css = [_flow_panel_asset("flow_panel.css")]

doc_events = {
	"*": {
		"after_insert": "flow.triggers.dispatch",
		"on_update": "flow.triggers.dispatch",
		"on_submit": "flow.triggers.dispatch",
		"on_cancel": "flow.triggers.dispatch",
		"on_trash": "flow.triggers.dispatch",
	}
}

# Flow's references to other docs are bookkeeping — they must never block deleting
# the referenced doc. A knowledge chunk indexes a doc; a Flow Run records the doc a
# trigger acted on. The incremental sweep removes orphaned chunks afterwards.
# A session's Flow Model reference is historical bookkeeping and must not block deletion.
ignore_links_on_delete = ["Flow Knowledge Chunk", "Flow Run", "Flow Session"]

default_log_clearing_doctypes = {
	"Flow Session": 90,
}

scheduler_events = {
	"daily": [
		"flow.knowledge.ingest.sync_due_sources",
	],
	"cron": {
		"*/5 * * * *": [
			"flow.triggers.dispatch_scheduled",
		],
	},
}

after_migrate = ["flow.assistant.sync_builtin_assistant"]

extend_bootinfo = "flow.boot.boot_session"

# Site-specific agent customizations (HR Helpdesk Agent, Onboarding Agent, Offboarding
# Agent, Attendance Agent, Payroll Agent, Resume Shortlisting Agent, and their supporting
# tools/webforms/templates/master lists — including the India payroll framework: Salary
# Component, Income Tax Slab, Salary Structure, the Company custom fields the
# HRA-exemption formula reads, and the Job Applicant custom fields (match_score,
# extracted_skills, screening_summary) the Resume Shortlisting Agent writes to)
# exported as data so they can be version controlled and replayed onto another site via
# `bench --site <site> import-fixtures`. The "Onboarding Document" and "Asset Return
# Activity" doctypes themselves ship as real app code instead (module="Flow", custom=0 —
# see flow/flow/doctype/onboarding_document and flow/flow/doctype/asset_return_activity)
# since `export-fixtures` refuses to fixture the "DocType" doctype itself. The Employee
# Separation.asset_return_activity Table field that uses it, however, IS a Custom Field
# and travels as a fixture below.
# Excludes: Flow Model/Flow Provider (hold encrypted, site-specific API credentials —
# never belong in a git-committed fixture), the system-generated "Flow" agent/builtin
# tools (recreated automatically by after_migrate, not data to replay), Flow Knowledge
# Base/Source/Chunk (reference uploaded files and derived vector embeddings that don't
# travel with a fixture export — rebuild via re-ingestion on the target site), and
# per-employee/per-year/per-company instance data (Leave Allocation, Employee.
# leave_approver, Holiday List Assignment, Payroll Period, and the Company records'
# own basic_component/hra_component/default_payroll_payable_account values) — real
# setup for THIS site's employees/companies/year, not portable "code" to replay onto a
# different site's different employees. The Income Tax Slab rates are representative
# figures for a working demo — verify against the current Finance Act before any real
# payroll run.
fixtures = [
	{"dt": "Identification Document Type"},
	{"dt": "Leave Type", "filters": [["name", "in", ["Casual Leave", "Sick Leave", "Earned Leave", "Leave Without Pay"]]]},
	{"dt": "Salary Component"},
	{"dt": "Income Tax Slab", "filters": [["name", "in", ["Old Regime FY 2026-27", "New Regime FY 2026-27"]]]},
	{"dt": "Salary Structure", "filters": [["name", "=", "Standard - Monthly"]]},
	{
		"dt": "Custom Field",
		"filters": [
			["dt", "in", ["Employee Onboarding", "Job Offer", "Company", "Job Applicant", "Employee Separation", "Employee"]],
			["fieldname", "in", [
				"gender", "date_of_birth", "date_of_joining",
				"hra_section", "basic_component", "hra_component", "hra_column_break", "arrear_component",
				"match_score", "extracted_skills", "screening_summary",
				"asset_return_activity",
				"start_offboarding",
			]],
		],
	},
	{"dt": "Email Template", "filters": [["name", "in", ["Onboarding Welcome", "Offboarding Notice", "Leave Decision"]]]},
	{"dt": "Web Form", "filters": [["name", "in", ["onboarding-documents"]]]},
	{"dt": "Client Script", "filters": [["name", "=", "Employee Exit - Start Offboarding"]]},
	{"dt": "Flow Tool", "filters": [["is_system_generated", "=", 0]]},
	{"dt": "Flow Agent", "filters": [["is_system_generated", "=", 0]]},
	{"dt": "Flow Trigger"},
]
