from django.contrib import admin
from .models import Municipality, Profile, Microsite, Theme, Dataset
from .forms import DatasetForm
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.html import escape


class MicroAdminSite(admin.AdminSite):
    site_header = 'Microsite Administrators'


class UserProfileInline(admin.StackedInline):
    verbose_name = 'Additional information for'
    model = Profile
    max_num = 1
    can_delete = False


class ProfileUserAdmin(UserAdmin):
    inlines = [UserProfileInline]


class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country',)
    list_editable = ('country',)

    class Meta:
        model = Dataset


class DatasetAdmin(admin.ModelAdmin):
    form = DatasetForm
    list_display = ('name', 'microsite', 'code', 'viz_type',)
    list_editable = ('microsite', 'code', 'viz_type',)

    fieldsets = (
        ('Name and Site', {
            'fields': ('name', 'microsite'),
            'description': escape('Enter a name for this dataset and relate the dataset to a microsite.'),
        }),
        ('Data and Visualization', {
            'description': escape('Search for a dataset code in OpenSpending and select a visualization strategy.'),
            'fields': ('code', 'viz_type', 'initial_dimension', ),
        }),
    )

    def get_queryset(self, request):
        # Restrict queryset to only show Datasets belonging to the same
        # municipality as the user
        qs = super(self.__class__, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(microsite__municipality=request.user.profile.municipality)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Restrict select box to only show microsites related to the same
        # municipality as the user
        if request.user.is_superuser:
            return super(self.__class__, self)\
                .formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'microsite':
            kwargs['queryset'] = Microsite.objects.filter(
                municipality=request.user.profile.municipality)
        return super(self.__class__, self).formfield_for_foreignkey(db_field, request, **kwargs)

    class Meta:
        model = Dataset


class ThemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'microsite', 'brand_color', 'sidebar_color',
                    'content_color',)
    list_editable = ('microsite', 'brand_color', 'sidebar_color',
                     'content_color',)
    fieldsets = (
        ('Name and Site', {
            'fields': ('name', 'microsite')
        }),
        ('Colors', {
            'fields': ('brand_color', 'sidebar_color', 'content_color'),
        }),
    )


    def get_queryset(self, request):
        # Restrict queryset to only show Themes belonging to the same
        # municipality as the user
        qs = super(self.__class__, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(
            microsite__municipality=request.user.profile.municipality)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Restrict select box to only show microsites related to the same
        # municipality as the user
        if request.user.is_superuser:
            return super(self.__class__, self)\
                .formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'microsite':
            kwargs['queryset'] = Microsite.objects.filter(
                municipality=request.user.profile.municipality)
        return super(self.__class__, self)\
            .formfield_for_foreignkey(db_field, request, **kwargs)

    class Meta:
        model = Theme


class MicrositeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'municipality', 'selected_theme', 'language',
                    'forum_platform', 'layout', 'stacked_datasets',
                    'render_from')
    list_editable = ('name', 'selected_theme', 'language', 'forum_platform', 'layout',
                     'stacked_datasets', 'render_from')
    readonly_fields = ('id', )

    def get_queryset(self, request):
        # Restrict queryset to only show Microsites belonging to the same
        # municipality as the user
        qs = super(self.__class__, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(municipality=request.user.profile.municipality)

    def get_form(self, request, obj=None, **kwargs):
        # Trick to allow filtering the selected_theme drop-down to only show
        # themes that belong to this Microsite
        self.instance = obj
        return super(self.__class__, self).get_form(request, obj=obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        # Core part of the trick (selected_theme drop-down trick)
        try:
            if db_field.name == 'selected_theme' and self.instance:
                kwargs['queryset'] = \
                    Theme.objects.filter(microsite=self.instance)
        except:
            pass

        if request.user.is_superuser:
            return super(self.__class__, self)\
                .formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'municipality':
            kwargs['queryset'] = Municipality.objects\
                .filter(id=request.user.profile.municipality_id)

        return super(self.__class__, self)\
            .formfield_for_foreignkey(db_field, request, **kwargs)

    class Meta:
        model = Microsite


ma_site = MicroAdminSite(name='municipalityadmin')
ma_site.register(Municipality, MunicipalityAdmin)
ma_site.register(Microsite, MicrositeAdmin)
ma_site.register(Theme, ThemeAdmin)
ma_site.register(Dataset, DatasetAdmin)

# un-register unmodified UserAdmin and register ProfileUserAdmin from above
admin.site.unregister(User)
admin.site.register(User, ProfileUserAdmin)

# standard registrations
admin.site.register(Municipality, MunicipalityAdmin)
admin.site.register(Microsite, MicrositeAdmin)
admin.site.register(Theme, ThemeAdmin)
admin.site.register(Dataset, DatasetAdmin)
