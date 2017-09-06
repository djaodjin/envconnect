# Copyright (c) 2017, DjaoDjin inc.
# see LICENSE.
from __future__ import unicode_literals

import csv, datetime, json, logging, io

from django.utils import six
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import TemplateView
from deployutils.crypt import JSONEncoder
from openpyxl import Workbook
from survey.models import Answer, Response, SurveyModel

from ..api.benchmark import BenchmarkMixin
from ..models import Consumption, Improvement
from ..serializers import ConsumptionSerializer


LOGGER = logging.getLogger(__name__)


class SelfAssessmentBaseView(BenchmarkMixin, TemplateView):

    @staticmethod
    def decorate_with_opportunities(leafs):
        for consumption in Consumption.objects.with_opportunity():
            leaf = leafs.get(consumption.path, None)
            if leaf:
                # If the consumption is not in leafs,
                # we have cut out the tree at an icon or heading level.
                leaf[0]['consumption'] = \
                    ConsumptionSerializer().to_representation(consumption)

    def decorate_with_answers(self, leafs):
        for path, values in six.iteritems(leafs):
            try:
                consumption = Consumption.objects.get(path=path)
                answer = Answer.objects.filter(
                    question=consumption, response=self.sample).first()
                if answer:
                    values[0]['implemented'] = answer.text
                else:
                    values[0]['implemented'] = False
            except Consumption.DoesNotExist:
                # We have cut out the tree at an icon or heading level.
                pass

    def decorate_with_improvements(self, leafs):
        for path, values in six.iteritems(leafs):
            try:
                consumption = Consumption.objects.get(path=path)
                values[0]['planned'] = Improvement.objects.filter(
                    consumption=consumption, account=self.account).exists()
            except Consumption.DoesNotExist:
                # We have cut out the tree at an icon or heading level.
                pass

    def attach_benchmarks(self, rollup_tree):
        self._start_time()
        # We create the response if it does not exists.
        survey = SurveyModel.objects.get(title=self.report_title)
        self._sample, _ = Response.objects.get_or_create(
            account=self.account,
            survey=survey)
        leafs = self.get_leafs(rollup_tree)
        self._report_queries("leafs loaded")
        self.decorate_with_opportunities(leafs)
        self.decorate_with_answers(leafs)
        self.decorate_with_improvements(leafs)
        self._report_queries("leafs populated")


class SelfAssessmentView(SelfAssessmentBaseView):

    template_name = 'envconnect/self_assessment.html'
    breadcrumb_url = 'report'

    def get_breadcrumb_url(self, path):
        organization = self.kwargs.get('organization', None)
        if organization:
            return reverse('report_organization', args=(organization, path))
        return super(SelfAssessmentView, self).get_breadcrumb_url(path)

    def get_context_data(self, **kwargs):
        context = super(SelfAssessmentView, self).get_context_data(**kwargs)
        from_root, trail = self.breadcrumbs
        root = None
        if trail:
            root = self._build_tree(trail[-1][0], from_root, cut=None)
#XXX            root = self._cut_tree(root)
            self.attach_benchmarks(root)
            context.update({
                'root': root,
                'entries': json.dumps(root, cls=JSONEncoder)
            })
        organization = context['organization']
        context.update({
            'page_icon': self.icon,
            'response': self.sample,
            'survey': self.sample.survey,
            'role': "tab",
            'score_toggle': self.request.GET.get('toggle', False)})
        self.update_context_urls(context, {
            'api_self_assessment_response': reverse(
                'survey_api_response', args=(organization, self.sample)),
        })
        return context

    def get(self, request, *args, **kwargs):
        from_root, _ = self.breadcrumbs
        if not from_root or from_root == "/":
            return HttpResponseRedirect(reverse('homepage'))
        return super(SelfAssessmentView, self).get(request, *args, **kwargs)


class SelfAssessmentSpreadsheetView(SelfAssessmentBaseView):

    basename = 'self-assessment'

    @staticmethod
    def _get_consumption(element):
        return element.get('consumption', None)

    @staticmethod
    def _get_tag(element):
        return element.get('tag', "")

    @staticmethod
    def _get_title(element):
        return element.get('title', "")

    def insert_path(self, tree, parts=None):
        if not parts:
            return tree
        if not parts[0] in tree:
            tree[parts[0]] = {}
        return self.insert_path(tree[parts[0]], parts[1:])

    def writerow(self, row):
        self.csv_writer.writerow([
            rec.encode('utf-8') if six.PY2 else rec
            for rec in row])

    def write_tree(self, root, indent=''):
        """
        The *root* parameter looks like:
        (PageElement, [(PageElement, [...]), (PageElement, [...]), ...])
        """
        if not root[1]:
            # We reached a leaf
            consumption = self._get_consumption(root[0])
            row = [indent + self._get_title(root[0])]
            if consumption:
                for heading in self.get_headings(self._get_tag(root[0])):
                    if consumption.get('implemented', "") == heading:
                        row += ['X']
                    else:
                        row += ['']
            self.writerow(row)
        else:
            self.writerow([indent + self._get_title(root[0])])
            for element in six.itervalues(root[1]):
                self.write_tree(element, indent=indent + '  ')

    def get(self, *args, **kwargs): #pylint: disable=unused-argument
        # All self-assessment questions for an industry, regardless
        # of the actual from_path.
        # XXX if we do that, we shouldn't use from_root (i.e. system pages)
        _, trail = self.breadcrumbs
        trail_head = ("/"
            + trail[0][0].slug.decode('utf-8') if six.PY2 else trail[0][0].slug)
        from_trail_head = "/" + "/".join([
            element.slug.decode('utf-8') if six.PY2 else element.slug
            for element in self.get_full_element_path(trail_head)])
        root = self._build_tree(trail[0][0], from_trail_head, cut=None)
        self.attach_benchmarks(root)

        self.create_writer()
        self.writerow(["The Sustainability Project - Self-assessment"])
        self.writerow([self._get_title(root[0])])
        indent = ' '
        for nodes in six.itervalues(root[1]):
            self.writerow([indent + self._get_title(nodes[0])]
                + self.get_headings(self._get_tag(nodes[0])))
            for elements in six.itervalues(nodes[1]):
                self.write_tree(elements, indent=indent + ' ')
        resp = HttpResponse(self.flush_writer(), content_type=self.content_type)
        resp['Content-Disposition'] = 'attachment; filename="{}"'.format(
            self.get_filename())
        return resp

    @staticmethod
    def get_headings(tag):
        return list(Consumption.ASSESSMENT_CHOICES.get(tag,
            Consumption.ASSESSMENT_CHOICES.get('default')))


class SelfAssessmentCSVView(SelfAssessmentSpreadsheetView):

    content_type = 'text/csv'

    def writerow(self, row):
        self.csv_writer.writerow(row)

    def create_writer(self):
        if six.PY2:
            self.content = io.BytesIO()
        else:
            self.content = io.StringIO()
        self.csv_writer = csv.writer(self.content)

    def flush_writer(self):
        self.content.seek(0)
        return self.content

    def get_filename(self):
        return datetime.datetime.now().strftime(self.basename + '-%Y%m%d.csv')


class SelfAssessmentXLSXView(SelfAssessmentSpreadsheetView):

    content_type = \
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    def writerow(self, row):
        self.wsheet.append(row)

    def create_writer(self):
        self.wbook = Workbook()
        self.wsheet = self.wbook.active

    def flush_writer(self):
        content = io.BytesIO()
        self.wbook.save(content)
        content.seek(0)
        return content

    def get_filename(self):
        return datetime.datetime.now().strftime(self.basename + '-%Y%m%d.xlsx')
