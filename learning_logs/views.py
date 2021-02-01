from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404

from .models import Topic, Entry
from .forms import TopicForm, EntryForm


# The home page for Learning Log
def index(request):
	return render(request, 'learning_logs/index.html')

# SHow all topics
@login_required
def topics(request):
	topics = Topic.objects.filter(owner=request.user).order_by('date_added')
	context = {'topics': topics}
	return render(request, 'learning_logs/topics.html', context)

# Show a single topic and all its entries
@login_required
def topic(request, topic_id):
	topic = get_object_or_404(Topic, id=topic_id)
	# Make sure the topic belongs to the current user
	if topic.owner != request.user:
		raise Http404

	entries = topic.entry_set.order_by('-date_added')
	context = {'topic': topic, 'entries': entries}
	return render(request, 'learning_logs/topic.html', context)

# Add a new Topic
@login_required
def new_topic(request):
	if request.method != 'POST':
		# No data submittedl create a blank form
		form = TopicForm()
	else:
		# POST data submitted; process data
		form = TopicForm(data=request.POST)
		if form.is_valid():
			new_topic = form.save(commit=False)
			new_topic.owner = request.user
			new_topic.save()
			return redirect('learning_logs:topics')

	# Display a blank or invalid form
	context = {'form': form}
	return render(request, 'learning_logs/new_topic.html', context)

# Add a new entry for a particular topic
@login_required
def new_entry(request, topic_id):
	topic = Topic.objects.get(id=topic_id)
	if topic.owner != request.user:
		raise Http404

	# No data submitted; create a blank form
	if request.method != 'POST':
		form = EntryForm()
	else:
		# POST data submitted; process data
		form = EntryForm(data=request.POST)
		if form.is_valid():
			new_entry = form.save(commit=False)
			new_entry.topic = topic
			new_entry.save()
			return redirect('learning_logs:topic', topic_id=topic_id)

	# Display a black or invalid form
	context = {'topic': topic, 'form': form}
	return render(request, 'learning_logs/new_entry.html', context)


# Edit an existing entry
@login_required
def edit_entry(request, entry_id):
	entry = Entry.objects.get(id=entry_id)
	topic = entry.topic
	if topic.owner != request.user:
		raise Http404

	if request.method != 'POST':
		# Initial request; pre-fill form with the current entry
		form = EntryForm(instance=entry)
	else:
		# POST data submitted, process data
		form = EntryForm(instance=entry, data=request.POST)
		if form.is_valid():
			form.save()
			return redirect('learning_logs:topic', topic_id=topic.id)

	context = {'entry': entry, 'topic': topic, 'form': form}
	return render(request, 'learning_logs/edit_entry.html', context)
