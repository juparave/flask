# Create PDF files with `xhtml2pdf` lib

Install library

    $ pip install xhtml2pdf

Create a simple function to receive the html file, already rendered.

```python
from io import BytesIO     # for handling byte strings

from xhtml2pdf import pisa


def convert_html_to_pdf_stream(source_html, replace_char=False):

    pisa.showLogging()
    # create pdf
    buf = BytesIO()
    pisa.showLogging()

    if replace_char:
        # in case of enconding errors on PDF, replace with htmlentities
        pisa_status = pisa.pisaDocument(
            BytesIO(source_html.encode("ascii", "xmlcharrefreplace")),
            buf, encoding="utf-8")
    else:
        pisa_status = pisa.pisaDocument(
            BytesIO(source_html.encode("utf-8")),
            buf, encoding="utf-8")

    if pisa_status.err:
        # logger.error(
        #     'xhtml2pdf encountered exception during generation of pdf %s: %s',
        #     context['filename'],
        #     pisa_status.err
        # )
        print("PISA Error")
        return

    pdfData = buf.getvalue()

    return pdfData
```

Use the function on your view and return the pdf bytes on the request.

```python
registry_blueprint = Blueprint('registry_blueprint', __name__)


@registry_blueprint.route('/api/v1/registry/to_pdf')
@auth_required
def to_pdf():
    """ Returns Registry PDF """

    # if request.method == OPTIONS, ignore it
    if request.method == 'OPTIONS':
        return

    registry_id = request.args.get('registerId')
    registry = db.session.query(Registry).filter_by(id=registry_id).first()
    # get current path to calculate fonts path
    parent_dir = pathlib.Path(__file__).parent.parent.resolve()
    static_dir = parent_dir / 'static'
    static_dir.resolve()
    html = render_template("registry.html",  registry=registry, static_dir=static_dir)
    pdf = convert_html_to_pdf_stream(html, replace_char=True)
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline; filename=registro_{}.pdf".format(registry.id)
    return response
```

In case your using custom fonts on your template, i.e. `FontAwesom` you have to send absolute path to the template.

Calculate the absolute path of your statics files using pathlib.   In this case, `static` is a sibling of `views` directory where the script is executed

```python
    # get current path to calculate fonts path
    parent_dir = pathlib.Path(__file__).parent.parent.resolve()
    static_dir = parent_dir / 'static'
    static_dir.resolve()
```

Use the `static_dir` inside your html template:

```html
  <style>
    @font-face {
      font-family: 'Font Awesome 5 Free';
      font-style: normal;
      font-display: block;
      src: url("file:///{{ static_dir }}/webfonts/fa-regular-400.ttf") format("truetype");
    }

    .far {
      font-family: 'Font Awesome 5 Free';
      font-weight: 400;
    }
...
```
