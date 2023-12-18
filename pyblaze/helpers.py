from .responses import HttpResponse

template = """
<!DOCTYPE html>
<html>
<title>Not Found</title>
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


def format_server_exception() -> HttpResponse:
    msg = template.format(
        message="Internal Server Error"
        "<br><br>We are currently trying to fix the problem.",
        status_code=500,
    )
    return HttpResponse(content=msg, status_code=500, content_type="text/html")


def format_not_found_exception() -> HttpResponse:
    msg = template.format(
        message="Ooops!!! The page you are looking for is not found", status_code=404
    )
    return HttpResponse(content=msg, status_code=404, content_type="text/html")


def format_method_not_allowed_exception() -> HttpResponse:
    msg = template.format(
        message="Method Not Allowed"
        "<br><br>The method is not allowed for the requested URL.",
        status_code=405,
    )
    return HttpResponse(content=msg, status_code=405, content_type="text/html")
