"""Tests for documenteer.sphinext.mockcoderefs."""


from tempfile import mkdtemp
from shutil import rmtree
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

import pytest
from sphinx.application import Sphinx

import documenteer.sphinxext.mockcoderefs as mockcoderefs


@pytest.fixture()
def app(request):
    src = mkdtemp()
    doctree = mkdtemp()
    confdir = mkdtemp()
    outdir = mkdtemp()

    Sphinx._log = lambda self, message, wfile, nonl=False: None
    app = Sphinx(
        srcdir=src,
        confdir=None,
        outdir=outdir,
        doctreedir=doctree,
        buildername='html',
    )
    mockcoderefs.setup(app)
    # Stitch together as the sphinx app init() usually does w/ real conf files
    app.config.init_values(Sphinx._log)

    def fin():
        for dirname in (src, doctree, confdir, outdir):
            rmtree(dirname)

    request.addfinalizer(fin)

    return app


@pytest.fixture()
def inliner(app):
    return Mock(document=Mock(settings=Mock(env=Mock(app=app))))


@pytest.mark.parametrize(
    'test_input,expected',
    [(('lmod', 'lsst.afw'), 'lsst.afw'),
     (('lmod', '~lsst.afw'), 'afw'),
     (('lmod', '~lsst'), 'lsst')])
def test_mock_code_ref_role(inliner, test_input, expected):
    role_name, role_content = test_input
    result = mockcoderefs.mock_code_ref_role(
        name=role_name,
        rawtext=role_content,
        text=role_content,
        inliner=inliner,
        lineno=None)
    assert result[0][0].astext() == expected
