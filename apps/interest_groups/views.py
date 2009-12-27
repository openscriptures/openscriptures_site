from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _

from django.conf import settings

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

from interest_groups.models import InterestGroup
from interest_groups.forms import InterestGroupForm, InterestGroupUpdateForm

TOPIC_COUNT_SQL = """
SELECT COUNT(*)
FROM topics_topic
WHERE
    topics_topic.object_id = interest_groups_interestgroup.id AND
    topics_topic.content_type_id = %s
"""
MEMBER_COUNT_SQL = """
SELECT COUNT(*)
FROM interest_groups_interestgroup_members
WHERE interest_groups_interestgroup_members.interestgroup_id = interest_groups_interestgroup.id
"""

@login_required
def create(request, form_class=InterestGroupForm, template_name="interest_groups/create.html"):
    interest_group_form = form_class(request.POST or None)
    
    if interest_group_form.is_valid():
        interest_group = interest_group_form.save(commit=False)
        interest_group.creator = request.user
        interest_group.save()
        interest_group.members.add(request.user)
        interest_group.save()
        if notification:
            # @@@ might be worth having a shortcut for sending to all users
            notification.send(User.objects.all(), "interest_groups_new_interest_group",
                {"interest_group": interest_group}, queue=True)
        return HttpResponseRedirect(interest_group.get_absolute_url())
    
    return render_to_response(template_name, {
        "interest_group_form": interest_group_form,
    }, context_instance=RequestContext(request))


def interest_groups(request, template_name="interest_groups/interest_groups.html"):
    
    interest_groups = InterestGroup.objects.all()
    
    search_terms = request.GET.get('search', '')
    if search_terms:
        interest_groups = (interest_groups.filter(name__icontains=search_terms) |
            interest_groups.filter(description__icontains=search_terms))
    
    content_type = ContentType.objects.get_for_model(InterestGroup)
    
    interest_groups = interest_groups.extra(select=SortedDict([
        ('member_count', MEMBER_COUNT_SQL),
        ('topic_count', TOPIC_COUNT_SQL),
    ]), select_params=(content_type.id,))
    
    return render_to_response(template_name, {
        'interest_groups': interest_groups,
        'search_terms': search_terms,
    }, context_instance=RequestContext(request))


def delete(request, group_slug=None, redirect_url=None):
    interest_group = get_object_or_404(InterestGroup, slug=group_slug)
    if not redirect_url:
        redirect_url = reverse('interest_group_list')
    
    # @@@ eventually, we'll remove restriction that interest_group.creator can't leave interest group but we'll still require interest_group.members.all().count() == 1
    if (request.user.is_authenticated() and request.method == "POST" and
            request.user == interest_group.creator and interest_group.members.all().count() == 1):
        interest_group.delete()
        request.user.message_set.create(message=_("Interest group %(interest_group_name)s deleted.") % {"interest_group_name": interest_group.name})
        # no notification required as the deleter must be the only member
    
    return HttpResponseRedirect(redirect_url)


@login_required
def your_interest_groups(request, template_name="interest_groups/your_interest_groups.html"):
    return render_to_response(template_name, {
        "interest_groups": InterestGroup.objects.filter(members=request.user).order_by("name"),
    }, context_instance=RequestContext(request))


def interest_group(request, group_slug=None, form_class=InterestGroupUpdateForm,
        template_name="interest_groups/interest_group.html"):
    interest_group = get_object_or_404(InterestGroup, slug=group_slug)
    
    interest_group_form = form_class(request.POST or None, instance=interest_group)
    
    if not request.user.is_authenticated():
        is_member = False
    else:
        is_member = interest_group.user_is_member(request.user)
    
    action = request.POST.get('action')
    if action == 'update' and interest_group_form.is_valid():
        interest_group = interest_group_form.save()
    elif action == 'join':
        if not is_member:
            interest_group.members.add(request.user)
            request.user.message_set.create(
                message=_("You have joined the interest group %(interest_group_name)s") % {"interest_group_name": interest_group.name})
            is_member = True
            if notification:
                notification.send([interest_group.creator], "interest_groups_created_new_member", {"user": request.user, "interest_group": interest_group})
                notification.send(interest_group.members.all(), "interest_groups_new_member", {"user": request.user, "interest_group": interest_group})
        else:
            request.user.message_set.create(
                message=_("You have already joined interest group %(interest_group_name)s") % {"interest_group_name": interest_group.name})
    elif action == 'leave':
        interest_group.members.remove(request.user)
        request.user.message_set.create(message="You have left the interest_group %(interest_group_name)s" % {"interest_group_name": interest_group.name})
        is_member = False
        if notification:
            pass # @@@ no notification on departure yet
    
    return render_to_response(template_name, {
        "interest_group_form": interest_group_form,
        "interest_group": interest_group,
        "group": interest_group, # @@@ this should be the only context var for the interest_group
        "is_member": is_member,
    }, context_instance=RequestContext(request))
