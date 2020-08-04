from django.urls import include, path
# from rest_framework import routers
# from .views import  IngredientViewSet, RecipeViewSet, OCRView
# from .SearchView import SearchView
# from .RecipeStepsView import RecipeStepsView
# from .SeasonUpdateView import SeasonUpdateView
# router = routers.DefaultRouter()
# router.register(r'ingredient', IngredientViewSet)
# router.register(r'recipe', RecipeViewSet)

from . import views

urlpatterns = [
    path('',views.index)
    # path('', include(router.urls)),
    # path(r'search/', SearchView.as_view()),
    # path(r'recipeSteps/', RecipeStepsView.as_view()),
    # path(r'seasonUpdate/', SeasonUpdateView.as_view())
]
