# Copyright (c) 2026, Frappe Technologies and contributors
# License: MIT. See LICENSE

"""Site-specific Flow Tools implemented as real Python (Imported type), for logic that needs
more than the Script sandbox (frappe.utils.safe_exec) allows — e.g. a real import statement."""

from __future__ import annotations

import frappe

from flow.knowledge.extract import extract_file
from flow.lib.tool import tool


@tool
def extract_resume_text(job_applicant: str) -> dict:
	"""Extracts plain text from a Job Applicant's resume_attachment file (PDF, DOCX, scanned
	image, etc — with OCR fallback for scans), using Flow's own knowledge-extraction pipeline.
	Returns an 'error' key ('no_resume_attachment' or 'no_extractable_text') instead of throwing
	when there's nothing to read — if 'no_resume_attachment', resume_link is returned for
	reference only, since this tool cannot fetch an external URL. Never guess or infer resume
	content when this returns an error; say so plainly instead."""
	doc = frappe.get_doc("Job Applicant", job_applicant)
	if not doc.resume_attachment:
		return {
			"job_applicant": job_applicant,
			"error": "no_resume_attachment",
			"resume_link": doc.resume_link,
		}

	file_doc = frappe.get_doc("File", {"file_url": doc.resume_attachment})
	text = extract_file(file_doc)
	if not text.strip():
		return {"job_applicant": job_applicant, "error": "no_extractable_text"}

	return {"job_applicant": job_applicant, "resume_text": text}
