from django.core.urlresolvers import reverse
from django.db.models import Count, Sum

from funfactory import utils
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer

from mozillians.api.authenticators import AppAuthentication
from mozillians.api.authorisers import MozillaOfficialAuthorization
from mozillians.api.resources import (AdvancedSortingResourceMixIn,
                                      ClientCacheResourceMixIn,
                                      GraphiteMixIn)
from mozillians.api.paginator import Paginator
from mozillians.groups.models import Group, Skill


class GroupBaseResource(AdvancedSortingResourceMixIn, ClientCacheResourceMixIn,
                        GraphiteMixIn, ModelResource):
    number_of_members = fields.IntegerField(attribute='number_of_members',
                                            readonly=True)

    class Meta:
        authentication = AppAuthentication()
        authorization = MozillaOfficialAuthorization()
        cache_control = {'max-age': 0}
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        paginator_class = Paginator
        serializer = Serializer(formats=['json', 'jsonp'])
        fields = ['id', 'name', 'number_of_members']
        ordering = ['id', 'name', 'number_of_members']
        default_order = ['id']


class GroupResource(GroupBaseResource):
    url = fields.CharField()

    class Meta(GroupBaseResource.Meta):
        resource_name = 'groups'
        # This Sum hack counts the number of 1's in database, only
        # works with MySQL because it stores booleans as 0s and 1s
        queryset = (Group.objects
                    .annotate(number_of_members=Count('members'))
                    .filter(number_of_members__gt=0))

    def dehydrate_url(self, bundle):
        url = reverse('groups:show_group', args=[bundle.obj.url])
        return utils.absolutify(url)


class SkillResource(GroupBaseResource):

    class Meta(GroupBaseResource.Meta):
        resource_name = 'skills'
        queryset = (Skill.objects
                    .annotate(number_of_members=Sum('members__is_vouched'))
                    .filter(number_of_members__gt=0))
