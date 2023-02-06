from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView,DeleteView, FormView
from django.urls import reverse_lazy
from .models import Task

from django.contrib.auth.views import LoginView

from django.contrib.auth.mixins import LoginRequiredMixin       #this prevent unknown user to perform certain tasks
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
# Create your views here.

#LOGIN VIEW IN REACT ITS CALLED COMPONENT
class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True    #Redirecting the user if not login
    
    def get_success_url(self):
        return reverse_lazy('tasks')
    
#using built in usercreation form to do the magic for our register form
class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')
    
    def form_valid(self, form):              #valid the form submit
        user = form.save()
        if user is not None:               #if user is authenticated go ahead and use the login page
             login(self.request, user)
        return super(RegisterPage, self).form_valid(form)
    
    def get(self, *arg, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*arg, **kwargs)

class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'
    
    #A USER SHOULD ONLY SEE THEIR ONLY DATA OR TASKS
    def get_context_data(self, **kwargs):
        context = super().get_context_data( **kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False)
        
        #search functionality
        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(title__startswith=search_input)
        context['search_input'] = search_input
        
        return context
        
    
class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'
    
class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = {'title', 'description', 'complete'}  #lists all fields
    success_url = reverse_lazy('tasks')   #redirect the user to task
    
    #valided the form for the loged in user to get his data when created
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)
    
class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = {'title', 'description', 'complete'}   
    success_url = reverse_lazy('tasks')
    
class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')
    