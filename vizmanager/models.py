import json
import os
import pdb
import urllib
import requests

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from colorfield.fields import ColorField

from microsite_backend import settings
from vizmanager.model_mixins import ModelDiffMixin


class Organization(models.Model):
    name = models.CharField(max_length=200, verbose_name=_('Name'))
    url = models.URLField(max_length=200, verbose_name=_('Url'), primary_key=True)

    class Meta:
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')

    def __str__(self):
        return '{}'.format(self.name)


class Phase(models.Model):
    name = models.CharField(max_length=200, verbose_name=_('Name'))
    url = models.URLField(max_length=200, verbose_name=_('Url'), primary_key=True)

    class Meta:
        verbose_name = _('Budget Phase')
        verbose_name_plural = _('Budget Phases')

    def __str__(self):
        return '{}'.format(self.name)


class Year(models.Model):
    name = models.CharField(max_length=200, verbose_name=_('Name'))
    url = models.URLField(max_length=200, verbose_name=_('Url'), primary_key=True)

    class Meta:
        verbose_name = _('Year')
        verbose_name_plural = _('Years')

    def __str__(self):
        return '{}'.format(self.name)


class Indicator(models.Model):
    name = models.CharField(max_length=200, verbose_name=_('Name'))
    indicator = models.CharField(max_length=200, verbose_name=_('indicator'))

    class Meta:
        verbose_name = _('Indicator')
        verbose_name_plural = _('Indicators')

    def __str__(self):
        return '{}'.format(self.name)


class KPI(models.Model):
    name = models.CharField(max_length=200, verbose_name=_('Name'))
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE,)
    year = models.ForeignKey(Year, on_delete=models.CASCADE,)
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE,)

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name = _('KPI')
        verbose_name_plural = _('KPIs')

    def embed_url(self):
        """
        Build URL to get to this dataset in OS Viewer
        :return: URL string
        """
        url = '{kpi_host}/embed?'.format(
            kpi_host=settings.KPI_HOST,

        )
        params = {
            'phase': self.phase.url,
            'year': self.year.url,
            'organization': self.organization.url
        }
        return '{}{}'.format(url, urllib.parse.urlencode(params))


class Municipality(models.Model):
    name = models.CharField(max_length=200, verbose_name=_('Name'))
    country = models.CharField(max_length=200, verbose_name=_('Country'))

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name = _('Municipality')
        verbose_name_plural = _('Municipalities')


class Profile(models.Model):
    """
    Class to add extra data to Django's user model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    municipality = models.ForeignKey(Municipality,
                                     verbose_name=_('Municipality'),
                                     on_delete=models.CASCADE,)

    def __str__(self):
        return '{}'.format(self.user.username)


class Microsite(models.Model):
    name = models.CharField(max_length=200, verbose_name=_('Name'))
    municipality = models.ForeignKey(Municipality,
                                     verbose_name=_('Municipality'),
                                     on_delete=models.CASCADE,)
    selected_theme = models.ForeignKey('Theme', blank=True, null=True,
                                       related_name='mock_microsite',
                                       on_delete=models.CASCADE,)
    language = models.CharField(max_length=2, default='en',
                                choices=(('en', 'en'), ('de', 'de'),
                                         ('es', 'es'),
                                         ('el', 'el'),),
                                verbose_name=_('Language'))
    forum_platform = models.CharField(max_length=20, default='Disqus',
                                      verbose_name=_('Forum'),
                                      choices=(('Disqus', 'Disqus'),
                                               ('No', 'No')))
    layout = models.CharField(max_length=200,
                              default='datasets list, forum right',
                              verbose_name=_('Layout'),
                              choices=(('datasets list, forum right',
                                        'datasets list, forum right'),
                                       ('datasets list, forum bottom',
                                        'datasets list, forum bottom'),
                                       ('datasets list, forum on flip',
                                        'datasets list, forum on flip'),))
    stacked_datasets = models.BooleanField(verbose_name=_('Stacked Datasets'),
                                           default=False)
    kpi_set = models.ManyToManyField(KPI, blank=True)

    render_from = models.CharField(max_length=200,
                                   default='OpenSpending',
                                   choices=(('OpenSpending', 'OpenSpending'),
                                            ('Babbage-ui', 'Babbage-ui'),))

    def create_forum(self):
        self.forum = Forum()
        self.forum.save()

    def save(self, *args, **kwargs):
        """
        Prior to saving the Microsite, create its Forum
        :param args: default args
        :param kwargs: default kwargs
        :return: None
        """
        super(self.__class__, self).save(*args, **kwargs)
        if not hasattr(self, 'forum'):
            self.create_forum()

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name = _('Microsite')
        verbose_name_plural = _('Microsites')


class Forum(models.Model):
    microsite = models.OneToOneField(Microsite, on_delete=models.CASCADE,)

    # def disqus_url(self):
    #    raise NotImplementedError

    def disqus_title(self):
        return '{}'.format(self.microsite.name)

    def disqus_identifier(self):
        # TODO: disambiguation for multiple instances of the Microsite service
        # we could (parts of) the production URL(?)
        return 'openbudgets-microsite-disqus-{}'.format(self.microsite.pk)


class Theme(models.Model):
    name = models.CharField(max_length=200, verbose_name=_('Name'))
    microsite = models.ForeignKey(Microsite, verbose_name=_('Microsite'),
                                  null=True,
                                  on_delete=models.CASCADE,)
    brand_color = ColorField(verbose_name=_('Brand Color'),
                                   default='#FFFFFF')
    sidebar_color = ColorField(verbose_name=_('Sidebar Color'),
                                     default='#888888')
    content_color = ColorField(verbose_name=_('Content Color'),
                                     default='#222222')

    def json(self):
        """
        Build the json representation of this theme that is needed by OS Viewer
        :return: JSON string
        """
        return json.dumps({
            'colors': {
                'brand': self.brand_color,
                'sidebar': self.sidebar_color,
                'content': self.content_color
            },
            'header': {},
            'footer': {},
            'socialMedia': {}
        })

    def create_theme_file(self):
        """
        Create the file representing this theme and save it to OS Viewer's
        themes folder
        :return: None
        """
        folder = '{}'.format(settings.OS_VIEWER_THEMES_FOLDER)

        # create the folder if it doesn't exist to avoid crashing
        if not os.path.exists(folder):
            os.makedirs(folder)

        file_path = '{folder}/{filename}.json'.format(
            folder=settings.OS_VIEWER_THEMES_FOLDER,
            filename=self.__str__())
        theme_file = open(file_path, 'w')
        theme_file.write(self.json())
        theme_file.close()

    def save(self, *args, **kwargs):
        """
        Prior to saving the theme, create its theme file
        :param args: default args
        :param kwargs: default kwargs
        :return: None
        """
        self.create_theme_file()
        super(self.__class__, self).save(*args, **kwargs)

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name = _('Theme')
        verbose_name_plural = _('Themes')


class Measure(models.Model):
    name = models.CharField(max_length=200, verbose_name=_('Name'))

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name = _('Measure')
        verbose_name_plural = _('Measures')


class Hierarchy(models.Model):
    name = models.CharField(max_length=200, verbose_name=_('Name'))

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name = _('Hierarchy')
        verbose_name_plural = _('Hierarchies')


class Dataset(ModelDiffMixin, models.Model):
    name = models.CharField(max_length=200, verbose_name=_('Name'))
    microsite = models.ForeignKey(Microsite, verbose_name=_('Microsite'),
                                  null=True, blank=True,
                                  on_delete=models.CASCADE,)
    code = models.CharField(max_length=200, verbose_name=_('Code'))
    viz_type = models.CharField(max_length=200,
                                choices=(
                                    ('Treemap', 'Treemap'),
                                    ('BarChart', 'BarChart'),
                                    ('PieChart', 'PieChart'),
                                    ('BubbleTree', 'BubbleTree'),
                                    ('Sankey', 'Sankey'),
                                    ('Radar', 'Radar'),
                                    ('PivotTable', 'PivotTable'),
                                    ('Table', 'Table')
                                ),
                                verbose_name=_('Visualization Type'))
    show_tables = models.BooleanField(default=False,
                                      verbose_name=_('Show Tables?'))
    initial_dimension = models.CharField(max_length=100, null=True)
    initial_measure = models.CharField(max_length=100, null=True)

    def save(self, *args, **kwargs):
        """
        Prior to saving a Dataset, make sure
        :param args: default args
        :param kwargs: default kwargs
        :return: None
        """
        try:
            # if the 'code' is changing to '', set it back to its original value
            old_value, new_value = self.get_field_diff('code')
            if new_value == '' and old_value not in ['', None]:
                self.code = old_value
        except TypeError:
            pass

        super(self.__class__, self).save(*args, **kwargs)

    def embed_url(self):
        """
        Build URL to get to this dataset in OS Viewer
        :return: URL string
        """
        url = '{os_viewer_host}/embed/{code}?'.format(
            os_viewer_host=settings.OS_VIEWER_HOST,
            code=self.code
        )
        params = {
            'lang': self.microsite.language,
            'theme': self.microsite.selected_theme,
            # 'order': 'Amount.sum|desc',
            'visualizations': self.viz_type,
            'groups[]': self.initial_dimension,
            'measure': '{}.sum'.format(self.initial_measure)
        }
        return '{}{}'.format(url, urllib.parse.urlencode(params))

    def get_hierarchies(self):
        """
        Lists the hierarchies of this dataset
        :return: dictionary of hierarchies
        """
        self.get_os_model()
        return self.os_model.get('hierarchies')

    def get_dimensions(self):
        """
        Lists the dimensions of this dataset
        :return: dictionary of dimensions
        """
        self.get_os_model()
        return self.os_model.get('dimensions')

    def get_measures(self):
        """
        Lists the dimensions of this dataset
        :return: dictionary of dimensions
        """
        self.get_os_model()
        return self.os_model.get('measures')

    def build_url(self, extra):
        """
        Put together the URL to be used in queries and apply the extra arguments
        received
        :param extra: string, usually a URL Query String like 'aggregate?cut=..'
        :return: string, fully formatted URL to be used
        """
        return '{os_api}/cubes/{dataset_code}/{extra}'\
            .format(os_api=settings.OS_API,
                    dataset_code=self.code,
                    extra=extra)

    def get_os_model(self):
        """
        Query OpenSpendings API to get the model related to this dataset
        :return: dictionary containing an OpenSpendings model
        """
        # if the OS model has not been downloaded yet, download it now and
        # return it, otherwise just return the saved version
        try:
            # os_model is already downloaded for this dataset
            return self.os_model
        except AttributeError:
            # os_model is not yet downloaded for this dataset

            if self.code == '':
                # missing code, just return an empty/default os_model
                self.os_model = {
                    'dimensions': {},
                    'measures': {},
                    'hierarchies': {}
                }
                return self.os_model

            # dataset with code, let's download the os_model
            response = requests.get(self.os_model_url())
            if response.status_code == 200:
                self.os_model = response.json().get('model')
            else:
                # response from babbage API got an error, probably it doesn't
                # contain this dataset's code
                raise RuntimeError(
                    'The configured OS_API is not working for this dataset.\n'
                    'Please check the settings.py file.\n'
                    'OS_API = {}.\n'
                    'Dataset code = {}'
                    .format(settings.OS_API, self.code))
        return self.os_model

    def os_model_url(self):
        """
        Helper method to build the URL string to query the OS model data
        :return: string, URL to query OS model
        """
        return self.build_url('model')

    def drilldown(self, hierarchy, cut):
        """
        Query OpenSpendings API to drilldown on given hierarchy and cut
        :return: dictionary containing subjects, money spend, etc
        """
        return NotImplementedError

    def build_tree(self, hierarchy):
        """
        Build the tree structure of the dataset on a given hierarchy
        :return: dictionary containing the tree
        """
        self.get_os_model()

        return NotImplementedError

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name = _('Dataset')
        verbose_name_plural = _('Datasets')
