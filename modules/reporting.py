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
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                overflow: hidden;
            }
            header { 
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: #fff; 
                padding: 30px 40px;
                border-bottom: 4px solid #667eea;
            }
            header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            header .meta {
                display: flex;
                gap: 30px;
                margin-top: 15px;
                font-size: 0.95em;
                opacity: 0.95;
            }
            header .meta span {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .content {
                padding: 40px;
            }
            h2 { 
                color: #1e3c72; 
                margin: 30px 0 20px 0;
                font-size: 1.8em;
                border-bottom: 3px solid #667eea;
                padding-bottom: 10px;
            }
            h3 {
                color: #2a5298;
                margin: 20px 0 15px 0;
                font-size: 1.3em;
            }
            table { 
                border-collapse: collapse; 
                width: 100%; 
                margin-bottom: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                border-radius: 8px;
                overflow: hidden;
            }
            th, td { 
                padding: 15px 20px; 
                text-align: left; 
            }
            th { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                font-weight: 600;
                text-transform: uppercase;
                font-size: 0.9em;
                letter-spacing: 0.5px;
            }
            td {
                border-bottom: 1px solid #f0f0f0;
            }
            tbody tr:hover {
                background: #f8f9ff;
            }
            tbody tr:last-child td {
                border-bottom: none;
            }
            pre { 
                background: #f8f9fa; 
                padding: 20px; 
                border: 1px solid #e9ecef;
                border-radius: 8px;
                overflow-x: auto;
                font-size: 0.9em;
                line-height: 1.6;
            }
            .badge {
                display: inline-block;
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 0.85em;
                font-weight: 600;
            }
            .badge-critical { background: #dc3545; color: white; }
            .badge-warning { background: #ffc107; color: #000; }
            .badge-info { background: #17a2b8; color: white; }
            .badge-success { background: #28a745; color: white; }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            .stat-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 25px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            }
            .stat-card h3 {
                color: white;
                margin: 0 0 10px 0;
                font-size: 2.5em;
            }
            .stat-card p {
                margin: 0;
                font-size: 0.95em;
                opacity: 0.95;
            }
            footer {
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                color: #6c757d;
                border-top: 1px solid #e9ecef;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🔒 Insight Security Report</h1>
                <div class="meta">
                    <span>🎯 <strong>Target:</strong> {{ results.target }}</span>
                    <span>📅 <strong>Date:</strong> {{ results.timestamp }}</span>
                    {% if results.performance and results.performance.total_duration %}
                    <span>⏱️ <strong>Duration:</strong> {{ results.performance.total_duration }}s</span>
                    {% endif %}
                </div>
            </header>
            
            <div class="content">
                <h2>📊 Executive Summary</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>{{ summary.critical }}</h3>
                        <p>Critical Findings</p>
                    </div>
                    <div class="stat-card">
                        <h3>{{ summary.warning }}</h3>
                        <p>Warnings</p>
                    </div>
                    <div class="stat-card">
                        <h3>{{ summary.info }}</h3>
                        <p>Informational</p>
                    </div>
                </div>
                
                {% if results.performance and results.performance.module_times %}
                <h2>⚡ Performance Metrics</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Module</th>
                            <th>Execution Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for module, time in results.performance.module_times.items() %}
                        <tr>
                            <td>{{ module.replace('_', ' ').title() }}</td>
                            <td>{{ time }}s</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% endif %}
                
                <h2>🔍 Detailed Findings</h2>
                {% for name, data in modules %}
                <h3>{{ name.replace('_', ' ').title() }}</h3>
                <pre>{{ data }}</pre>
                {% endfor %}
            </div>
            
            <footer>
                <p>Generated by <strong>Insight v0.2.0</strong> - Advanced Web Pentesting Suite</p>
                <p>© 2026 - Security made visible</p>
            </footer>
        </div>
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
