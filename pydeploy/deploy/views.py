import json
import time
from django.http import HttpResponse, JsonResponse
# Need for reading json POST request
from docker import APIClient
import docker
from .models import Deployment

from django.core import serializers
from pygit2 import clone_repository


# Need to import exceptions for better
# error handling
from django.core.exceptions import ObjectDoesNotExist



import hashlib

SUPER_SECRET_KEY = 'uokqerudduheulkieuheuqeruh'

def index(request):
  if not request.user.is_authenticated:
    return JsonResponse({'message': 'You are not logged in.'}, status=403)
  # Now check if this is a POST or GET request
  if request.method == 'GET':
    # We kow that they are logged in now
    # So send them all of the deployment models
    return JsonResponse(serializers.serialize("json", Deployment.objects.all()), safe=False)
  elif request.method == 'POST':
    try:
      params = json.loads(request.body)
      name = params['name']
      git = params['git']
      dirt = params['dir']
      run = params['run']
      cport = params['cport']
      lport = params['lport']
      # Make sure they have given us a semi
      # valid git URL
      splits = git.split('/')
      okay = False
      git_name = None
      for thing in splits:
        if ".git" in thing:
          okay = True
          git_name = thing.replace('.git','')
      if not okay:
        return JsonResponse({'message': 'invalid git url'})
      # append our repo name to our dir name
      if dirt.endswith('/'):
        dirt = dirt + git_name
      else:
        dirt = dirt + '/' + git_name

      # Let's try to clone our repo
      clone_repository(git, dirt)
      # awesome, now lets create our custom url
      webhook = hashlib.md5((params['name'] + SUPER_SECRET_KEY).encode())

      

      d = Deployment.objects.create(name_text=name,git_url_text=git,dir_text=dirt,is_running=run,webhook_text=webhook.hexdigest(),container_port=cport,local_port=lport)
      
      return JsonResponse({'message':'success', 'id': d.id})

    except Exception as e:
      print(e)
      return JsonResponse({'message': 'Invalid params'}, status=400)

  else:
    return JsonResponse({'message': 'Unknown method'}, status=404)

def detail(request, deployment_id):
  try:
    dep = Deployment.objects.get(pk=deployment_id)
    return JsonResponse(serializers.serialize("json", [dep]), safe=False)
  except ObjectDoesNotExist as e:
    return JsonResponse({'message': 'Error retriving deployment.'})

def webhooks(request, deployment_hash):
  if request.method != "POST":
    return JsonResponse({'message': 'not found.'}, status=404)
  # Now we pull out the slug and try to preform a new build
  try:
    dep = Deployment.objects.get(webhook_text=deployment_hash)
    # Do all the docker stuff and then respond
    c = APIClient(base_url='unix://var/run/docker.sock')
    
    c.build(path='/Users/dom/tmp',rm=True,tag='myexample')
    client = docker.from_env()
    client.containers.run('myexample', detach=True, ports={'8080/tcp': 3333})
    # Now that this is done we assume it has been tagged succesfully
    # and we bring it up

    return JsonResponse({'message':'success'})
  except ObjectDoesNotExist as e:
    return JsonResponse({'message':'not found'}, status=404)

####################################################################################
# Method for starting containers
####################################################################################
def start(requset, deployment_id):
  # Reject if the request is not get
  if requset.method != 'GET':
    return JsonResponse({'message': 'not found.'}, status=404)
  try:
    dep = Deployment.objects.get(pk=deployment_id)
    # check that this is not already started
    if dep.is_running:
      return JsonResponse({'message': 'already running'}, status=202)
    # Try to start the container
    try:
      client = docker.from_env()
      nid = client.containers.run(dep.name_text, detach=True, ports={dep.container_port + '/tcp': int(dep.local_port)})
      # update the container id so that it is easier to
      # stop it
      dep.container_id_text = nid.short_id
    except Exception as e:
      print(e)
      return JsonResponse({'message': 'Error starting container'}, status=500)
    # Okay now update the running var
    dep.is_running = True
    dep.save()
    return JsonResponse({'message': 'success'})
  except ObjectDoesNotExist as e:
    return JsonResponse({'message': 'not found'}, status=404)

def stop(request, deployment_id):
  if request.method != 'GET':
    return JsonResponse({'message':'not found'}, status=404)

  try:
    dep = Deployment.objects.get(pk=deployment_id)
    # check that this is not already started
    if not dep.is_running:
      return JsonResponse({'message': 'not running'}, status=202)
    try:
      client = docker.from_env()
      cont = client.containers.get(dep.container_id_text)
      cont.stop()
    except Exception as e:
      print(e)
      return JsonResponse({'message': 'error stopping container'}, status=500)
    # Okay now update the running var
    # and set our container id back to
    # nothing
    dep.is_running = False
    dep.container_id_text = ''
    dep.save()
    return JsonResponse({'message': 'success'})

  except ObjectDoesNotExist as e:
    return JsonResponse({'message': 'not found'}, status=404)

def build(request, deployment_id):
  if request.method != 'GET':
    return JsonResponse({'message': 'not found'}, status=404)
  try:
    # Pull out our dep
    dep = Deployment.objects.get(pk=deployment_id)

    c = APIClient(base_url='unix://var/run/docker.sock')
    response = [line for line in c.build(path=dep.dir_text,rm=True,tag=dep.name_text)]
    print(response)
    print(dep.name_text)
    print(dep.dir_text)
    return JsonResponse({'message': 'success'})
  except Exception as e:
    return JsonResponse({'mesage': 'error building container'})

def delete(request, deployment_id):
  if request.method != 'DELETE':
    return JsonResponse({'message': 'not found'}, status=404)
  # Okay they actually want to delete things
  try:
    dep = Deployment.objects.get(pk=deployment_id)
    dep.delete()
    return JsonResponse({'message': 'success'})
  except ObjectDoesNotExist as e:
    return JsonResponse({'message': 'not found'})