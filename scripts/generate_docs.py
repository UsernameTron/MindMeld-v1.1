import json
import os

from fastapi.openapi.utils import get_openapi

from app.main import app

DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")


def generate_openapi_spec():
    """Generate OpenAPI spec from FastAPI app and save as openapi.json."""
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    os.makedirs(DOCS_DIR, exist_ok=True)
    with open(os.path.join(DOCS_DIR, "openapi.json"), "w") as f:
        json.dump(openapi_schema, f, indent=2)
    print("OpenAPI spec generated at docs/openapi.json")


def generate_markdown_docs():
    """Generate Markdown documentation for all endpoints."""
    openapi_path = os.path.join(DOCS_DIR, "openapi.json")
    if not os.path.exists(openapi_path):
        print("OpenAPI spec not found. Run generate_openapi_spec() first.")
        return
    with open(openapi_path) as f:
        spec = json.load(f)

    md_lines = [f"# {spec['info']['title']} API Documentation\n"]
    for path, methods in spec["paths"].items():
        for method, details in methods.items():
            md_lines.append(f"## `{method.upper()} {path}`\n")
            md_lines.append(f"**Summary:** {details.get('summary', '')}\n")
            if details.get("description"):
                md_lines.append(f"**Description:** {details['description']}\n")
            # Parameters
            if details.get("parameters"):
                md_lines.append("**Parameters:**\n")
                for param in details["parameters"]:
                    md_lines.append(
                        f"- `{param['name']}` ({param['in']}): {param.get('description', '')}"
                    )
            # Request body
            if "requestBody" in details:
                md_lines.append("**Request Body:**\n")
                content = details["requestBody"]["content"]
                for ctype, cval in content.items():
                    md_lines.append(f"- `{ctype}`: {cval.get('schema', {})}")
            # Responses
            if "responses" in details:
                md_lines.append("**Responses:**\n")
                for code, resp in details["responses"].items():
                    desc = resp.get("description", "")
                    md_lines.append(f"- `{code}`: {desc}")
            md_lines.append("")
    with open(os.path.join(DOCS_DIR, "api.md"), "w") as f:
        f.write("\n".join(md_lines))
    print("Markdown API docs generated at docs/api.md")


if __name__ == "__main__":
    generate_openapi_spec()
    generate_markdown_docs()
