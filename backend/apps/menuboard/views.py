from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle

from .board import board_payload, default_screen
from .models import MenuScreen


class _PerAddress(SimpleRateThrottle):
    def get_cache_key(self, request, view):
        return self.cache_format % {'scope': self.scope, 'ident': self.get_ident(request)}


class PairThrottle(_PerAddress):
    # 10,000 codes; this keeps guessing slow. A screen pairs once.
    scope = 'screen_pair'
    rate = '30/hour'


class HeartbeatThrottle(_PerAddress):
    # Every screen in the shop shares one address and checks in each minute.
    scope = 'screen_heartbeat'
    rate = '600/hour'


def _screen(slug):
    if slug == 'default':
        return default_screen()
    return get_object_or_404(MenuScreen, slug=slug)


@api_view(['GET'])
@permission_classes([AllowAny])
def board(request, slug):
    """The design, the live menu, promotions and opening status of a screen."""
    return Response(board_payload(_screen(slug), request))


@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([PairThrottle])
def pair(request, code):
    """/tv: the 4-digit code shown in the admin opens that screen."""
    screen = get_object_or_404(MenuScreen, code=str(code).strip())
    return Response({'slug': screen.slug, 'name': screen.name})


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([HeartbeatThrottle])
def heartbeat(request, slug):
    """Screens check in every minute, so the admin can show them as online."""
    screen = _screen(slug)
    if screen.pk:
        info = {key: str(request.data.get(key, ''))[:200] for key in ('width', 'height', 'agent', 'version')}
        MenuScreen.objects.filter(pk=screen.pk).update(last_seen_at=timezone.now(), last_seen_info=info)
    return Response({'reload_token': screen.reload_token})
