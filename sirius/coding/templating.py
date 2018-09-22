import io
import os
import datetime
import jinja2

DEFAULT_TEMPLATE_FILE = os.path.join(os.path.dirname(__file__), 'templates/default.html')

ENV = jinja2.Environment()

# TODO apply scrubber library if wanted.
# https://pypi.python.org/pypi/scrubber

def default_template(raw_html, from_name):
    with open(DEFAULT_TEMPLATE_FILE) as f:
        template = f.read()

    t = ENV.from_string(template)
    return t.render(
        raw_html=raw_html,
        date=datetime.datetime.now(),
        from_name=from_name
    ).encode('utf-8')


def deep_web_template():
    template_path = os.path.join(os.path.dirname(__file__), 'templates/deep_web.html')
    with io.open(template_path, mode='r', encoding='utf-8') as f:
        template = f.read()

    t = ENV.from_string(template)

    # TODO pull these from twitter
    tiny_star_field = (
        u'·  .         · ✺  +'
        u'　 ˚  .   + 　 *　  　.'
        u'　 　 　 ⊹  .　　 ✺'
        u' . .  * ·　　✵  　　　　　　　'
        u' 　  .  . 　.　　　　　'
        u'　   .  . 　  　'
        u'　　   . 　　 　　　  ✹'
    )
    ten_print_chr = (
        u'╱╲╲╲╱╲╲╲╱╱'
        u'╱╲╲╲╲╱╲╲╱╱'
        u'╱╲╲╱╲╱╱╱╱╱'
        u'╱╲╲╲╱╲╲╲╲╲'
        u'╲╱╱╱╱╲╱╱╱╱'
        u'╱╲╲╱╲╱╱╲╲╱'
        u'╱╲╲╲╱╲╱╱╱╲'
        u'╲╲╱╲╱╲╱╱╲╲'
        u'╲╱╲╱╱╲╱╱╲╲'
        u'╲╱╲╱╱╲╱╲╱╲'
    )

    return t.render(
        tiny_star_field=tiny_star_field,
        ten_print_chr=ten_print_chr,
        date=datetime.datetime.now(),
    ).encode('utf-8')
