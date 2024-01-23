def favorites_cart_check(self, obj, model):
    ''' Функция для проверки наличия рецепта в избранном и корзине. '''
    return (model.objects.filter(
            consumer__id=self.context.get('request').user.id,
            recipe__id=obj.id
            ).exists())
