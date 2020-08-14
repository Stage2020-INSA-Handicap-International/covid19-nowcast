from django.urls import include, path
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView


from . import views

urlpatterns = [
    path("",
        TemplateView.as_view(template_name="application.html"),
        name="app",
    ),
    path("dev/",
        TemplateView.as_view(template_name="dev_application.html"),
        name="dev_app",
    ),
    path(r'collector/',views.CollectorView.as_view()),
    path(r'topics/',views.TopicAnalysisView.as_view()),
    path(r'examples/',views.TopicExamplesView.as_view()),
    path(r'graph/',views.GraphAnalysisView.as_view()),
    path(r'category/',views.CategoryView.as_view()),
    path('testcookie/', views.cookie_session),
    path('deletecookie/', views.cookie_delete),
    path('create/', views.create_session),
    path('access/', views.access_session),
    path('delete/', views.delete_session),
]
