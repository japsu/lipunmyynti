# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django import template

register = template.Library()

@register.simple_tag
def wizard_buttons():
    button_template = template.loader.get_template("wizard_ui/buttons.html")
    context = template.Context({})
    return button_template.render(context)

@register.simple_tag
def progress_bar():
    progress_bar_template = template.loader.get_template(
        "wizard_ui/progress.html")
    context = template.Context({})
    return progress_bar_template.render(context)
