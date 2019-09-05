# Copyright (c) 2019, DjaoDjin inc.
# see LICENSE.

from __future__ import unicode_literals

import io, logging, json, subprocess, tempfile

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.template.loader import get_template
from django.views.generic.base import (RedirectView, TemplateView,
    ContextMixin, TemplateResponseMixin)
from django.utils import six
from deployutils.apps.django.templatetags.deployutils_prefixtags import (
    site_prefixed)
from deployutils.crypt import JSONEncoder
from deployutils.helpers import datetime_or_now
from extended_templates.backends.pdf import PdfTemplateResponse
from pages.models import PageElement

from ..api.benchmark import BenchmarkMixin, BenchmarkAPIView
from ..mixins import ReportMixin, TransparentCut
from ..models import Consumption
from ..suppliers import get_supplier_managers


LOGGER = logging.getLogger(__name__)


class ShareRedirectView(ReportMixin, TemplateResponseMixin, ContextMixin,
                        RedirectView):
    """
    On login, by default the user will be redirected to `/app/` which in turn
    will redirect to `/app/:organization/share/$`.

    If *organization* has started an assessment then we have candidates
    to redirect to (i.e. /app/:organization/share/:path).
    """

    template_name = 'envconnect/share/index.html'

    def get_redirect_url(self, *args, **kwargs):
        if self.kwargs.get('organization') in self.accessibles(
                ['manager', 'contributor']):
            # If the user has a more than a `viewer` role on the organization,
            # we force the redirect to the benchmark page such that
            # the contextual menu with assessment, etc. appears.
            try:
                return reverse('share_organization',
                    args=args, kwargs=kwargs)
            except NoReverseMatch:
                return None
        return super(ShareRedirectView, self).get_redirect_url(
            *args, **kwargs)

    def get(self, request, *args, **kwargs):
        candidates = []
        organization = kwargs.get('organization')
        if self.assessment_sample:
            for element in PageElement.objects.filter(tag__contains='industry'):
                root_prefix = '/%s/sustainability-%s' % (
                    element.slug, element.slug)
                if Consumption.objects.filter(
                        answer__sample=self.assessment_sample,
                        path__contains=root_prefix).exists():
                    candidates += [element]
        if not candidates:
            # On user login, registration and activation,
            # we will end-up here.
            if not organization in self.accessibles(
                    roles=['manager', 'contributor']):
                messages.warning(self.request,
                    VIEWER_SELF_ASSESSMENT_NOT_YET_STARTED % {
                        'organization': organization})
            return HttpResponseRedirect(reverse('homepage'))

        redirects = []
        for element in candidates:
            root_prefix = '/sustainability-%s' % element.slug
            kwargs.update({'path': root_prefix})
            url = self.get_redirect_url(*args, **kwargs)
            print_name = element.title
            redirects += [(url, print_name)]

        if len(redirects) > 1:
            context = self.get_context_data(**kwargs)
            context.update({'redirects': redirects})
            return self.render_to_response(context)
        return super(ShareRedirectView, self).get(request, *args, **kwargs)


class ShareView(ReportMixin, TemplateView):

    template_name = 'envconnect/share/index.html'

    def get_context_data(self, **kwargs):
        context = super(ShareView, self).get_context_data(**kwargs)
        from_root, trail = self.breadcrumbs
        # Find supplier managers subscribed to this profile
        # to share scorecard with.
        if self.manages(self.account):
            context.update({
                'is_account_manager': True,
                'supplier_managers': json.dumps(
                    get_supplier_managers(self.account))})
        self.update_context_urls(context, {
            'api_benchmark_share': reverse('api_benchmark_share',
                args=(context['organization'], from_root)),
            'api_organizations': site_prefixed("/api/profile/"),
            'api_viewers': site_prefixed(
                "/api/profile/%s/roles/viewers/" % self.account),
        })
        return context