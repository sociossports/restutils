import re


def create_html(json_string):
    content = """
    <html>
    <head>
    <title>JSON output</title>
    <link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/highlight.js/8.4/styles/default.min.css">
    </head>
    <body>
    <script src="//cdnjs.cloudflare.com/ajax/libs/highlight.js/8.4/highlight.min.js"></script>
    <script>hljs.initHighlightingOnLoad();</script>
    <pre><code class="json">""" + re.sub('"(https?://.*)"', '"<a href="\\1">\\1</a>"', json_string) + """
    </code>
    </pre>
    </body>
    </html>"""
    return content