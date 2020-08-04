from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
# from .models import Ingredient, Recipe, Quantity, Time
# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from .serializers import IngredientSerializer, RecipeSerializer, QuantitySerializer, TimeSerializer

# from ocr.ocr import newIngredient,OCR
import json

from django.shortcuts import render_to_response
from django.template import RequestContext


def index(request):
    return render_to_response('index.html')


# class IngredientViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     queryset = Ingredient.objects.all()
#     serializer_class = IngredientSerializer
#     filterset_fields = ('seasonal', 'name', )

#     def create(self, request, *args, **kwargs):
#         """
#         #checks if post request data is an array initializes serializer with many=True
#         else executes default CreateModelMixin.create function 
#         """
#         is_many = isinstance(request.data, list)
#         if not is_many:
#             return super(IngredientViewSet, self).create(request, *args, **kwargs)
#         else:
#             serializer = self.get_serializer(data=request.data, many=True)
#             serializer.is_valid(raise_exception=True)
#             self.perform_create(serializer)
#             headers = self.get_success_headers(serializer.data)
#             return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

# class RecipeViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """
#     queryset = Recipe.objects.all()
#     serializer_class = RecipeSerializer
#     filterset_fields = ('name', 'recipeType', 'difficulty', 'servings')

# class OCRView (View):
#     @csrf_exempt
#     def post(self, request):
#         with open('ocr/ingredients_list.json','r') as ingredientsListFile:
#             jsonIngredientList = json.load(ingredientsListFile)
#         imageToAnalyze = request.FILES["toAnalyze"]
#         response = OCR.runOCR(imageToAnalyze,jsonIngredientList)
#         print ("--------------------------")
#         print(response)
#         return HttpResponse(json.dumps((response),ensure_ascii=False))

#     def create(self, request, *args, **kwargs):
#         """
#         #checks if post request data is an array initializes serializer with many=True
#         else executes default CreateModelMixin.create function 
#         """
#         is_many = isinstance(request.data, list)
#         if not is_many:
#             return super(RecipeViewSet, self).create(request, *args, **kwargs)
#         else:
#             serializer = self.get_serializer(data=request.data, many=True)
#             serializer.is_valid(raise_exception=True)
#             self.perform_create(serializer)
#             headers = self.get_success_headers(serializer.data)
#             return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
# class OCRView (View):
#     @csrf_exempt
#     def post(self, request):
#         with open('ocr/ingredients_list.json','r') as ingredientsListFile:
#             jsonIngredientList = json.load(ingredientsListFile)
#         imageToAnalyze = request.FILES["toAnalyze"]
#         response = OCR.runOCR(imageToAnalyze,jsonIngredientList)
#         print ("--------------------------")
#         print(response)
#         return HttpResponse(json.dumps((response),ensure_ascii=False))
