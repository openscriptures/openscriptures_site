from django import template
from interest_groups.forms import InterestGroupForm

register = template.Library()


@register.inclusion_tag("interest_groups/interest_group_item.html", takes_context=True)
def show_interest_group(context, interest_group):
    return {'interest_group': interest_group, 'request': context['request']}

# @@@ should move these next two as they aren't particularly interest-group-specific

@register.simple_tag
def clear_search_url(request):
    getvars = request.GET.copy()
    if 'search' in getvars:
        del getvars['search']
    if len(getvars.keys()) > 0:
        return "%s?%s" % (request.path, getvars.urlencode())
    else:
        return request.path


@register.simple_tag
def persist_getvars(request):
    getvars = request.GET.copy()
    if len(getvars.keys()) > 0:
        return "?%s" % getvars.urlencode()
    return ''