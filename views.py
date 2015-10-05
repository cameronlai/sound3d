from django.shortcuts import render
from django.template import Context, Template

from models import UploadFileForm
from models import sound3dGenerator
import re

message = {
    'none': '', 
    'failUpload': 'Fail in upload, please check input sound file!!',
    'failGenerate': 'Fail in generation, please check input sound file!!',
}

# Create your views here.
def index(request):
    status = 'none'
    indexContext = {'status': message['none']}

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            mSound3dGenerator = sound3dGenerator()
            response = mSound3dGenerator.gen_online(request.FILES['musicFile'])
            if response:
                indexContext['status'] = message['none']
                return response
            else:
                indexContext['status'] = message['failGenerate']
        else:
            indexContext['status'] = message['failUpload']

    form = UploadFileForm()
    indexContext['form'] = form
    return render(request, 'sound3d/index.html', indexContext)
