from django.shortcuts import render
from django.template import Context, Template

from models import UploadFileForm
from models import sound3dGenerator
import re

message = {
    'none': '', 
    'fail': 'Fail in generation, please check input sound file!!',
}

# Create your views here.
def index(request):
    status = 'none'
    indexContext = {'status': message['none']}

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        print form.is_valid()
        if form.is_valid():
            mSound3dGenerator = sound3dGenerator()
            ret = sound3dGenerator.generate(request.FILES['musicFile'])
            if ret:
                indexContext['status'] = message['none']
            else:
                indexContext['status'] = message['fail']
        else:
            indexContext['status'] = message['fail']
    else:
        form = UploadFileForm()

    indexContext['form'] = form
    return render(request, 'sound3d/index.html', indexContext)
