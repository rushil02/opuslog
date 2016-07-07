import datetime

from haystack import indexes

from write_up.models import WriteUp


class WriteUpIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    # author = indexes.CharField(model_attr='user')
    create_time = indexes.DateTimeField(model_attr='create_time')

    def get_model(self):
        return WriteUp

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(create_time__lte=datetime.datetime.now())
