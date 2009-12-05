# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django import template
from django.core.urlresolvers import reverse

from tracon.ticket_sales.views import ALL_PHASES

register = template.Library()

@register.simple_tag
def wizard_buttons(phase):
    button_template = template.loader.get_template("wizard_ui/buttons.html")
    context = template.Context(dict(phase=phase))
    return button_template.render(context)

@register.simple_tag
def progress_bar(request, current_phase):
    phases = [(phase, phase.index < current_phase.index, phase is current_phase) for phase in ALL_PHASES]

    progress_bar_template = template.loader.get_template(
        "wizard_ui/progress.html")
    context = template.Context(dict(phases=phases))
    return progress_bar_template.render(context)

@register.simple_tag
def show_errors(errors):
    error_template = template.loader.get_template("wizard_ui/errors.html")
    context = template.Context(dict(errors=errors))
    return error_template.render(context)

@register.simple_tag
def url_ptr(name):
    return reverse(name)
