from jinja2 import Environment, select_autoescape
import json


def _calculate_summary(results):
    """Return summary counts similar to print_summary."""
    critical = 0
    warning = 0
    info = 0
    for module, data in results.get("modules", {}).items():
        if module == "ssl_analyzer":
            if any("vulnerable" in str(item).lower() for item in data):
                critical += 1
        elif module == "header_analyzer":
            if any("MISSING" in str(item) for item in data):
                warning += 1
        elif module == "crawler" and data:
            critical += len(data)
    return {"critical": critical, "warning": warning, "info": info}


def _render_html(results):
    """Render HTML report from results."""
    env = Environment(autoescape=select_autoescape(["html", "xml"]))
    template_str = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset='utf-8'>
        <title>Insight Report - {{ results.target }}</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { background: #333; color: #fff; padding: 10px; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
            th { background: #f2f2f2; }
            pre { background: #f8f8f8; padding: 10px; border: 1px solid #eee; }
        </style>
    </head>
    <body>
        <h1>Insight Scan Report</h1>
        <p><strong>Target:</strong> {{ results.target }}</p>
        <p><strong>Date:</strong> {{ results.timestamp }}</p>
        <h2>Summary</h2>
        <table>
            <tr><th>Critical Findings</th><th>Warnings</th><th>Informational</th></tr>
            <tr><td>{{ summary.critical }}</td><td>{{ summary.warning }}</td><td>{{ summary.info }}</td></tr>
        </table>
        <h2>Module Results</h2>
        {% for name, data in modules %}
        <h3>{{ name }}</h3>
        <pre>{{ data }}</pre>
        {% endfor %}
    </body>
    </html>
    """
    template = env.from_string(template_str)
    summary = _calculate_summary(results)
    modules = [(name, json.dumps(data, indent=2)) for name, data in results.get("modules", {}).items()]
    return template.render(results=results, summary=summary, modules=modules)


def generate_html_report(results, outfile):
    """Write HTML report to outfile."""
    html = _render_html(results)
    with open(outfile, "w") as f:
        f.write(html)


def generate_pdf_report(results, outfile):
    """Write PDF report to outfile using weasyprint."""
    from weasyprint import HTML

    html = _render_html(results)
    HTML(string=html).write_pdf(outfile)
