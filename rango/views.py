from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from rango.forms import PageForm
from rango.forms import UserForm, UserProfileForm

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

def register(request):
    # A boolean value for telling the template
    # whether the registration was successful.
    # Set to False initially. Code changes value to
    # True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves,
            # we set commit=False. This delays saving the model
            # until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and
            #put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to indicate that the template
            # registration was successful.
            registered = True
        else:
            # Invalid form or forms - mistakes or something else?
            # Print problems to the terminal.
            print(user_form.errors, profile_form.errors)
    else:
        # Not a HTTP POST, so we render our form using two ModelForm instances.
        # These forms will be blank, ready for user input.
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render(request,
                'rango/register.html',
                {'user_form': user_form,
                'profile_form': profile_form,
                'registered': registered})
