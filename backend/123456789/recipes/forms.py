from django import forms

from .models import Ingredient

NUM_OF_LETTERS = 0


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ('name',)
        labels = {
            'name': ('А тут надо выбрать ингридиент')
        }
        help_texts = {
            'name': ('А тут надо выбрать ингридиент')
        }

    def clean_text(self):
        data = self.cleaned_data['text']
        max_length = len(data)
        if max_length <= NUM_OF_LETTERS:
            raise forms.ValidationError('Кажется ты что забыл сделать! '
                                        'Поле обязательно для заполнения')
        return data
