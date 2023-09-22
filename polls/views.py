from django.http import HttpResponseRedirect, request
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm

from .models import Question, Choice, Vote


class IndexView(generic.ListView):
    """
    Displays the index page listing all questions.
    """
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(LoginRequiredMixin, generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        question = get_object_or_404(Question, pk=self.kwargs['pk'])
        if not question.can_vote():
            messages.error(request, 'Voting is not allowed.')
            return redirect('polls:index')
        return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
    """
    View for results page.
    """
    model = Question
    template_name = 'polls/results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            try:
                user_vote = Vote.objects.get(user=self.request.user, choice__question=self.get_object())
                context['user_vote'] = user_vote
            except Vote.DoesNotExist:
                context['user_vote'] = None
        else:
            context['user_vote'] = None
        return context

@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if not request.user.is_authenticated:
        # user must login
        return redirect("login")
    if not question.can_vote():
        messages.error(request, "Not available to vote")
        return redirect("polls:index")
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    this_user = request.user
    try:
        # find a vote for this user and this question.
        vote = Vote.objects.get(user=this_user, choice__question=question)
        # update his vote
        vote.choice = selected_choice
    except Vote.DoesNotExist:
        # no matching vote - create new Vote
        vote = Vote(user=this_user, choice=selected_choice)

    vote.save()
    messages.success(request, "Your vote has been recorded")
    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
def signup(request):
    """Register a new user."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # get named fields from the form data
            username = form.cleaned_data.get('username')
            # password input field is named 'password1'
            raw_passwd = form.cleaned_data.get('password1')
            user = authenticate(username=username,password=raw_passwd)
            login(request, user)
            return redirect('polls:index')
        # what if form is not valid?
        # we should display a message in signup.html
    else:
        # create a user form and display it the signup page
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})