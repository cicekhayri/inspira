from inspira.constants import TEXT_HTML
from inspira.responses import HttpResponse

template = """
<!DOCTYPE html>
<html>
<title>{title}</title>
<style>
html, body{{
  margin: 0;
  padding: 0;
  text-align: center;
  font-family: sans-serif;
}}

h1, a{{
  margin: 0;
  padding: 0;
  text-decoration: none;
}}

.section{{
  padding: 4rem 2rem;
}}

.section .error{{
  font-size: 150px;
}}

.page{{
  font-size: 20px;
  font-weight: 600;
}}

.back-home{{
  display: inline-block;
  text-transform: uppercase;
  font-weight: 600;
  padding: 0.75rem 1rem 0.6rem;
}}
</style>
<body>

<div class="section">
  <h1 class="error">{status_code}</h1>
  <div class="page">{message}</div>
</div>

</body>
</html>
"""


def format_internal_server_error() -> HttpResponse:
    msg = template.format(
        title="Internal Server Error",
        message="Internal Server Error"
        "<br><br>We are currently trying to fix the problem.",
        status_code=500,
    )
    return HttpResponse(content=msg, status_code=500, content_type=TEXT_HTML)


def format_not_found_exception() -> HttpResponse:
    msg = template.format(
        title="Not Found",
        message="Ooops!!! The page you are looking for is not found",
        status_code=404,
    )
    return HttpResponse(content=msg, status_code=404, content_type=TEXT_HTML)


def format_forbidden_exception() -> HttpResponse:
    msg = template.format(
        title="Forbidden",
        message="Forbidden",
        status_code=403,
    )
    return HttpResponse(content=msg, status_code=403, content_type=TEXT_HTML)


def format_unauthorized_exception() -> HttpResponse:
    msg = template.format(
        title="Unauthorized",
        message="Unauthorized",
        status_code=401,
    )
    return HttpResponse(content=msg, status_code=401, content_type=TEXT_HTML)


def format_method_not_allowed_exception() -> HttpResponse:
    msg = template.format(
        title="Method Not Allowed",
        message="Method Not Allowed"
        "<br><br>The method is not allowed for the requested URL.",
        status_code=405,
    )
    return HttpResponse(content=msg, status_code=405, content_type=TEXT_HTML)
