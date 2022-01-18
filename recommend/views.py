from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import render, get_object_or_404, redirect
from .forms import *
from django.http import Http404
from .models import Moviesss, Myrating, MyList
# from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponseRedirect
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# Create your views here.

def index(request):
    movies = list(Moviesss.objects.all())
    # query = request.GET.get('q')

    # if query:
    #     movies = Moviesss.objects.filter(Q(title__icontains=query)).distinct()
    #     return render(request, 'recommend/list.html', {'movies': movies})

    return render(request, 'recommend/list.html', {'movies': movies})


def detail(request, movies_id):

    if not request.user.is_authenticated:
            return redirect("login")
    if not request.user.is_active:
            raise Http404

    movies = get_object_or_404(Moviesss, id=movies_id)
    movie = Moviesss.objects.get(id=movies_id)

    try :

        
        temp = list(MyList.objects.all().values().filter(movies_id=movies_id,user=request.user))
        if temp:
            update = temp[0]['watch']
        else:
            update = False

        if request.method == "POST":
        
            # Saving the movie to My list
            if 'watch' in request.POST:
                
                watch_flag = request.POST['watch']
                if watch_flag == 'on':
                    update = True
                else:
                    update = False

                if MyList.objects.all().values().filter(movies_id=movies_id,user=request.user):
                    MyList.objects.all().values().filter(movies_id=movies_id,user=request.user).update(watch=update)
                else:
                    q=MyList(user=request.user,movies=movie,watch=update)
                    q.save()
                    
                if update:
                    messages.success(request, "Success! Movie added to your list!")
                else:
                    messages.success(request, "Success! Movie removed from your list!")

                
            # Rating
            else:
                rate = 0
                try :
                    rate = request.POST['rating']
 
                 
                    q=Myrating(user=request.user,movies=movie,rating=rate)
                    q.save()
                       
                    messages.success(request, "Success! Rating has been submitted!")

                except : 
                    messages.error(request, "Try Again ")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        out = list(Myrating.objects.filter(user=request.user.id).values())

        # Display ratings in the movie details page
        movie_rating = 0
        rate_flag = False
        for each in out:
            if each['movies_id'] == movies_id:
                movie_rating = each['rating']
                rate_flag = True
                break
        
        context = {'movies': movies,'movie_rating':movie_rating,'rate_flag':rate_flag,'update':update}
        return render(request, 'recommend/detail.html', context)
    except:
        messages.error(request, "Try Again ")
        context = {'movies': movies}
        return render(request, 'Failed recommend/detail.html', context)



# MyList 
def watch(request):

    if not request.user.is_authenticated:
        return redirect("login")
    if not request.user.is_active:
        raise Http404

    movies = Moviesss.objects.filter(mylist__watch=True,mylist__user=request.user)
    # query = request.GET.get('q')

    # if query:
    #     movies = Moviesss.objects.filter(Q(title__icontains=query)).distinct()
    #     return render(request, 'recommend/watch.html', {'movies': movies})

    return render(request, 'recommend/watch.html', {'movies': movies})


# Recommendation Algorithm

def combine_features(row):
    try:
        return row["keywords"] + " " + row["cast"] + " " + row["genres"] + " " + row["director"]
    except:
        print("Error", row)


def get_title_from_index(df,index):
    return df[df.index == index]["title"].values[0]

def get_index_from_title(df,title):
    return df[df.title == title]["id"].values[0]

def CheckMovie(df,title):
    for  i in df: 
        if str(i) == title:
            return False
    return True 

def recommend(request):
    
    try :
        if not request.user.is_authenticated:
            return redirect("login")

        if not request.user.is_active:
            raise Http404

        movie_rating=pd.DataFrame(list(Myrating.objects.all().values()))
        # new_user=movie_rating.user_id.unique().shape[0]
        # current_user_id= request.user.id

        user = pd.DataFrame(list(Myrating.objects.filter(user=request.user).values())).drop(['user_id','id'],axis=1)
        all_movies=pd.DataFrame(list(Moviesss.objects.values()))
        user_movie_list=list(Moviesss.objects.filter(id__in = user.movies_id))
        features = ["keywords", "cast", "genres", "director"]

        for feature in features:
            all_movies[feature] = all_movies[feature].fillna('')
            
        all_movies["combined_features"] = all_movies.apply(combine_features, axis=1)
        
        cv = CountVectorizer()
        count_matrix = cv.fit_transform(all_movies["combined_features"])
        cos_sim = cosine_similarity(count_matrix)

        movie_user_rate = str( Moviesss.objects.get(id=user.iloc[-1,0]))
        movie_index = get_index_from_title(all_movies,movie_user_rate)

        similar_movies = list(enumerate(cos_sim[movie_index]))
        sorted_similar_movies = sorted(similar_movies, key=lambda x: x[1], reverse=True)
        final=[]
        
        i = 0
        for movie in sorted_similar_movies:
            if  CheckMovie(list(user_movie_list),str(get_title_from_index(all_movies,movie[0]))):
                final.append(movie[0])
                i = i + 1
                if i > 5:
                    break
        movie_list=list(Moviesss.objects.filter(  id__in = final ))
        context = {'movie_list':movie_list }


        return render(request, 'recommend/recommend.html', context)
    except Exception as e:
        return render(request, 'recommend/recommend.html', {'movie_list':[],'warning':'please rate a movie first'})



# Register 
def signUp(request):
    form = UserForm(request.POST or None)

    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("index")

    context = {'form': form}

    return render(request, 'recommend/signUp.html', context)


# Login 
def Login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("index")
            else:
                return render(request, 'recommend/login.html', {'error_message': 'Your account disable'})
        else:
            return render(request, 'recommend/login.html', {'error_message': 'Invalid Login'})

    return render(request, 'recommend/login.html')


# Logout user
def Logout(request):
    logout(request)
    return redirect("login")
