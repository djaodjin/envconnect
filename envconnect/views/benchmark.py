# Copyright (c) 2020, DjaoDjin inc.
# see LICENSE.

from __future__ import unicode_literals

import io, logging, json, subprocess, tempfile

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.template.loader import get_template
from django.views.generic.base import TemplateView
from django.utils import six
from deployutils.crypt import JSONEncoder
from deployutils.helpers import datetime_or_now, update_context_urls
from extended_templates.backends.pdf import PdfTemplateResponse

from ..compat import reverse
from ..api.benchmark import BenchmarkMixin, ScorecardQuerySetMixin
from ..mixins import TransparentCut


LOGGER = logging.getLogger(__name__)


class BenchmarkView(BenchmarkMixin, TemplateView):
    """
    Subclasses are meant to define `template_name` and `breadcrumb_url`.
    """
    template_name = 'envconnect/benchmark.html'
    breadcrumb_url = 'benchmark'

    def get_context_data(self, **kwargs):
        #pylint:disable=too-many-locals
        context = super(BenchmarkView, self).get_context_data(**kwargs)
        segment_url, segment_prefix, segment_element = self.segment
        root = None
        if segment_element:
            root = self._build_tree(segment_element, segment_prefix,
                cut=TransparentCut())
            # Flatten icons and practices (i.e. Energy Efficiency) to produce
            # the list of charts.
            self.decorate_with_breadcrumbs(root)
            charts = self.get_charts(root, excludes=[segment_element.slug])
            organization = kwargs.get('organization')
            if self.assessment_sample:
                last_updated_at = self.assessment_sample.created_at.strftime(
                    "%b %Y")
                update_context_urls(context, {
                    'scorecard_organization_download': reverse(
                        'scorecard_organization_download', args=(
                            organization, self.assessment_sample, segment_url)),
                    'api_account_benchmark': reverse('api_benchmark', args=(
                        organization, self.assessment_sample,
                        segment_prefix[1:])),
                    'api_historical_scores': reverse(
                        'api_historical_scores', args=(
                            organization, segment_prefix[1:])),
                })
                context.update({'sample': self.assessment_sample})
            else:
                # There are no assessment yet.
                last_updated_at = "N/A"
                if organization in self.accessibles(roles=[
                        'manager', 'contributor']):
                    if organization != settings.APP_NAME:
                        # /app/:organization/scorecard/:path
                        # Only when accessing an actual scorecard and
                        # if the request user is a manager/contributor
                        # for the organization will we prompt to start
                        # the assessment.
                        context.update({'no_assessment_warning':
                          "You need to complete an <em>Assessment</em> before"\
                          " moving on to the <em>Scorecard</em>."})
                else:
                    context.update({'no_assessment_warning':
                        "This organization has not yet started"\
                        " their <em>Assessment</em>."})
            context.update({
                'charts': charts,
                'root': root,
                'entries': json.dumps(root, cls=JSONEncoder),
                'last_updated_at': last_updated_at,
            })
        return context

    def get_assessment_redirect_url(self, *args, **kwargs):
        #pylint:disable=unused-argument
        url_path = kwargs.get('path')
        organization = kwargs.get('organization')
        if not isinstance(url_path, six.string_types):
            url_path = ""
        if organization in self.accessibles(
                roles=['manager', 'contributor']):
            # /app/:organization/scorecard/:path
            # Only when accessing an actual scorecard and if the request user
            # is a manager/contributor for the organization will we prompt
            # to start the assessment.
            messages.warning(self.request,
                "You need to complete an assessment before"\
                " moving on to the scorecard.")
            return HttpResponseRedirect(
                reverse('assess_organization_redirect',
                    kwargs={'organization': organization, 'path': url_path}))
        return HttpResponseRedirect(reverse('summary_organization_redirect',
            kwargs={'organization': organization, 'path': url_path}))


class PrintableChartsMixin(object):
    """
    Creates images of charts that could then be embed in printable documents.
    """

    @staticmethod
    def get_base_url():
        return "file://%s" % settings.HTDOCS

    def generate_chart_image(self, slug, template_name, context,
                             js_content, cache_storage, on_start=True,
                             width=410, height=300, delay=1):
        #pylint:disable=too-many-arguments
        context.update({'base_url': self.get_base_url()})
        template = get_template(template_name)
        content = template.render(context, self.request)
        cache_storage.save('%s.html' % slug, io.StringIO(content))
        phantomjs_url = 'file://%s/%s.html' % (
            cache_storage.location, slug)
        img_path = cache_storage.path('%s.png' % slug)
        if on_start:
            js_content.write("""casper.start('%(url)s', function() {
    this.echo("starting...");
});
""" % {'url': phantomjs_url})
        js_content.write("""
casper.viewport(%(width)s, %(height)s).thenOpen('%(url)s', function() {
    this.wait(%(delay)d, function() {
        this.capture('%(img_path)s', {top: 0, left: 0, width: %(width)s, height: %(height)s});
    });
});
""" % {'width': width, 'height': height, 'delay': delay,
       'url': phantomjs_url, 'img_path': img_path})
        return self.get_base_url() + cache_storage.url('%s.png' % slug)

    def generate_printable_html(self, charts):
        location = tempfile.mkdtemp(
            prefix=settings.APP_NAME + "-", dir=settings.MEDIA_ROOT)
        base_url = (
            settings.MEDIA_URL + location.replace(settings.MEDIA_ROOT, ""))
        cache_storage = FileSystemStorage(
            location=location, base_url=base_url)
        js_content = io.StringIO()
        js_content.write("""var casper = require('casper').create();

""")
        on_start = True
        for chart in charts:
            if chart['slug'] == 'totals':
                chart['image'] = self.generate_chart_image(chart['slug'],
                    'envconnect/prints/total_score.html',
                    context={'total_score': chart},
                    js_content=js_content,
                    cache_storage=cache_storage,
                    on_start=on_start,
                    width=300, height=200, delay=2)
            else:
                chart['distribution'] = json.dumps(
                    chart.get('distribution', {}))
                chart['image'] = self.generate_chart_image(chart['slug'],
                    'envconnect/prints/benchmark_graph.html',
                    context={'chart': chart},
                    js_content=js_content,
                    cache_storage=cache_storage,
                    on_start=on_start,
                    width=270, height=204)
            on_start = False
        js_content.write("""
casper.run();
""")
        js_content.seek(0)
        js_generate_images = 'generate-images.js'
        cache_storage.save(js_generate_images, js_content)
        phantomjs_script_path = cache_storage.path(js_generate_images)
        cmd = [settings.PHANTOMJS_BIN.replace('bin/phantomjs', 'bin/casperjs'),
            phantomjs_script_path]
        LOGGER.info("RUN: %s", ' '.join(cmd))
        subprocess.check_call(cmd)


class BenchmarkDownloadView(PrintableChartsMixin, ScorecardQuerySetMixin,
                            TemplateView):
    """
    Download the scorecard of an organization as a PDF
    """
    template_name = 'envconnect/prints/benchmark.html'

    @property
    def score_charts(self):
        if not hasattr(self, '_score_charts'):
            self._score_charts = self.get_queryset()
            segment_url, segment_prefix, segment_element = self.segment
            excludes = [segment_element.slug]
            found = -1
            for idx, chart in enumerate(self._score_charts):
                if chart.get('slug', None) in excludes:
                    found = idx
                    break
            if found >= 0:
                del self._score_charts[found]
        return self._score_charts

    def get_printable_charts(self):
        if not hasattr(self, '_printable_charts'):
            self._printable_charts = []
            for chart in self.score_charts:
                slug = chart.get('slug', "")
                tag = chart.get('tag', None)
                if (slug == 'totals'
                    or (tag and settings.TAG_SCORECARD in tag)):
                    icon = chart.get('icon', None)
                    if icon and icon.startswith('/'):
                        if icon.startswith('/%s/' % settings.APP_NAME):
                            icon = icon[len(settings.APP_NAME) + 1:]
                        chart['icon'] = self.get_base_url() + icon
                    self._printable_charts += [chart]
        return self._printable_charts

    def get_context_data(self, **kwargs):
        context = {'base_url': self.get_base_url()}
        context.update({'organization': self.account})
        from_root, trail = self.breadcrumbs
        root = None
        if trail:
            root = self._build_tree(trail[-1][0], from_root,
                    cut=TransparentCut())
            # Flatten icons and practices (i.e. Energy Efficiency) to produce
            # the list of charts.
            for element in six.itervalues(root[1]):
                for chart in self.score_charts:
                    # We use `score_charts`, not `get_printable_charts` because
                    # not all top level icons might show up in the benchmark
                    # graphs, yet we need to display the scores under the icons.
                    if element[0]['slug'] == chart['slug']:
                        if 'normalized_score' in chart:
                            element[0]['normalized_score'] = "%s%%" % chart.get(
                                'normalized_score')
                        else:
                            element[0]['normalized_score'] = "N/A"
                        element[0]['score_weight'] = chart.get(
                            'score_weight', "N/A")
                        break
            charts = self.get_printable_charts()
            for chart in charts:
                if chart['slug'] == 'totals':
                    context.update({
                        'total_chart': chart,
                        'nb_respondents': chart.get('nb_respondents', "N/A")})
                    break
            context.update({
                'charts': [chart
                    for chart in charts if chart['slug'] != 'totals'],
                'breadcrumbs': trail,
                'root': root,
                'at_time': datetime_or_now()
            })
            context.update({
                'highlighted_practices': self.get_highlighted_practices(),
            })
        return context

    def get(self, request, *args, **kwargs):
        # Hacky way to insure `get_queryset` will use the same kwargs['path']
        # than as the API.
        from_root, _ = self.breadcrumbs
        self._breadcrumbs = self.get_breadcrumbs(from_root)
        self.generate_printable_html(self.get_printable_charts())
        return PdfTemplateResponse(request, self.template_name,
            self.get_context_data(**kwargs))
