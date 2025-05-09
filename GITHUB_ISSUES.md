🧾 MindMeld GitHub Issue Cards (Auto-Generated)

⸻

✅ Add structured logging and request ID middleware

🎯 Goal

Add request correlation ID middleware and structured JSON logging using loguru.

🧱 Files to Create
	•	middleware/request_id.py — UUID generator + header injection
	•	services/logging.py — JSON logger configuration with request ID
	•	Modify main.py — Add middleware to app

🛠 Requirements
	•	Use loguru + uuid4 for traceability
	•	Add X-Request-ID header to all responses
	•	Replace print() with logger.info/debug/error()

✅ Success Criteria
	•	Logs include request ID per line
	•	Test routes return X-Request-ID header
	•	Middleware errors are logged with trace ID

⸻

✅ Define custom exception classes and global error handler

🎯 Goal

Implement a clean exception handling strategy.

🧱 Files to Create
	•	services/errors.py — Custom exceptions
	•	core/errors.py — Global error handler

🛠 Requirements
	•	Map service-level exceptions to HTTP responses
	•	Use FastAPI @app.exception_handler
	•	Log all exceptions to console with request ID if present

✅ Success Criteria
	•	Clean JSON error responses returned
	•	Errors are logged + mappable
	•	No stack trace exposure in API

⸻

✅ Scaffold /prompt/advanced endpoint (Jinja2 prompt service)

🎯 Goal

Render dynamic prompt templates using Jinja2.

🧱 Files to Create
	•	models/prompt/prompt.py
	•	services/prompt_template_service.py
	•	api/routes/prompt.py
	•	config/prompt_templates/*.j2

🛠 Requirements
	•	Add jinja2 to dependencies
	•	Load template by name + vars
	•	Return final string

✅ Success Criteria
	•	POST /prompt/advanced returns rendered prompt
	•	Missing template returns 404
	•	Template examples work (default_chat.j2)

⸻

✅ Add embedding drift detector

🎯 Goal

Detect when new content deviates semantically from your base embedding profile.

🧱 Files to Create
	•	tasks/drift_check.py
	•	utils/alerts.py
	•	data/embeddings_base.pkl

🛠 Requirements
	•	Compare vector drift using cosine distance
	•	Alert on threshold overage
	•	Log when stable

✅ Success Criteria
	•	Weekly drift check runs
	•	Alerts/logs when drift detected
	•	No crash on malformed data

⸻

✅ Implement /convert endpoint (document parsing)

🎯 Goal

Build a doc conversion pipeline for PDF, DOCX, Markdown.

🧱 Files to Create
	•	models/convert/convert.py
	•	services/convert/convert_service.py
	•	api/routes/convert.py
	•	tests/test_api/test_convert.py

🛠 Requirements
	•	Handle file uploads
	•	Use format-specific parser
	•	Return plaintext

✅ Success Criteria
	•	Upload returns valid output
	•	Test cases pass
	•	Graceful errors for unsupported files
