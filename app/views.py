from django.shortcuts import render # type: ignore

from django.views.generic import TemplateView # type: ignore

class HomePageView(TemplateView):
    template_name = 'app/home.html'

class AboutPageView(TemplateView):
    template_name = 'app/about.html'


