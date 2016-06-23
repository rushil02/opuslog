import abc

from django.contrib.auth import get_user_model
from django.core.exceptions import SuspiciousOperation
from django.http.response import HttpResponseRedirect
from django.views.generic.base import TemplateResponseMixin, View

from django.views.generic.edit import BaseCreateView, BaseUpdateView, ModelFormMixin

from write_up.forms import CreateWriteUpForm, EditWriteUpForm, BaseDesignForm, CollectionUnitForm
from write_up.models import WriteUp, BaseDesign, CollectionUnit, Unit


class UserPublicationMixin(object):
    @abc.abstractmethod
    def get_user(self):
        raise NotImplementedError("Not Implemented Error")

    @abc.abstractmethod
    def get_publication_user(self):
        raise NotImplementedError("Not Implemented Error")

    @abc.abstractmethod
    def get_success_url_prefix(self):
        raise NotImplementedError("Not Implemented Error")


class CreateWriteUpView(UserPublicationMixin, TemplateResponseMixin, BaseCreateView):
    form_class = CreateWriteUpForm
    model = WriteUp
    template_name = "write_up/form_template.html"

    def get_success_url(self):
        write_up = self.object
        url = write_up.get_handler_redirect_url()
        user_type_prefix = self.get_success_url_prefix()
        return user_type_prefix + url + str(write_up.uuid)

    def form_valid(self, form):
        user = self.get_user()
        self.object = form.save()
        write_up = self.object
        write_up.set_owner(user, publication_user=self.get_publication_user())
        write_up.create_write_up_handler(
            user=user)  # TODO: owner in contributor of a unit(UnitContributor) where owner is publication. i dont understand what should i fill in user variable which is not null for publication type owner.
        return HttpResponseRedirect(self.get_success_url())


class EditWriteUpView(UserPublicationMixin, TemplateResponseMixin, BaseUpdateView):
    form_class = EditWriteUpForm
    model = WriteUp
    template_name = "write_up/form_template.html"
    contributor = None

    def get_object(self, queryset=None):
        self.contributor = self.kwargs.get('contributor')
        return self.contributor.write_up

    def get_success_url(self):
        write_up = self.object
        user_type_prefix = self.get_success_url_prefix()
        return user_type_prefix + "/edit_write_up/" + str(write_up.uuid)


class EditIndependentArticle(UserPublicationMixin, TemplateResponseMixin, BaseUpdateView):
    model = BaseDesign
    template_name = "write_up/form_template.html"
    form_class = BaseDesignForm
    contributor = None
    write_up = None
    article_unit = None

    def get_object(self, queryset=None):
        self.contributor = self.kwargs.get('contributor')
        self.write_up = self.contributor.write_up
        method_name = 'get_object_for_' + self.write_up.collection_type
        method = getattr(self, method_name)
        return method()

    def get_object_for_I(self):
        self.article_unit = self.write_up.unit
        return self.article_unit.text

    def get_object_for_M(self):
        index = int(self.kwargs['chapter_index'])
        try:
            self.chapter = self.write_up.get_chapter_from_index(index)
        except Exception as e:
            raise SuspiciousOperation("No Chapter Found")
        else:
            self.article_unit = self.chapter.article
            return self.article_unit.text

    def get_form_kwargs(self):
        kwargs = super(EditIndependentArticle, self).get_form_kwargs()
        kwargs.update({'write_up': self.write_up, 'article_unit': self.article_unit})
        return kwargs

    def form_valid(self, form):
        method_name = 'save_title_for_' + self.write_up.collection_type
        save_title = getattr(self, method_name)
        save_title(form)
        base_design = form.save(commit=False)
        if self.request.POST['save_with_revision']:
            base_design.save_with_revision(user=self.contributor, title=form.cleaned_data['revision_history_title'])
        else:
            base_design.save()
        return HttpResponseRedirect(self.get_success_url())

    def save_title_for_I(self, form):
        if form.cleaned_data['title'] != self.write_up.title:
            self.write_up.title = form.cleaned_data['title']
            self.write_up.save()

    def save_title_for_M(self, form):
        if form.cleaned_data['title'] != self.article_unit.title:
            self.article_unit.title = form.cleaned_data['title']
            self.article_unit.save()

    def get_success_url(self):
        user_type_prefix = self.get_success_url_prefix()
        method_name = 'get_success_url_suffix_for_' + self.write_up.collection_type
        suffix = getattr(self, method_name)
        return user_type_prefix + suffix()

    def get_success_url_suffix_for_I(self):
        return "/edit_article/" + str(self.write_up.uuid)

    def get_success_url_suffix_for_M(self):
        return "/edit_article/" + str(self.write_up.uuid) + '/' + self.kwargs['chapter_index']


# class AddUnitView(UserPublicationMixin, TemplateResponseMixin, View, ContextMixin):
#     template_name = "write_up/form_template.html"
#     formset_class = CollectionUnitFormSet
#     model = CollectionUnit
#     write_up = None
#     contributor = None
# 
#     def get_context_data(self, **kwargs):
#         if 'formset' not in kwargs:
#             kwargs['formset'] = self.get_formset()
#         if self.write_up:
#             kwargs['write_up'] = self.write_up
#         return super(AddUnitView, self).get_context_data(**kwargs)
# 
#     def get_formset(self):
#         return self.formset_class(**self.get_formset_kwargs())
# 
#     def get_formset_kwargs(self):
#         kwargs = {}
#         if self.request.method in ('POST', 'PUT'):
#             kwargs.update({
#                 'data': self.request.POST,
#             })
#         kwargs.update({'instance': self.write_up})
#         return kwargs
# 
#     def get(self, request, *args, **kwargs):
#         self.write_up = self.get_write_up()
#         return self.render_to_response(self.get_context_data())
# 
#     def get_write_up(self):
#         self.contributor = self.kwargs.get('contributor')
#         return self.contributor.write_up
# 
#     def post(self, request, *args, **kwargs):
#         self.write_up = self.get_write_up()
#         formset = self.get_formset()
#         if formset.is_valid():
#             return self.formset_valid(formset)
#         else:
#             return self.formset_invalid(formset)
# 
#     def formset_valid(self, formset):
#         for form in formset:
#             collection_unit = form.save(commit=False)
# 
# 
#     def formset_invalid(self, formset):
#         pass


class CollectionUnitView(UserPublicationMixin, TemplateResponseMixin, ModelFormMixin, View):
    template_name = "write_up/collection_unit_list.html"
    model = CollectionUnit
    form_class = CollectionUnitForm
    write_up = None
    contributor = None
    chapters = None

    def get_write_up(self):
        if self.write_up:
            return self.write_up
        self.contributor = self.kwargs.get('contributor')
        return self.contributor.write_up

    def get(self, request, *args, **kwargs):
        self.object = None
        self.write_up = self.get_write_up()
        self.chapters = self.write_up.get_all_chapters()
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = None
        self.write_up = self.get_write_up()
        self.chapters = self.write_up.get_all_chapters()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        title = form.cleaned_data['title']
        collection_unit = form.save(commit=False)
        collection_unit.magazine = self.write_up
        collection_unit.relationship = 'I'

        base_design = BaseDesign.objects.create()
        unit = Unit.objects.create(text=base_design, title=title)
        if isinstance(self.get_user(), get_user_model()):
            unit.add_unit_contributor(self.get_user())
        else:
            unit.add_unit_contributor(user=self.get_publication_user(), publication=self.get_user())

        if not self.contributor.is_owner:
            owner = self.write_up.get_owner()
            if isinstance(owner.contributor, get_user_model()):
                unit.add_unit_contributor(owner.contributor)
                # TODO: owner in contributor of a unit(UnitContributor) where owner is publication. i dont understand what should i fill in user variable which is not null for publication type owner.

        collection_unit.article = unit
        self.object = collection_unit.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        user_type_prefix = self.get_success_url_prefix()
        chapter_number = self.chapters.count()
        return user_type_prefix + "/edit_article/" + str(self.write_up.uuid) + '/' + str(chapter_number)

    def get_context_data(self, **kwargs):
        context = super(CollectionUnitView, self).get_context_data(**kwargs)
        context.update({"queryset": self.chapters, "write_up": self.write_up})
        return context

# TODO: Auto-save, add_contributor, remove_contributor, edit permission
