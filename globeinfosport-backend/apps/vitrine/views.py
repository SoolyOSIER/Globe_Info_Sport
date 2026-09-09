"""Public anti-spam endpoints and editorial administration of site settings."""

from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.core.permissions import IsAdministrateur, IsEditeurOuPlus

from .models import AbonneNewsletter, FAQ, MessageContact, PageContenu, Partenaire
from .serializers import (
    AbonneNewsletterCreateSerializer,
    AbonneNewsletterSerializer,
    FAQPublicSerializer,
    FAQSerializer,
    MessageContactCreateSerializer,
    MessageContactSerializer,
    NewsletterUnsubscribeSerializer,
    PageContenuPublicSerializer,
    PageContenuSerializer,
    PartenairePublicSerializer,
    PartenaireSerializer,
)
from .throttles import PublicAnonThrottle, PublicReadThrottle


class PublicContactCreateView(generics.CreateAPIView):
    serializer_class = MessageContactCreateSerializer
    permission_classes = [AllowAny]
    throttle_classes = [PublicAnonThrottle]
    throttle_scope = "public"


class PublicNewsletterSubscriptionView(generics.CreateAPIView):
    serializer_class = AbonneNewsletterCreateSerializer
    permission_classes = [AllowAny]
    throttle_classes = [PublicAnonThrottle]
    throttle_scope = "public"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save()
        return Response(
            {"detail": "Votre abonnement est confirmé.", "email": subscription.email},
            status=status.HTTP_201_CREATED,
        )


class PublicNewsletterUnsubscribeView(generics.GenericAPIView):
    serializer_class = NewsletterUnsubscribeSerializer
    permission_classes = [AllowAny]
    throttle_classes = [PublicAnonThrottle]
    throttle_scope = "public"

    def post(self, request, token: str):
        subscription = get_object_or_404(AbonneNewsletter, token_desabonnement=token)
        subscription.actif = False
        subscription.save(update_fields=["actif", "updated_at"])
        return Response({"detail": "Votre désabonnement est confirmé."})


class PublicFAQListView(generics.ListAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQPublicSerializer
    permission_classes = [AllowAny]
    throttle_classes = [PublicReadThrottle]
    throttle_scope = "public-read"


class PublicPartenaireListView(generics.ListAPIView):
    queryset = Partenaire.objects.filter(actif=True)
    serializer_class = PartenairePublicSerializer
    permission_classes = [AllowAny]
    throttle_classes = [PublicReadThrottle]
    throttle_scope = "public-read"


class PublicPageContenuListView(generics.ListAPIView):
    queryset = PageContenu.objects.filter(actif=True)
    serializer_class = PageContenuPublicSerializer
    permission_classes = [AllowAny]
    throttle_classes = [PublicReadThrottle]
    throttle_scope = "public-read"


class MessageContactViewSet(viewsets.ModelViewSet):
    queryset = MessageContact.objects.all()
    serializer_class = MessageContactSerializer
    permission_classes = [IsEditeurOuPlus]
    http_method_names = ["get", "patch", "head", "options"]
    filterset_fields = ["traite"]
    search_fields = ["nom", "email", "sujet", "message"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]


class AbonneNewsletterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AbonneNewsletter.objects.all()
    serializer_class = AbonneNewsletterSerializer
    permission_classes = [IsEditeurOuPlus]
    filterset_fields = ["actif"]
    search_fields = ["email"]
    ordering_fields = ["created_at"]


class PartenaireViewSet(viewsets.ModelViewSet):
    queryset = Partenaire.objects.all()
    serializer_class = PartenaireSerializer
    permission_classes = [IsAdministrateur]


class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [IsEditeurOuPlus]


class PageContenuViewSet(viewsets.ModelViewSet):
    queryset = PageContenu.objects.all()
    serializer_class = PageContenuSerializer
    permission_classes = [IsAdministrateur]
