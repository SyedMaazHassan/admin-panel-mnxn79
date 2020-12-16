from django.db import models
from datetime import datetime
from django.contrib.auth.models import User, auth
# Create your models here.


class SurveyInfo(models.Model):
    name = models.CharField(max_length=128)
    survey_id = models.IntegerField(unique=True)
    added_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='survey_owner')
    added_date = models.DateTimeField(auto_now_add=True,editable=False)
    token = models.CharField(max_length=255)
    
    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name_plural = 'SurveyInfo'

class Questions(models.Model):
    survey = models.ForeignKey(SurveyInfo,on_delete=models.CASCADE)
    question_text = models.CharField(max_length=255)
    questionId = models.IntegerField()

    class Meta:
        verbose_name_plural = 'Questions'

    def __str__(self):
        return f"{self.question_text} of {self.survey.name} survey"

class Answers(models.Model):
    question = models.ForeignKey(Questions,on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=255)
    answerId = models.IntegerField(blank=True,null=True)

    class Meta:
        verbose_name_plural = 'Answers'

    def __str__(self):
        return f"{self.question.question_text} answer"
