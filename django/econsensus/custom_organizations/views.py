
from django.contrib.sites.models import get_current_site
from django.shortcuts import redirect

from organizations.views import OrganizationCreate, OrganizationUpdate, \
    OrganizationUserCreate, OrganizationUserUpdate, OrganizationUserDelete, OrganizationUserRemind
from guardian.shortcuts import remove_perm
from forms import CustomOrganizationAddForm, CustomOrganizationForm, \
        CustomOrganizationUserForm, CustomOrganizationUserAddForm



from organizations.backends import invitation_backend


from django.core.urlresolvers import reverse


class CustomOrganizationCreate(OrganizationCreate):
    form_class = CustomOrganizationAddForm

class CustomOrganizationUpdate(OrganizationUpdate):
    form_class = CustomOrganizationForm

    def get_success_url(self):
        return reverse("organization_list")

class CustomOrganizationUserRemind(OrganizationUserRemind):

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        invitation_backend().send_reminder(self.object.user,
                **{'domain': get_current_site(self.request),
                    'organization': self.organization, 'sender': request.user})
        return redirect(reverse("organization_user_list", args=[str(self.organization.id)]))



class CustomOrganizationUserUpdate(OrganizationUserUpdate):
    form_class = CustomOrganizationUserForm

    def get_initial(self):
        super(CustomOrganizationUserUpdate, self).get_initial()
        is_editor = self.object.user.has_perm('edit_decisions_feedback', self.object.organization)
        self.initial = {"is_editor":is_editor}
        return self.initial

class CustomOrganizationUserCreate(OrganizationUserCreate):
    form_class = CustomOrganizationUserAddForm

#Delete unused permissions!
class CustomOrganizationUserDelete(OrganizationUserDelete):
    def delete(self, *args, **kwargs):
        org_user = self.get_object()
        remove_perm('edit_decisions_feedback', org_user.user, org_user.organization)
        return super(CustomOrganizationUserDelete,self).delete(*args, **kwargs)
    
