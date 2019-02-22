import os
import datetime

parent_directory = os.path.dirname(__file__)
js_path = os.path.join('client_build', 'bookmarklet.js')
with open(js_path, 'r') as f:
    js_source = f.read()

html_src_path = os.path.join('client', 'index.html')
with open(html_src_path, 'r') as f:
    html_source: str = f.read()

now = datetime.datetime.now()
html_source = html_source.replace(r'{{JAVASCRIPT_SOURCE}}', js_source)
html_source = html_source.replace(r'{{DATETIME}}', now.isoformat())
html_source = html_source.replace(r'{{DATE}}', now.strftime("%Y-%m%d"))
html_out_path = os.path.join('templates', 'index.html')
with open(html_out_path, 'w') as f:
    f.write(html_source)