from djongo import models

# # Create your models here.
# class Quantity(models.Model):
#     nbr = models.FloatField(default=0)
#     unit = models.CharField(max_length=200, default="unit")
#     def __str__(self):
#         return str({"nbr":self.nbr, "unit":self.unit})

#     @staticmethod
#     def fromDict(sourceDict):
#         quantity = Quantity()
#         quantity.nbr = sourceDict["nbr"]
#         quantity.unit = sourceDict["unit"]
#         return quantity

#     def isQuantityEnough(self, referenceQuantity, ratio=1):
#         ratioQuantitePresente   = self.nbr/(referenceQuantity.nbr*ratio)
#         quantiteManquante       = ratio*referenceQuantity.nbr - self.nbr
#         return (ratioQuantitePresente,Quantity.fromDict({"nbr":quantiteManquante,"unit":self.unit}))

# from .forms.QuantityForm import QuantityForm
# class Ingredient (models.Model):
#     name = models.CharField(max_length=200, default="ingredient", primary_key=True)
#     seasonal = models.NullBooleanField(default=False, blank=True)
#     quantity = models.EmbeddedModelField(model_container=Quantity,model_form_class=QuantityForm)

#     def __str__(self):
#         quantityDict={"name":self.name, "seasonal":self.seasonal, "quantity":eval(str(self.quantity))}
#         if hasattr(self, "seasonal") and self.seasonal is not None:
#             quantityDict["seasonal"]=self.seasonal
#         return str(quantityDict)

#     @staticmethod
#     def fromDict(sourceDict):
#         ingredient = Ingredient()
#         ingredient.name = sourceDict["name"]
#         if "seasonal" in sourceDict.keys():
#             ingredient.seasonal = sourceDict["seasonal"]
#         if "quantity" in sourceDict.keys():
#             ingredient.quantity = Quantity.fromDict(sourceDict["quantity"])

#         return ingredient

#     @staticmethod
#     def sumQuantitiesByIngredient(ingredientsList):
#         ingredientsDict={}
#         for ingredient in ingredientsList:
#             if ingredient.name not in ingredientsDict.keys():
#                 ingredientsDict[ingredient.name]=ingredient
#             else:
#                 summedIngredient = ingredientsDict[ingredient.name]
#                 assert(summedIngredient.quantity is not None and ingredient.quantity is not None)
#                 assert(summedIngredient.quantity.unit == ingredient.quantity.unit)
#                 summedIngredient.quantity.nbr += ingredient.quantity.nbr
#                 ingredientsDict[ingredient.name]=summedIngredient
#         return list(ingredientsDict.values())

# class Time (models.Model):
#     cooking = models.IntegerField(default=0)
#     preparation = models.IntegerField(default=0)
#     rest = models.IntegerField(default=0)
#     def __str__(self):
#         return str({"cooking":self.cooking, "preparation":self.preparation, "rest":self.rest})

#     @staticmethod
#     def fromDict(sourceDict):
#         time = Time()
#         time.cooking = sourceDict["cooking"]
#         time.preparation = sourceDict["preparation"]
#         time.rest = sourceDict["rest"]
#         return time

# from .forms.TimeForm import TimeForm
# from .forms.IngredientForm import IngredientForm
# class Recipe (models.Model):
#     name = models.CharField(max_length=200, default="name")
#     link = models.URLField(max_length=200, default="https://www.marmiton.org/recettes/recette_carottes-vichy_17717.aspx", primary_key=True)
#     img_link = models.URLField(max_length=200, default="https://assets.afcdn.com/recipe/20180208/77439_w648h414c1cx1200cy1800cxt0cyt0cxb2400cyb3600.jpg")
#     recipeType = models.CharField(max_length=200, default="recipeType")
#     servings = models.IntegerField(default=0)
#     difficulty = models.IntegerField(default=0)

#     ingredients = models.ArrayModelField(model_container=Ingredient,model_form_class=IngredientForm, default=list)

#     time=models.EmbeddedModelField(model_container=Time,model_form_class=TimeForm)

#     @staticmethod
#     def fromDict(sourceDict):
#         recipe = Recipe()
#         recipe.name = sourceDict["name"]
#         recipe.link = sourceDict["link"]
#         recipe.img_link = sourceDict["img_link"]
#         recipe.recipeType = sourceDict["recipeType"]
#         recipe.servings = sourceDict["servings"]
#         recipe.difficulty = sourceDict["difficulty"]

#         recipe.ingredients = sourceDict["ingredients"]

#         recipe.time=sourceDict["time"]

#         return recipe

#     def __str__(self):
#         recipeDict={"name":self.name, "link":self.link, "img_link":self.img_link, "recipeType":self.recipeType, "servings":self.servings, "difficulty":self.difficulty, "ingredients":[eval(str(i)) for i in self.ingredients], "time":eval(str(self.time))}
#         if hasattr(self, "priorities"):
#             recipeDict["priorities"]=[priorityLevel.toDict() for priorityLevel in self.priorities]
#         return str(recipeDict)
