import json as js

with open('ingredients.json', 'r', encoding='utf-8') as src:
    items = js.load(src)

result = [{
    'model': 'recipes.ingredient',
    'pk': i + 1,
    'fields': elem
} for i, elem in enumerate(items)]

with open('ingredients_result.json', 'w', encoding='utf-8') as dest:
    js.dump(result, dest, indent=4, ensure_ascii=False)
