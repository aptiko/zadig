from django.utils.translation import ugettext as _
from zadig.core import portlets

portlets.append(
    { 'name': _(u"Navigation"),
      'tag': 'navigation', },
)
