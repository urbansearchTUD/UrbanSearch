from bs4 import BeautifulSoup

from urbansearch.clustering import link2doc


def test_get_doc():
    l2d = link2doc.Link2Doc()
    text = l2d.get_doc('http://www.nu.nl')
    assert isinstance(text, str)
    assert text != ''

def test_get_doc_bad_link():
    l2d = link2doc.Link2Doc()
    text = l2d.get_doc('http://www.1f3qdewd213d2e§1d21.nl')
    assert text == ''

def test_strip_unwanted_tags():
    html = """
    <head>
        <meta charset="UTF-8">
        <link rel="stylesheet" type="text/css" href="theme.css">
        <style>
            h1 {color:red;}
            p {color:blue;}
        </style>
    </head>
    <body>
        <div>
            <script></script>
            <p>random text</p>
            <p>random text with <img src="random.jpg" alt="random"> an image</p>
        </div>
    </body>
    """

    l2d = link2doc.Link2Doc()
    soup = BeautifulSoup(html, 'html.parser')
    l2d.strip_unwanted_tags(soup)

    assert soup.findAll(link2doc.UNWANTED_TAGS) == []
