from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.http import HttpResponse
from django.http import JsonResponse
import json
import requests
from django.views import generic
from django.contrib import messages

# main page function

def index(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return redirect('admin-panel')


# function for signup

def signup(request):
    if request.method == "POST":
        name = request.POST['name']
        l_name = request.POST['l_name']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        context = {
            "name":name,
            "l_name":l_name,
            "email":email,
            "pass1":pass1,
            "pass2":pass2,
        }
        if pass1==pass2:
            if User.objects.filter(username=email).exists():
                print("Email already taken")
                messages.info(request, "Entered email already in use!")
                context['border'] = "email" 
                return render(request, "signup.html", context)

            user = User.objects.create_user(username=email, first_name=name, password=pass1, last_name=l_name)
            user.save()
            
            return redirect("login")
        else:
            messages.info(request, "Your pasword doesn't match!")
            context['border'] = "password"
            return render(request, "signup.html", context)


    
    return render(request, "signup.html")


# function for login

def login(request):

    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        context = {
            'email': email,
            'password': password
        }
        user = auth.authenticate(username=email, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect("index")
        else:
            messages.info(request, "Incorrect login details!")
            return render(request, "login.html", context)
            # return redirect("login")
    else:
        return render(request, "login.html")


# function for logout

def logout(request):
    auth.logout(request)
    return redirect("index")


def surveyform(request):
    # adding the survey 
    if request.method == 'POST':
        survey_name = request.POST['survey_name']
        survey_id = request.POST['id']
        token = request.POST['token']
        headers={
            'Authorization':f'bearer {token}',
            'Content-Type':'application/json'
        }
        url = f'https://api.surveymonkey.com/v3/surveys/{survey_id}/details'
        res = requests.get(url,headers=headers)
        data = res.json()
        # incase if info given is incorrect
        try:
            if data['error']:
                messages.warning(request,'Invalid token or survey do not exist')
                return redirect('add-survey')
        # with correct info        
        except:    
            survey = SurveyInfo.objects.create(name=survey_name,survey_id=survey_id,
                    added_by=request.user,token=token)
            # adding question to db along with all possible answers with the question        
            def func1(n):
                print(n)
                qus = Questions.objects.create(survey=survey,
                question_text=n['headings'][0]['heading']
                ,questionId=n['id'])
                try:
                    for i in range(len(n['answers']['choices'])):
                        print(i)
                        ans = Answers.objects.create(question=qus
                                ,answer_text=n['answers']['choices'][i]['text'],answerId=n['answers']['choices'][i]['id'])
                except:
                    pass
            x= list(map(func1,data['pages'][0]['questions']))
            print(x)
    return redirect('admin-panel')

# display on the admin page 
class SurveyList(generic.ListView):
    model = SurveyInfo
    context_object_name = 'survey_lists'
    template_name = 'index.html'

    def get_queryset(self):
        # token = '5CnOFq7JYDCGQW4B4sOhn6CguczPwtlytfQ.tSmpGJ2O2DO02vHUQ1j69dLRhgA6ZHwrbGdZfPMSkhQ8AOEMFHvFDFfgFPHpCfyonqTG62A9nXEFRUSraqt7J01S1kqw'
        # headers={
        #     'Authorization':f'bearer {token}',
        #     'Content-Type':'application/json'
        # }
        # x = requests.get('https://api.surveymonkey.com/v3/surveys',headers=headers)
        # print(x.json())
        return SurveyInfo.objects.filter(added_by=self.request.user)


def my_function(headers,href,qs_list,ans_list,pk):
    # query database for response id and put this whole code on loop
    url = href+'/details'
    res = requests.get(url, headers=headers)
    print(url)
    data = res.json()
    page = data['pages'][0]['questions']
    # getting the particular question id with answer id
    question_id = []
    answer_choice_id = []
    essay_style_q_id=[]
    essay_style_ans=[]
    final_dict = {}
    # making list of question id and answer id for which we have to get the text from survey detail url
    
    for i in range(0,len(page)):
        try:
            # for choice bsaed question ids and answer ids
            if page[i]['answers'][0]['choice_id']:
                question_id.append(page[i]['id'])
                answer_choice_id.append(page[i]['answers'][0]['choice_id'])
        except:
            #for essay style question ids and answer texts
            x = Questions.objects.filter(questionId=page[i]['id'])
            print(x,pk,page[i]['id' ])
            final_dict[x[0].question_text] = page[i]['answers'][0]['text']
            essay_style_q_id.append(page[i]['id'])
            essay_style_ans.append(page[i]['answers'][0]['text'])
    # getting the common ids so we cn query db to get the text from db
    final_ans_list = list(set(ans_list).intersection(set(answer_choice_id)))        
    final_qs_list = list(set(qs_list).intersection(set(question_id))) 
    final_qs_list.sort()     
    final_ans_list.sort()
    # making the final dict
    for i in range(0,len(final_ans_list)):
        x = Questions.objects.filter(questionId=final_qs_list[i],survey_id=pk)
        y = Answers.objects.filter(answerId=final_ans_list[i])
        final_dict[x[0].question_text] = y[0].answer_text

    # this whole code block to get the inline response if some questions are missing
    qs_dict_db = Questions.objects.filter(survey_id=pk)
    keys = [*final_dict]
    new_final_dict = {}
    for i in range(0,len(qs_dict_db)):
        try:
            if qs_dict_db[i].question_text != keys[i]:
                new_final_dict[qs_dict_db[i].question_text] = 'Not provided'  
            else:
                new_final_dict[qs_dict_db[i].question_text] = final_dict[keys[i]]
        except:
            if i == len(qs_dict_db)-1:
                new_final_dict.popitem()
                dict3 = {**new_final_dict,**final_dict}
                print(dict3)
                return dict3
    print(new_final_dict)            
    return new_final_dict



def checkresponses(request,**kwargs):

    # get survey id from db
    survey_id = SurveyInfo.objects.get(pk=kwargs['pk'])
    # defining headers to use ahead
    headers = {
        'Authorization': "bearer %s" % survey_id.token,
        'Content-Type': 'application/json'
    }
    #get questions from the survey pk
    question_list = Questions.objects.filter(survey_id=kwargs['pk'])
    #getting the questions value
    question_value = Questions.objects.filter(survey_id=kwargs['pk']).values_list('questionId').distinct()
    def to_list(n):
        try:
            return str(n[0])
        except:
            pass    
    # making a list of questions id value    
    question_value_list = list(map(to_list,question_value))
    answer_list = []
    # get all answers from the question id
    for i in question_list:
        answer_list.append(Answers.objects.filter(question_id=i.pk).values_list('answerId'))
    # making list of answers tuple(by list comprehension twice)
    out = [x for i in answer_list for x in i]
    out2 = [str(y) for i in out for y in i]
    # getting a survey response from the id in the db
    res_id = requests.get(f'https://api.surveymonkey.com/v3/surveys/{survey_id.survey_id}/responses',headers=headers)
    x = res_id.json()
    final_ans = []
    # for all responses in the survey response
    try:
        for i in range(0,len(x['data'])):
            final_ans.append(my_function(headers,x['data'][i]['href'],question_value_list,out2,kwargs['pk']))

    except:
        render(request,'admin-panel/tables.html')    
    return render(request,'admin-panel/tables.html',{'ctx':final_ans,'name':SurveyInfo.objects.get(pk=kwargs['pk'])}) 

