# -*- coding: utf-8 -*-

"""cernopendata base Invenio configuration."""

from __future__ import absolute_import, print_function

from flask import Blueprint, current_app, escape, render_template, request
from flask_babelex import lazy_gettext as _
from flask_breadcrumbs import default_breadcrumb_root, register_breadcrumb
from flask_menu import register_menu
from speaklater import make_lazy_string


blueprint = Blueprint(
    'cernopendata',
    __name__,
    template_folder='templates',
    static_folder='static',
)

default_breadcrumb_root(blueprint, '.')


def lazy_title(text, *args):
    """Make tranlated string with escaped values from request view args."""
    return _(text, **{key: make_lazy_string(
        lambda: escape(request.view_args.get(key, ''))
    ) for key in args})


@blueprint.route('/')
@register_menu(blueprint, 'main.education', _('Education'), order=2,
               active_when=lambda: False,
               endpoint_arguments_constructor=lambda: {'_anchor': 'education'})
@register_menu(blueprint, 'main.research', _('Research'), order=3,
               active_when=lambda: False,
               endpoint_arguments_constructor=lambda: {'_anchor': 'research'})
@register_breadcrumb(blueprint, '.', _('Home'))
@register_breadcrumb(blueprint, '.education', _('Education'),
                     endpoint_arguments_constructor=lambda: {
                         '_anchor': 'education'})
@register_breadcrumb(blueprint, '.research', _('Research'),
                     endpoint_arguments_constructor=lambda: {
                         '_anchor': 'education'})
def index():
    """Home Page."""
    return render_template('cernopendata/index.html')


@blueprint.route('/education')
@blueprint.route('/education/<string:experiment>')
@register_breadcrumb(blueprint, '.education.experiment',
                     lazy_title('%(experiment)s', 'experiment'),
                     endpoint_arguments_constructor=lambda: {
                         'experiment': request.view_args['experiment']})
def education(experiment=None):
    """Display education pages."""
    if experiment not in current_app.config['OPENDATA_EXPERIMENTS']:
        abort(404)

    return render_template('cernopendata/education.html',
                           experiment=experiment)



@blueprint.route('/research')
@blueprint.route('/research/<string:experiment>')
@register_breadcrumb(blueprint, '.research.experiment',
                     lazy_title('%(experiment)s', 'experiment'),
                     endpoint_arguments_constructor=lambda: {
                         'experiment': request.view_args['experiment']})
def research(experiment=None):
    import os.path, pkg_resources

    def file_exists(filename):
        filepath = pkg_resources.resource_filename('cernopendata.base', filename)
        return os.path.isfile(filepath)

    def splitting(value, delimiter='/'):
        return value.split(delimiter)

    current_app.jinja_env.filters['splitthem'] = splitting
    current_app.jinja_env.filters['file_exists'] = file_exists

    exp_colls, exp_names = get_collections()

    if experiment not in exp_names :
        try:
            return render_template('index_scrollspy.html', entry = 'research', exp_colls = exp_colls, exp_names = exp_names)
        except TemplateNotFound:
            return abort(404)

    try:
        return render_template('research.html',
                               experiment=experiment, exp_colls = exp_colls, exp_names = exp_names)
    except TemplateNotFound:
        return abort(404)

@blueprint.route('/visualise/events/<string:experiment>')
def visualise_events(experiment = 'CMS'):

    exp_names = get_collection_names(['ALICE', 'LHCb', 'ATLAS'])

    breadcrumbs = [{},{'url':'.education','text':'Education'},\
                        {'url':'.education','text':'Visualise Events'}]
    try:
        return render_template('visualise_events.html', experiment = experiment, exp_names = exp_names, breadcrumbs = breadcrumbs)
    except TemplateNotFound:
        return abort(404)


@blueprint.route('/visualise/histograms/<string:experiment>')
def visualise_histo(experiment='CMS'):
    exp_colls, exp_names = get_collections()

    breadcrumbs = [{}, {'url':'.education','text':'Education'},
                        {'url':'.education','text':'Visualise Histograms'}]

    try:
        return render_template('visualise_histograms.html', experiment = experiment, exp_names = exp_names, breadcrumbs = breadcrumbs)
    except TemplateNotFound:
        return abort(404)


@blueprint.route('/getstarted', defaults={'experiment': None})
@blueprint.route('/<string:experiment>/getstarted')
@blueprint.route('/getstarted/<string:experiment>')
@blueprint.route('/getting-started', defaults={'experiment': None, 'year': None})
@blueprint.route('/getting-started/<string:experiment>',defaults={'year': None})
@blueprint.route('/getting-started/<string:experiment>/<string:year>')
@register_breadcrumb(blueprint, '.get_started', 'Get Started', \
                        dynamic_list_constructor = (lambda :\
                        [{'url':'.get_started','text':'Getting started'}]))
def get_started(experiment, year):
    def splitting(value, delimiter='/'):
        return value.split(delimiter)
    exp_names = get_collection_names()
    current_app.jinja_env.filters['splitthem'] = splitting

    try:
        return render_template('get_started.html', experiment=experiment,exp_names=exp_names, year=year)
    except TemplateNotFound:
        return abort(404)


@blueprint.route('/resources/<string:experiment>')
@blueprint.route('/resources', defaults={'experiment': None})
@register_breadcrumb(blueprint, '.resources', 'Learning Resources', \
                        dynamic_list_constructor = (lambda :\
                        [{'url':'.education','text':'Education'},\
                        {'url':'.resources','text':'Learning Resources'}]) )
def resources(experiment):
    exp_names = get_collection_names()

    try:
        return render_template('resources.html', experiment=experiment, exp_names=exp_names)
    except TemplateNotFound:
        return abort(404)


@blueprint.route('/VM', defaults={'experiment': None, 'year': None})
@blueprint.route('/VM/<string:experiment>', defaults={'year': None})
@blueprint.route('/VM/<string:experiment>/<string:year>')
@register_breadcrumb(blueprint, '.data_vms', 'Virtual Machines' , \
                        dynamic_list_constructor = (lambda :\
                        [{'url':'.data_vms','text':'Virtual Machines'}]) )
def data_vms(experiment, year):
    exp_names = get_collection_names(['ATLAS'])
    if experiment not in exp_names and experiment is not None:
        return render_template('404.html')

    def splitting(value, delimiter='/'):
        return value.split(delimiter)
    current_app.jinja_env.filters['splitthem'] = splitting

    try:
        return render_template('data_vms.html', experiment=experiment, exp_names=exp_names, year=year)
    except TemplateNotFound:
        return abort(404)

@blueprint.route('/VM/experiment/validation/report')
@register_breadcrumb(blueprint, '.val_report', 'VM', \
                        dynamic_list_constructor = (lambda :\
                        [{'url':'.data_vms','text':'Virtual Machines'},\
                        {'url':'.data_vms','text':'Validation Report'}]) )
def val_report(experiment):
    exp_names = get_collection_names()

    try:
        return render_template([experiment+'_VM_validation.html', 'data_vms.html'], experiment=experiment,exp_names=exp_names)
    except TemplateNotFound:
        return abort(404)


@blueprint.route('/about')
@blueprint.route('/about/<page>')
@register_menu(blueprint, 'main.about', _('About'), order=1)
@register_breadcrumb(blueprint, '.about', _('About'),
                     dynamic_list_constructor=lambda: [
                         {'url': '.about', 'text': 'About'}])
def about(page=None):
    """Render about page."""
    return render_template('cernopendata/about/index.html')
    # @blueprint.route('/about/CMS-Physics-Objects')


@blueprint.route('/terms-of-use')
def terms():
    return render_template('termsofuse.html')


@blueprint.route('/privacy-policy')
def privacy():
    return render_template('privacy.html')


@blueprint.route('/experiments')
def collections():
    import json, pkg_resources
    filepath = pkg_resources.resource_filename('cernopendata.base', 'templates/helpers/text/testimonials.json')
    with open(filepath,'r') as f:
        testimonials = json.load(f)

    def splitting(value, delimiter='/'):
        return value.split(delimiter)

    current_app.jinja_env.filters['splitthem'] = splitting

    exp_colls, exp_names = get_collections()

    try:
        return render_template('index_scrollspy.html', testimonials = testimonials, exp_colls = exp_colls, exp_names = exp_names)
    except TemplateNotFound:
        return abort(404)


@blueprint.route('/glossary', methods=['GET', 'POST'])
@register_breadcrumb(blueprint, '.glossary', 'Glossary', \
                        dynamic_list_constructor = (lambda :\
                        [{'url':'.education', 'text':'Education'},\
                        {'url':'.glossary','text':'Glossary'}]) )
def glossary():
    import json, pkg_resources
    filepath = pkg_resources.resource_filename('cernopendata.base', 'static/json/glossary.json')
    with open(filepath,'r') as f:
        glossary = json.load(f)

    try:
        return render_template('glossary.html', glossary = glossary)
    except TemplateNotFound:
        return abort('404')


@blueprint.route('/news')
@register_breadcrumb(blueprint,'.news','News', dynamic_list_constructor=(
    lambda: [{'url':'.news','text':'News'}]
))
def news():
    """Render news."""
    return render_template('cernopendata/pages/news.html')
