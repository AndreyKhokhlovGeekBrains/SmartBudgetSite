from sqlalchemy.orm import Session

from app.models.service_addon import ServiceAddon


class ServiceAddonRepository:
    """
    Repository for service add-ons.

    Business rules:
    - Only active add-ons should be used in checkout.
    - Add-ons are selected by (family_slug, package_code, service_type).

    Side effects:
    - None. Pure DB access layer.

    Invariants/restrictions:
    - Assumes DB constraints enforce uniqueness of code.
    """

    @staticmethod
    def get_active_addon(
        db: Session,
        *,
        family_slug: str,
        package_code: str,
        service_type: str,
    ) -> ServiceAddon | None:
        """
        Get active add-on for given family/package/type.
        """

        return (
            db.query(ServiceAddon)
            .filter(ServiceAddon.is_active.is_(True))
            .filter(ServiceAddon.family_slug == family_slug)
            .filter(ServiceAddon.package_code == package_code)
            .filter(ServiceAddon.service_type == service_type)
            .one_or_none()
        )