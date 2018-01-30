from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from rango.forms import PageForm

# Index page
def index(request):
    # Query the database for a list of ALL categories currently stored
    # Order the categories by no. likes in descenfing order
    # Retrieve the top 5 only - pr all if less than 5
    # Place the list in context_dict dictionary
    # that will be passed to the template engine
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    # Construct a dictionary to pass to the template engine as its context
    # The key boldmessage is the same as {{ boldmessage }} in the template
    context_dict= {'categories': category_list, "pages": page_list}

    # Return a rendered response to send to the client
    # The first param is the template we wish to use
    return render(request, 'rango/index.html', context_dict)

# About page
def about(request):
    context_dict = {}
    # Print out the type of the method (GET or POST)
    print(request.method)
    # Print out the username (or AnonymousUser if no one is logged in)
    print(request.user)
    return render(request, 'rango/about.html', context=context_dict)

# Find categories and pages
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

# Add category view
def add_category(request):
    form = CategoryForm()

    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

    # Have been provided with a valid form?
    if form.is_valid():
        # Save the new category to the database
        form.save(commit=True)
        # Give a confirmation message that the category is saved
        # Since the most recent category added is on the index page
        # Then we can direct the user back to the index page.
        return index(request)
    else:
        # The supplied form contains errors - print them to the terminal
        print(form.errors)

    # Will handl th bad form, new form or no form supplied cases.
    # Render the form with error messages (if any).
    return render(request,'rango/add_category.html', {'form': form})

# Add page view
def add_page(request,category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        catgory = None
    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form_save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)
