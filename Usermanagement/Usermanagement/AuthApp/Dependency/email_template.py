import subprocess

def render_mjml(mjml_content):
    try:
        process = subprocess.run(
            ["~/.local/bin/mjml", "--stdin"],
            input=mjml_content,
            text=True,
            capture_output=True,
            check=True
        )
        return process.stdout  # Rendered HTML
    except subprocess.CalledProcessError as e:
        print(f"Error rendering MJML: {e.stderr}")
        return None

mjml_content = """
<mjml>
  <mj-body>
    <mj-section>
      <mj-column>
        <mj-text>Hello from MJML!</mj-text>
      </mj-column>
    </mj-section>
  </mj-body>
</mjml>
"""

html_content = render_mjml(mjml_content)
if html_content:
    print("Rendered HTML:\n", html_content)
