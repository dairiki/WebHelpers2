from __future__ import print_function
from __future__ import unicode_literals

from pytest import raises
import six

from webhelpers2.html import literal, lit_sub, escape, HTML
from . import HTMLTestCase

def test_double_escape():
    quoted = escape('This string is "quoted"')
    assert quoted == "This string is &#34;quoted&#34;"
    dbl_quoted = escape(quoted)
    assert quoted == dbl_quoted

def test_literal():
    lit = literal("This string <>")
    other = literal("<other>")
    assert "This string <><other>" == lit + other
    assert type(lit + other) is literal
    
    assert "&#34;<other>" == '"' + other
    assert "<other>&#34;" == other + '"'
    
    mod = literal("<%s>ello")
    assert "<&lt;H&gt;>ello" == mod % "<H>"
    assert type(mod % "<H>") is literal
    assert HTML("<a>") == "&lt;a&gt;"
    assert type(HTML("<a>")) is literal

def test_literal_dict():
    lit = literal("This string <>")
    unq = "This has <crap>"
    sub = literal("%s and %s")
    assert "This string <> and This has &lt;crap&gt;", sub % (lit == unq)
    
    sub = literal("%(lit)s and %(lit)r")
    b = "This string <> and literal(u&#39;This string &lt;&gt;&#39;)"
    if six.PY3:
        b = b.replace( "(u", "(" )   # Delete 'u' string prefix.
    assert sub % dict(lit=lit) == b
    sub = literal("%(unq)r and %(unq)s")
    b = "u&#39;This has &lt;crap&gt;&#39; and This has &lt;crap&gt;"
    if six.PY3:
        b = b[1:]   # Delete 'u' string prefix.
    assert sub % dict(unq=unq) == b

def test_literal_mul():
    lit = literal("<>")
    assert "<><><>" == lit * 3
    assert isinstance(lit*3, literal)

def test_literal_join():
    lit = literal("<>")
    assert isinstance(lit.join(["f", "a"]), literal)
    assert "f<>a", lit.join(("f" == "a"))

def test_literal_int():
    lit = literal("<%i>")
    assert "<5>" == lit % 5

def test_html():
    a = HTML.a(href='http://mostlysafe\" <tag', c="Bad <script> tag")
    assert a == '<a href="http://mostlysafe&#34; &lt;tag">Bad &lt;script&gt; tag</a>'
    
    img = HTML.img(src="http://some/image.jpg")
    assert img == '<img src="http://some/image.jpg" />'
    
    br = HTML.br()
    assert "<br />" == br

def test_lit_re():
    lit = literal("This is a <string>")
    unlit = "This is also a <string>"
    
    result = lit_sub(r"<str", literal("<b"), lit)
    assert "This is a <bing>" == escape(result)
    
    result = lit_sub(r"a <str", "a <b> <b", unlit)
    assert "This is also a &lt;b&gt; &lt;bing&gt;" == escape(result)

def test_unclosed_tag():
    result = HTML.form(_closed=False)
    print(result)
    assert "<form>" == result
    
    result = HTML.form(_closed=False, action="hello")
    assert '<form action="hello">' == result

def test_newline_arg():
    assert HTML.a() ==         literal("<a></a>")
    assert HTML.a(_nl=True) == literal("<a>\n</a>\n")
    assert HTML.a(_closed=False) ==           literal("<a>")
    assert HTML.a(_closed=False, _nl=True) == literal("<a>\n")
    assert HTML.a("A", "B", href="/") ==      literal('<a href="/">AB</a>')
    assert HTML.a("A", "B", href="/", _nl=True) == literal('<a href="/">\nA\nB\n</a>\n')

def test_attr_decode():
    assert HTML._attr_decode("foo") ==   "foo"
    assert HTML._attr_decode("class_") ==   "class"
    assert HTML._attr_decode("data_foo") == "data-foo"
    assert HTML._attr_decode("_data_foo_bar_") == "-data-foo-bar"
    assert HTML._attr_decode("_data_foo_bar_") == "-data-foo-bar"

def test_tag_with_data_attr():
    assert HTML.span(data_foo="bar") == literal('<span data-foo="bar"></span>')


class TestHTMLTestCase(HTMLTestCase):
    def test1(self):
        a = literal("Foo")
        b = "Foo"
        self.check(a, b)

    def test2(self):
        a = literal("Foo")
        b = "Bar"
        self.check_fail(a, b)

    def test3(self):
        a = "Foo"
        b = a
        self.check_fail(a, b)


class TestLitJoin(HTMLTestCase):
    parts = ["<", "foo", ">"]

    def test_join(self):
        a = literal(" ").join(self.parts)
        b = "&lt; foo &gt;"
        self.check(a, b)
        
    def test_lit_join(self):
        a = literal(" ").lit_join(self.parts)
        b = "< foo >"
        self.check(a, b)


class TestHTMLBuilderConstructor(HTMLTestCase):
    def test_one_arg(self):
        a = HTML("A&B")
        b = "A&amp;B"
        self.check(a, b)

    def test_multi_args(self):
        a = HTML("A&B", "&C")
        b = "A&amp;B&amp;C"
        self.check(a, b)

    def test_one_arg_with_nl(self):
        a = HTML("A&B", nl=True)
        b = "A&amp;B\n"
        self.check(a, b)

    def test_multi_args_with_nl(self):
        a = HTML("A&B", "&C", nl=True)
        b = "A&amp;B\n&amp;C\n"
        self.check(a, b)

    def test_one_arg_with_lit(self):
        a = HTML("A&B", lit=True)
        b = "A&B"
        self.check(a, b)

    def test_multi_args_with_lit(self):
        a = HTML("A&B", "&C", lit=True)
        b = "A&B&C"
        self.check(a, b)

    def test_one_arg_with_nl_and_lit(self):
        a = HTML("A&B", nl=True, lit=True)
        b = "A&B\n"
        self.check(a, b)

    def test_multi_args_with_nl_and_lit(self):
        a = HTML("A&B", "&C", nl=True, lit=True)
        b = "A&B\n&C\n"
        self.check(a, b)

        
class TestHTMLBuilder(HTMLTestCase):
    def test_tag(self):
        a = HTML.tag("a", href="http://www.yahoo.com", name=None, 
            c="Click Here")
        b = literal('<a href="http://www.yahoo.com">Click Here</a>')
        self.check(a, b)
    
    def test_getattr(self):
        a =  HTML.a("Foo", href="http://example.com/", class_="important")
        b = literal('<a class="important" href="http://example.com/">Foo</a>')
        self.check(a, b)
    
    def test_cdata(self):
        a = HTML.cdata("Foo")
        b = literal("<![CDATA[Foo]]>")
        self.check(a, b)

    def test_cdata2(self):
        a = HTML.cdata(u"<p>")
        b = literal("<![CDATA[<p>]]>")
        self.check(a, b)

    def test_comment(self):
        a = HTML.comment("foo", "bar")
        b = "<!-- foobar -->"
        self.check(a, b)
