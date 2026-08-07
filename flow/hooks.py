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

# Site-specific agent customizations (HR Helpdesk Agent, Onboarding Agent, and their
# supporting tool/webform/template) exported as data so they can be version controlled
# and replayed onto another site via `bench --site <site> import-fixtures`. The
# "Onboarding Document" doctype itself ships as real app code instead (converted from
# a Custom DocType to module="Flow", custom=0 — see flow/flow/doctype/onboarding_document)
# since `export-fixtures` refuses to fixture the "DocType" doctype itself.
# Excludes: Flow Model/Flow Provider (hold encrypted, site-specific API credentials —
# never belong in a git-committed fixture), the system-generated "Flow" agent/builtin
# tools (recreated automatically by after_migrate, not data to replay), and Flow
# Knowledge Base/Source/Chunk (reference uploaded files and derived vector embeddings
# that don't travel with a fixture export — rebuild via re-ingestion on the target site).
fixtures = [
	{"dt": "Identification Document Type"},
	{
		"dt": "Custom Field",
		"filters": [["dt", "=", "Employee Onboarding"], ["fieldname", "in", ["gender", "date_of_birth"]]],
	},
	{"dt": "Email Template", "filters": [["name", "=", "Onboarding Welcome"]]},
	{"dt": "Web Form", "filters": [["name", "=", "onboarding-documents"]]},
	{"dt": "Flow Tool", "filters": [["is_system_generated", "=", 0]]},
	{"dt": "Flow Agent", "filters": [["is_system_generated", "=", 0]]},
	{"dt": "Flow Trigger"},
]
