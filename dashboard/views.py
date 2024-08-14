from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render,redirect, get_object_or_404
from . forms import *
from django.views import generic
from .models import Notes,Homework
from youtubesearchpython import VideosSearch
import requests
from .forms import userRegistrationForm


def home(request):
    items = [
        {
            'name': 'Notes',
            'description': 'Create and manage your study notes',
            'url': 'notes',
            'image': 'images/notes.png'
        },
        {
            'name': 'Homework',
            'description': 'Track and complete your assignments',
            'url': 'homework',
            'image': 'images/home-work.jpg'
        },
        {
            'name': 'To-Do',
            'description': 'Manage your tasks and stay organized',
            'url': 'todo',
            'image': 'images/to-do.jpg'
        },
        {
            'name': 'YouTube',
            'description': 'Find educational videos for your studies',
            'url': 'youtube',
            'image': 'images/youtube.png'
        },
        {
            'name': 'Books',
            'description': 'Access your digital library',
            'url': 'books',
            'image': 'images/book.jpg'
        },
        {
            'name': 'Dictionary',
            'description': 'Look up definitions and improve your vocabulary',
            'url': 'dictionary',
            'image': 'images/dic.png'
        },
        {
            'name': 'Wikipedia',
            'description': 'Quick access to a wealth of information',
            'url': 'wiki',
            'image': 'images/wi-ki.jpg'
        },
        {
            'name': 'Conversion',
            'description': 'Convert units and measurements easily',
            'url': 'conversion',
            'image': 'images/conversion.jpg'
        }
    ]
    return render(request, 'dashboard/home.html', {'items': items})

@login_required
def notes(request): 
    if request.method == 'POST':
        form= NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user=request.user,title=request.POST['title'],desription=request.POST['desription'])
            notes.save() 
        messages.success(request,f"Notes Added by {request.user.username} Successfully")
    else:
        form=NotesForm()
    notes=Notes.objects.filter(user=request.user)
    context={'notes':notes,'form':form}
    return render(request,'dashboard/notes.html',context)

@login_required
def delete_note(request,pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect("notes")


class NotesDetailView(generic.DetailView):
    model = Notes

@login_required
def homework(request):
    if request.method == 'POST':
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST.get('is_finished', False)
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            homeworks = Homework(
                user=request.user,
                subject=request.POST['subject'],
                title=request.POST['title'],
                desription=request.POST['desription'],
                due=request.POST['due'],
                is_finished=finished
            )
            homeworks.save()
            messages.success(request, f"Homework added successfully by {request.user.username}")
    else:
        form = HomeworkForm()

    homework = Homework.objects.filter(user=request.user)
    homework_done = len(homework) == 0

    context = {
        'homeworks': homework,
        'homework_done': homework_done,
        'form': form,
    }
    return render(request, 'dashboard/homework.html', context)

@login_required
def update_homework(request,pk=None):
    homework=Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    return redirect('homework')

@login_required
def delete_homework(request,pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect("homework")

def youtube(request):
    if request.method == 'POST':
        form = Dashboardform(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            video = VideosSearch(text, limit=15) 
            result_list = []

            for i in video.result()['result']:
                result_dict = {
                    'input': text,
                    'title': i['title'],
                    'duration': i['duration'],
                    'thumbnail': i['thumbnails'][0]['url'],
                    'channel': i['channel']['name'],
                    'link': i['link'],
                    'views': i['viewCount']['short'],
                    'published': i['publishedTime'],
                }

                desc = ''
                if i['descriptionSnippet']:
                    for j in i['descriptionSnippet']:
                        desc += j['text']
                result_dict['description'] = desc

                result_list.append(result_dict)

            context = {
                'form': form,
                'results': result_list
            }

            return render(request, 'dashboard/youtube.html', context)
    else:
        form = Dashboardform()
    
    context = {'form': form}
    return render(request, 'dashboard/youtube.html', context)

@login_required
def todo(request):
    if request.method== 'POST':
        form=TodoForm(request.POST)
        if form.is_valid():
            try:
                finished=request.POST["is_finished"]
                if finished=='on':
                    finished=True
                else:
                    finished=False
                    
            except:
                finished=False
            todos= Todo(
                user=request.user,
                title=request.POST['title'],
                is_finished = finished
            )
            todos.save()
            messages.success(request,f"Todo Added succesfully by {request.user.username}")
    else:
        form=TodoForm()
    todo=Todo.objects.filter(user=request.user)
    if len(todo)==0:
        todos_done= True
    else:
        todos_done=False
    context={
        'form':form,
        'todos':todo,
        'todos_done':todos_done
    }
    return render(request,'dashboard/todo.html',context)

@login_required
def update_todo(request,pk=None):
    todo= Todo.objects.get(id=pk)
    todo.is_finished = not todo.is_finished
    todo.save()
    return redirect('todo')

@login_required
def delete_todo(request,pk=None):
    Todo.objects.get(id=pk).delete()
    return redirect("todo")

def books(request):
    form= Dashboardform()
    context={'form':form}
    return render(request,'dashboard/books.html')


def books(request):
    if request.method == 'POST':
        form = Dashboardform(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            url = 'https://www.googleapis.com/books/v1/volumes?q=' + text
            r = requests.get(url)
            answer = r.json()
            result_list = []

            # Check if 'items' key is in the response
            items = answer.get('items', [])
            num_items = min(len(items), 15)  # Ensure we do not go out of bounds

            for i in range(num_items):
                volume_info = items[i]['volumeInfo']
                result_dict = {
                    'title': volume_info.get('title'),
                    'subtitle': volume_info.get('subtitle'),
                    'description': volume_info.get('description'),
                    'count': volume_info.get('pageCount'),  # Fixed from 'count' to 'pageCount'
                    'categories': volume_info.get('categories'),
                    'rating': volume_info.get('averageRating'),  # Fixed from 'pageRating' to 'averageRating'
                    'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail'),
                    'preview': volume_info.get('previewLink'),
                }
                result_list.append(result_dict)

            context = {
                'form': form,
                'results': result_list
            }

            return render(request, 'dashboard/books.html', context)
    else:
        form = Dashboardform()
    
    context = {'form': form}
    return render(request, 'dashboard/books.html', context)

def dictionary(request):
    form = Dashboardform()
    context = {'form': form}  # Initialize context with the form

    if request.method == 'POST':
        form = Dashboardform(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            url = f'https://api.dictionaryapi.dev/api/v2/entries/en_US/{text}'
            r = requests.get(url)
            answer = r.json()

            try:
                # Initialize variables
                phonetics = None
                audio = None
                definition = None
                example = None
                synonyms = []

                # Get phonetics and audio
                if 'phonetics' in answer[0]:
                    phonetics = answer[0]['phonetics'][0].get('text', '')
                    # Iterate through phonetics to find audio
                    for phonetic in answer[0]['phonetics']:
                        if 'audio' in phonetic and phonetic['audio']:
                            audio = phonetic['audio']
                            break

                # Get definition and example
                if 'meanings' in answer[0]:
                    definition = answer[0]['meanings'][0]['definitions'][0].get('definition', '')
                    example = answer[0]['meanings'][0]['definitions'][0].get('example', '')

                    # Get synonyms if available
                    synonyms = answer[0]['meanings'][0]['definitions'][0].get('synonyms', [])

                context.update({
                    'input': text,
                    'phonetics': phonetics,
                    'audio': audio,
                    'definition': definition,
                    'example': example,
                    'synonyms': synonyms
                })
            except (IndexError, KeyError, TypeError):
                context.update({'input': ''})

    return render(request, 'dashboard/dictionary.html', context)


def wiki(request):
    results = []
    query = ''
    if request.method == 'POST':
        query = request.POST.get('query', '').strip()
        if query:
            url = f'https://en.wikipedia.org/w/api.php'
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': query,
                'utf8': 1
            }
            response = requests.get(url, params=params)
            data = response.json()
            results = [
                {
                    'title': item['title'],
                    'url': f'https://en.wikipedia.org/wiki/{item["title"].replace(" ", "_")}',
                    'snippet': item['snippet']
                }
                for item in data['query']['search']
            ]

    context = {
        'results': results,
        'query': query
    }
    return render(request, 'dashboard/wiki.html', context)

def conversion(request):
    result = None
    if request.method == 'POST':
        conversion_type = request.POST.get('conversion_type')
        input_value = request.POST.get('input_value')
        
        try:
            input_value = float(input_value)
            if conversion_type == 'cm_to_m':
                result = f"{input_value} centimeters is equal to {input_value / 100} meters."
            elif conversion_type == 'm_to_cm':
                result = f"{input_value} meters is equal to {input_value * 100} centimeters."
            elif conversion_type == 'kg_to_g':
                result = f"{input_value} kilograms is equal to {input_value * 1000} grams."
            elif conversion_type == 'g_to_kg':
                result = f"{input_value} grams is equal to {input_value / 1000} kilograms."
            elif conversion_type == 'l_to_ml':
                result = f"{input_value} liters is equal to {input_value * 1000} milliliters."
            elif conversion_type == 'ml_to_l':
                result = f"{input_value} milliliters is equal to {input_value / 1000} liters."
            elif conversion_type == 'f_to_c':
                result = f"{input_value} Fahrenheit is equal to {(input_value - 32) * 5 / 9:.2f} Celsius."
            elif conversion_type == 'c_to_f':
                result = f"{input_value} Celsius is equal to {(input_value * 9 / 5) + 32:.2f} Fahrenheit."
            elif conversion_type == 'mi_to_km':
                result = f"{input_value} miles is equal to {input_value * 1.60934:.2f} kilometers."
            elif conversion_type == 'km_to_mi':
                result = f"{input_value} kilometers is equal to {input_value / 1.60934:.2f} miles."
            elif conversion_type == 'inr_to_usd':
                response = requests.get('https://api.exchangerate-api.com/v4/latest/INR')
                data = response.json()
                rate = data['rates'].get('USD', 1)
                result = f"{input_value} Indian Rupees is equal to {input_value / rate:.2f} US Dollars."
            elif conversion_type == 'usd_to_inr':
                response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
                data = response.json()
                rate = data['rates'].get('INR', 1)
                result = f"{input_value} US Dollars is equal to {input_value * rate:.2f} Indian Rupees."
            elif conversion_type == 'eur_to_usd':
                response = requests.get('https://api.exchangerate-api.com/v4/latest/EUR')
                data = response.json()
                rate = data['rates'].get('USD', 1)
                result = f"{input_value} Euros is equal to {input_value * rate:.2f} US Dollars."
            elif conversion_type == 'usd_to_eur':
                response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
                data = response.json()
                rate = data['rates'].get('EUR', 1)
                result = f"{input_value} US Dollars is equal to {input_value * rate:.2f} Euros."
            elif conversion_type == 'gbp_to_usd':
                response = requests.get('https://api.exchangerate-api.com/v4/latest/GBP')
                data = response.json()
                rate = data['rates'].get('USD', 1)
                result = f"{input_value} British Pounds is equal to {input_value * rate:.2f} US Dollars."
            elif conversion_type == 'usd_to_gbp':
                response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
                data = response.json()
                rate = data['rates'].get('GBP', 1)
                result = f"{input_value} US Dollars is equal to {input_value * rate:.2f} British Pounds."
            elif conversion_type == 'jpy_to_usd':
                response = requests.get('https://api.exchangerate-api.com/v4/latest/JPY')
                data = response.json()
                rate = data['rates'].get('USD', 1)
                result = f"{input_value} Japanese Yen is equal to {input_value * rate:.2f} US Dollars."
            elif conversion_type == 'usd_to_jpy':
                response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
                data = response.json()
                rate = data['rates'].get('JPY', 1)
                result = f"{input_value} US Dollars is equal to {input_value * rate:.2f} Japanese Yen."
            elif conversion_type == 'aud_to_usd':
                response = requests.get('https://api.exchangerate-api.com/v4/latest/AUD')
                data = response.json()
                rate = data['rates'].get('USD', 1)
                result = f"{input_value} Australian Dollars is equal to {input_value * rate:.2f} US Dollars."
            elif conversion_type == 'usd_to_aud':
                response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
                data = response.json()
                rate = data['rates'].get('AUD', 1)
                result = f"{input_value} US Dollars is equal to {input_value * rate:.2f} Australian Dollars."
            elif conversion_type == 'cad_to_usd':
                response = requests.get('https://api.exchangerate-api.com/v4/latest/CAD')
                data = response.json()
                rate = data['rates'].get('USD', 1)
                result = f"{input_value} Canadian Dollars is equal to {input_value * rate:.2f} US Dollars."
            elif conversion_type == 'usd_to_cad':
                response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
                data = response.json()
                rate = data['rates'].get('CAD', 1)
                result = f"{input_value} US Dollars is equal to {input_value * rate:.2f} Canadian Dollars."
            # Add more conversion logic as needed
            
        except ValueError:
            result = "Invalid input. Please enter a valid number."
        except Exception as e:
            result = f"An error occurred: {e}"

    return render(request, 'dashboard/conversion.html', {'result': result})


def register(request):
    if request.method == 'POST':
        form = userRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = userRegistrationForm()
    
    context = {
        'form': form
    }
    return render(request, 'dashboard/register.html', context)

@login_required
def profile(request):
    # Filter only the uncompleted homeworks and todos for the current user
    homeworks = Homework.objects.filter(is_finished=False, user=request.user)
    todos = Todo.objects.filter(is_finished=False, user=request.user)

    # Determine if all homeworks and todos are completed
    homework_done = not homeworks.exists()
    todos_done = not todos.exists()

    context = {
        'homeworks': homeworks,
        'todos': todos,
        'homework_done': homework_done,
        'todos_done': todos_done
    }
    return render(request, 'dashboard/profile.html', context)

def update_todo(request, id):
    todo = get_object_or_404(Todo, id=id)
    if request.method == "POST":
        todo.is_finished = 'is_finished' in request.POST
        todo.save()
    return redirect('todo')

def update_homework(request, id):
    homework = get_object_or_404(Homework, id=id)
    if request.method == "POST":
        homework.is_finished = 'is_finished' in request.POST
        homework.save()
    return redirect('profile')