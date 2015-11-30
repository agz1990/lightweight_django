import os
from django.shortcuts import render
from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.template import Template
from django.utils._os import safe_join


# Create your views here.


def get_page_or_404(name):
    try:
        file_path = safe_join(settings.SITE_PAGE_DIRECTORY, name)
        print(file_path)
    except ValueError:
        raise Http404('Page Not Found')
    else:
        if not os.path.exists(file_path):
            raise Http404('Page Not Found')

    with open(file_path, 'r') as f:
        page = Template(f.read())

    return page


def page(request, slug='index'):
    print("page-[{}]".format(slug))
    file_name = '{}.html'.format(slug)
    page = get_page_or_404(file_name)
    context = {
        'slug': slug,
        'page': page
    }

    return render(request, 'page.html', context)
