from django.shortcuts import render

def index(request):
    return render(request,'portalfilmes/index.html')

def dashboard(request):
    return render(request,'portalfilmes/dashboard.html')