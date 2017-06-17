from django.shortcuts import render

from write_up.comp_rev_history import CompareRevisions
from write_up.models import RevisionHistory


def rev_view(request, rev1_id, rev2_id):
    rev1 = RevisionHistory.objects.get(id=rev1_id).text
    rev2 = RevisionHistory.objects.get(id=rev2_id).text

    clk = CompareRevisions(rev1, rev2)
    return render(request, 'test.html', {'var': clk.compare()})
