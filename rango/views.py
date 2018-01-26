from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page

def index(request):
    # Query the database for a list of ALL categories currently stored
    # Order the categories by no. likes in descenfing order
    # Retrieve the top 5 only - pr all if less than 5
    # Place the list in context_dict dictionary
    # that will be passed to the template engine
    category_list = Category.objects.order_by('-likes')[:5]

    # Construct a dictionary to pass to the template engine as its context
    # The key boldmessage is the same as {{ boldmessage }} in the template
    context_dict= {'categories': category_list}

    # Return a rendered response to send to the client
    # The first param is the template we wish to use
    return render(request, 'rango/index.html', context_dict)

def about(request):
    context_dict = {}
    return render(request, 'rango/about.html', context=context_dict)

def show_category(request, category_name_slug):
    # Create a context dictionary
    context_dict={}

    try:
        # Try to find a category name slug with the given name
        # else the .get() method raises a DoesNotExsist exception
        category = Category.objects.get(slug=category_name_slug)

        # Retrieve all of the associated pages
        # filter() will return a list of page objects or an empty list
        pages = Page.objects.filter(category=category)

        # Adds results lists to the template context under name pages
        context_dict['pages'] = pages
        # We also add the category object from the
        # database to the context dictionary.
        # We'll use this in the template to verify the category exists
        context_dict['category'] = category

    except Category.DoesNotExist:
        # If we couldn't find the specified category
        # Don't do anything - the template will
        # display the "no category" message for us.
        context_dict['category'] = None
        context_dict['pages'] = None

    # Render the response and return it to the client
    return render(request, 'rango/category.html', context_dict)
