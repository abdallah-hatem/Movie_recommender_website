from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User

from django.utils.translation import gettext as _
# Create your models here.


class Moviesss(models.Model):

    title = models.CharField(("title"), max_length=2000)
    genres = models.CharField(("genres"), max_length=2000)
    keywords = models.CharField(("keywords"), max_length=2000)
    cast = models.CharField(("cast"), max_length=2000)
    director = models.CharField(("director"), max_length=2000)
    images = models.CharField(("images"), max_length=2000)


    def __str__(self):
        return self.title



class Myrating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movies = models.ForeignKey(Moviesss, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0, validators=[MaxValueValidator(5), MinValueValidator(0)])



class MyList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    watch = models.BooleanField(default=False)
    movies = models.ForeignKey(Moviesss, on_delete=models.CASCADE)




# class Moviess(models.Model):

#     title = models.CharField(("title"), max_length=2000)
#     genres = models.CharField(("genres"), max_length=2000)
#     keywords = models.CharField(("keywords"), max_length=2000)
#     cast = models.CharField(("cast"), max_length=2000)
#     director = models.CharField(("director"), max_length=2000)
#     imagess = models.CharField(("images"), max_length=2000)


#     def __str__(self):
#         return self.title



# class Movies(models.Model):


#     budget= models.BigIntegerField(_("budget"))
#     genres=  models.CharField(_("genres"),max_length=2000)
#     homepage=models.CharField(_("homepage"),max_length=2000)
#     keywords=models.CharField(_("keywords"),max_length=2000)
#     original_language=models.CharField(_("original_language"),max_length=2000)
#     original_title= models.CharField(_("original_title"),max_length=2000)
#     overview= models.CharField(_("overview"),max_length=2000)
#     popularity	=models.FloatField(_("popularity"))
#     release_date = models.CharField(_("release_date"),max_length=2000)
#     tagline	=models.CharField(_("tagline"),max_length=2000)
#     title	=models.CharField(_("title"),max_length=2000)
#     vote_average	=models.IntegerField(_("vote_average"))
#     cast=models.CharField(_("cast"),max_length=2000)
#     director=models.CharField(_("director"),max_length=2000)

#     def __str__(self):
#         return self.title
# class Movie(models.Model):
#     title = models.CharField(max_length=200)
#     genre = models.CharField(max_length=100)
#     movie_logo = models.FileField()

#     def __str__(self):
#         return self.title







