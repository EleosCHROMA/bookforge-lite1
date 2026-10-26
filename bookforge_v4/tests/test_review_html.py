import unittest
from bookforge_v4.review_html import render

class ReviewHtmlTests(unittest.TestCase):
    def test_source_is_escaped_and_pending_status_is_visible(self):
        packet={'items':[{'id':'practice:<script>','content_sha256':'a'*64,
            'content':{'chapter':1,'kind':'practice','source':{'prompt':'</pre><script>alert(1)</script>','answer':'42'}}}]}
        html=render(packet,{'items':[{'id':'practice:<script>','status':'PENDING'}]})
        self.assertNotIn('</pre><script>alert',html)
        self.assertIn('&lt;script&gt;',html)
        self.assertIn('PENDING',html)
        self.assertIn('"answer": "42"',html.replace('&quot;','"'))
        self.assertIn('reviewer-only',html)
