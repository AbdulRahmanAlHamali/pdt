"""PDT admin object list column functions."""
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


def tags(obj):
    """Tags.

    :param obj: taggable object

    :return: comma separated list of tag names for the given object
    :rtype: str
    """
    return ', '.join(item.tag.name for item in obj.tagged_items.all())


def ci_project_column(getter=lambda obj: obj.ci_project, order='ci_project__name', short_description=_('CI project')):
    """Get CI project column function.

    :param getter: function to get the CI project object for given context object
    :param order: order field name for column to be used for ordering

    :return: column function
    :rtype: callable
    """
    def column(self):
        ci_project = getter(self)
        return mark_safe(
            '<a href="{url}">{name}</a>'.format(
                url=reverse("admin:core_ciproject_change", args=(ci_project.id,)),
                name=ci_project.name))
    column.admin_order_field = order
    column.short_description = short_description
    return column


def case_column(getter=lambda obj: obj.case, order='case__id', short_description=_('Case')):
    """Get case column function.

    :param getter: function to get the Case object for given context object
    :param order: order field name for column to be used for ordering

    :return: column function
    :rtype: callable
    """
    def column(self):
        """Get case link."""
        case = getter(self)
        return mark_safe(
            '<a href="{local_url}">{id}</a>: <a href="{external_url}" target="_blank">{title}</a>'.format(
                external_url=case.url,
                local_url=reverse("admin:core_case_change", args=(case.id,)),
                id=case.id,
                title=case.title)
        )
    column.admin_order_field = order
    column.short_description = short_description
    return column


def release_column(getter=lambda obj: obj.release, order='release__number', short_description=_('Release')):
    """Return release column function.

    :param getter: function to get the Release object for given context object
    :param order: order field name for column to be used for ordering

    :return: column function
    :rtype: callable
    """
    def column(self):
        """Get release name."""
        release = getter(self)
        return mark_safe(
            '<a href="{url}">{name}</a>'.format(
                url=reverse("admin:core_release_change", args=(release.id,)),
                name=release)) if release else ''
    column.admin_order_field = order
    column.short_description = short_description
    return column


def migration_column(getter=lambda obj: obj.migration, order='migration__uid', short_description=_('Migration')):
    """Get CI project column function.

    :param getter: function to get the Migration object for given context object
    :param order: order field name for column to be used for ordering

    :return: column function
    :rtype: callable
    """
    def column(self):
        migration = getter(self)
        return mark_safe(
            '<a href="{url}">{name}</a>'.format(
                url=reverse("admin:core_migration_change", args=(migration.id,)),
                name=migration.uid)) if migration else ''
    column.admin_order_field = order
    column.short_description = short_description
    return column


def instance_column(getter=lambda obj: obj.instance, order='instance__name', short_description=_('Instance')):
    """Get instance column function.

    :param getter: function to get the Instance object for given context object
    :param order: order field name for column to be used for ordering

    :return: column function
    :rtype: callable
    """
    def column(self):
        instance = getter(self)
        return mark_safe(
            '<a href="{url}">{name}</a>'.format(
                url=reverse("admin:core_instance_change", args=(instance.id,)),
                name=instance.name))
    column.admin_order_field = order
    column.short_description = short_description
    return column
