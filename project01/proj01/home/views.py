from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def main1(request):
    return render(request, 'index.html')
