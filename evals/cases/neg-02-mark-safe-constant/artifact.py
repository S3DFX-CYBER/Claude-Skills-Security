from django.utils.safestring import mark_safe

FOOTER = mark_safe("<p>&copy; 2026 Acme Ltd. Registered in England.</p>")

def render_footer():
    return FOOTER
