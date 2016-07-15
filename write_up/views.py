import abc

from django.core.exceptions import SuspiciousOperation
from django.http.response import HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.edit import BaseCreateView, BaseUpdateView, ModelFormMixin
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from write_up.forms import CreateWriteUpForm, EditWriteUpForm, BaseDesignForm, CollectionUnitForm
from write_up.models import WriteUp, BaseDesign, CollectionUnit, Unit
from write_up.serializers import AddContributorWriteUpSerializer


class UserPublicationMixin(object):
    @abc.abstractmethod
    def get_actor(self):
        raise NotImplementedError("Not Implemented Error")

    @abc.abstractmethod
    def get_success_url_prefix(self):
        raise NotImplementedError("Not Implemented Error")


class WriteupPermissionMixin(object):
    contributor = None
    write_up_permissions = {}
    collection_type = None

    def dispatch(self, request, *args, **kwargs):
        method_permission_list = self.write_up_permissions.get(request.method.lower(), [])
        if method_permission_list:
            uuid = self.kwargs.get('write_up_uuid')
            try:
                self.contributor = self.get_actor() \
                    .contribution.get_contributor_for_writeup_with_perm(uuid,
                                                                        method_permission_list,
                                                                        collection_type=self.collection_type)
            except:
                return HttpResponseForbidden()
        return self.post_permission_check(request, *args, **kwargs)

    def post_permission_check(self, request, *args, **kwargs):
        return super(WriteupPermissionMixin, self).dispatch(request, *args, **kwargs)


class CreateWriteUpView(UserPublicationMixin, TemplateResponseMixin, BaseCreateView):
    form_class = CreateWriteUpForm
    model = WriteUp
    template_name = "write_up/form_template.html"
    groups = None

    def get(self, request, *args, **kwargs):
        self.groups = self.get_groups()
        if not self.groups:
            return HttpResponseForbidden()
        return super(CreateWriteUpView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.groups = self.get_groups()
        if not self.groups:
            return HttpResponseForbidden()
        return super(CreateWriteUpView, self).post(request, *args, **kwargs)

    def get_success_url(self):
        write_up = self.object
        url = write_up.get_handler_redirect_url()
        user_type_prefix = self.get_success_url_prefix()
        return user_type_prefix + url + str(write_up.uuid)

    def form_valid(self, form):
        user = self.get_actor()
        self.object = form.save()
        write_up = self.object
        group = form.cleaned_data['group']
        owner = write_up.set_owner(user, group)
        write_up.create_write_up_profile(user=self.request.user)
        write_up.create_write_up_handler(contributor=owner)
        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super(CreateWriteUpView, self).get_form_kwargs()
        kwargs.update({'groups': self.groups})
        return kwargs

    def get_groups(self):
        raise NotImplementedError


class EditWriteUpView(UserPublicationMixin, WriteupPermissionMixin, TemplateResponseMixin, BaseUpdateView):
    # FIXME: change group in this form but who should be able to change i.e define its permission
    form_class = EditWriteUpForm
    model = WriteUp
    template_name = "write_up/form_template.html"

    def get_object(self, queryset=None):
        return self.contributor.write_up

    def get_success_url(self):
        write_up = self.object
        user_type_prefix = self.get_success_url_prefix()
        return user_type_prefix + "/edit_write_up/" + str(write_up.uuid)


class EditBaseDesign(UserPublicationMixin, WriteupPermissionMixin, TemplateResponseMixin, BaseUpdateView):
    model = BaseDesign
    template_name = "write_up/form_template.html"
    form_class = BaseDesignForm
    write_up = None
    article_unit = None

    def get_object(self, queryset=None):
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
        kwargs = super(EditBaseDesign, self).get_form_kwargs()
        kwargs.update({'write_up': self.write_up, 'article_unit': self.article_unit})
        return kwargs

    def form_valid(self, form):
        method_name = 'save_title_for_' + self.write_up.collection_type
        save_title = getattr(self, method_name)
        save_title(form)
        base_design = form.save(commit=False)
        if self.request.POST.get('save_with_revision'):
            base_design.save_with_revision(user=self.contributor, title=form.cleaned_data['revision_history_title'])
            return HttpResponseRedirect(self.get_success_url())
        else:
            base_design.autosave_with_revision(user=self.contributor)
            return JsonResponse({"success": True})

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


class CollectionUnitView(UserPublicationMixin, WriteupPermissionMixin, TemplateResponseMixin, ModelFormMixin, View):
    template_name = "write_up/collection_unit_list.html"
    model = CollectionUnit
    form_class = CollectionUnitForm
    write_up = None
    chapters = None

    def get_write_up(self):
        if self.write_up:
            return self.write_up
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
        unit.add_unit_contributor(self.contributor)

        if not self.contributor.is_owner:
            owner = self.write_up.get_owner()
            unit.add_unit_contributor(owner)

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

# TODO: add_contributor, remove_contributor, edit permission


class ContributorRequest(UserPublicationMixin, WriteupPermissionMixin, CreateAPIView):
    serializer_class = AddContributorWriteUpSerializer
    write_up = None

    def get_contributors(self):
        return self.write_up.get_all_contributors()

    def get_queryset(self):
        return self.get_contributors()

    def get(self, request, *args, **kwargs):
        self.write_up = self.contributor.write_up
        contributors = self.get_contributors()
        serializer = self.get_serializer(contributors, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        self.write_up = self.contributor.write_up
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contributor = serializer.obj
        permission_list = serializer.validated_data.get('permissions')
        share_XP = serializer.validated_data.get('share_XP')
        share_money = serializer.validated_data.get('share_money')
        # TODO: create notification and request for adding contributor and ask for group in request
        message = 'The contributor has been sent a request. Wait for his response.'
        serializer.data[0].update({'message': message})
        return Response(serializer.data)
