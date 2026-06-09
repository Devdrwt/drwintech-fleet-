from rest_framework.routers import DefaultRouter

from .views import GpsUnitViewSet, SimCardViewSet, SimRechargeViewSet, VehicleViewSet

router = DefaultRouter()
router.register("fleet/vehicles", VehicleViewSet, basename="vehicle")
router.register("fleet/units", GpsUnitViewSet, basename="gpsunit")
router.register("fleet/sim-cards", SimCardViewSet, basename="simcard")
router.register("fleet/recharges", SimRechargeViewSet, basename="simrecharge")

urlpatterns = router.urls
