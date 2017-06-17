from difflib import HtmlDiff


class CompareRevisions(object):
    def __init__(self, rev1, rev2):
        self.rev1 = self.clean(rev1)
        self.rev2 = self.clean(rev2)

    def clean(self, text):
        """Return cleaned text"""
        return text.split('.')

    def compare(self):
        di = HtmlDiff()
        comp = di.make_file(self.rev1, self.rev2)
        return comp
