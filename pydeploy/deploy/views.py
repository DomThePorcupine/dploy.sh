"""
This module contains all of our logic for creating
and deleting deployments as well as the routes for
starting stopping and building various containers.
"""
import json

# Hashing imports
import hashlib

# Django imports
from django.http import JsonResponse
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist

# Git imports
from pygit2 import clone_repository, GitError

# Helper imports
from deploy.helpers import *

import requests
from .models import Deployment
from django.views.decorators.csrf import csrf_exempt
from subprocess import call

SUPER_SECRET_KEY = 'uokqerudduheulkieuheuqeruh'

@csrf_exempt
def index(request):
    """
    This method will return all deployments when
    responding to a GET request, it will create
    a new deployment when responding to a POST
    request and will return a 404 not found on
    any other method. User authentication is required
    """
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'You are not logged in.'}, status=403)
    # Now check if this is a POST or GET request
    if request.method == 'GET':
        # We kow that they are logged in now
        # So send them all of the deployment models
        return JsonResponse(
            serializers.serialize("json", Deployment.objects.all()),
            safe=False)
    elif request.method == 'POST':
        #try:
        params = json.loads(request.body.decode('utf-8'))
        name = params['name']
        git = params['git']
        dirt = params['dir']
        run = params['run']
        cport = params['cport']
        lport = params['lport']
        create_new_key = params['gen_new_key']
        compose = params['compose']

        

        git_name = parse_git_url(git)
        
        # Make sure we have a valid git name
        if git_name == '':
            return JsonResponse({'message': 'invalid git url', 'reason': 'bad_git_url'}, status=400)
        
        # Replace copied ssh with proper ssh
        #if "git@github.com" in git:
        #    git = "ssh://" + git
        
        # append our repo name to our dir name
        if dirt.endswith('/'):
            dirt = dirt + git_name
        else:
            dirt = dirt + '/' + git_name

        # awesome, now lets create our custom url
        webhook = hashlib.md5((params['name'] + SUPER_SECRET_KEY).encode())

        # First see if we need to generate an ssh key
        # If we do we cannot pull automatically
        if create_new_key:
            generate_ssh_key(dirt)
        else:
            # Let's try to clone our repo
            try:
                clone_repository(git, dirt)
            except GitError:
                return JsonResponse({'message': 'invalid git url', 'reason': 'bad_git_url'}, status=400)
            except ValueError:
                return JsonResponse({'message': 'invalid directory, perhaps the destination folder exists?', 'reason': 'bad_dir'}, status=400)

        d = Deployment.objects.create(
            name_text=name,
            git_url_text=git,
            dir_text=dirt,
            is_running=run,
            webhook_text=webhook.hexdigest(),
            container_port=cport,
            local_port=lport,
            is_compose=compose)

        return JsonResponse({'message': 'success', 'id': d.id})

        '''except Exception as e:
            print(e)
            print(e.__class__.__name__)
            return JsonResponse({'message': 'Invalid params'}, status=400)'''

    else:
        return JsonResponse({'message': 'Unknown method'}, status=404)

####################################################################################
# Method for inspecting deployments
####################################################################################
def detail(request, deployment_id):
    """
    This method gives details about a given
    deployment. It only responds to GET
    requests for now
    """
    if request.method == "GET": 
        try:
            dep = Deployment.objects.get(pk=deployment_id)
            return JsonResponse(serializers.serialize("json", [dep]), safe=False)
        except ObjectDoesNotExist as e:
            return JsonResponse({'message': 'Error retriving deployment.'})
    else:
        return JsonResponse({'message':'not found'}, status=404)

####################################################################################
# Method for handling webhooks
####################################################################################
@csrf_exempt
def webhooks(request, deployment_hash):
    """
    Given a deployment hash, find the deployment
    and then use the helper functions to stop
    the container if it is running,
    rebuild it (with potential changes)
    and if it was running start it again
    """
    if request.method != "POST":
        return JsonResponse({'message': 'not found.'}, status=404)
    # Now we pull out the slug and try to preform a new build
    try:
        dep = Deployment.objects.get(webhook_text=deployment_hash)
        # First try to preform a git pull, since the deployment
        # has to exist we know that it was at least cloned
        pull_repo(dep.dir_text, dep.git_branch_text)
        # First check to see if the container is running
        if dep.is_running:
            # It is so stop the container
            stop_container(dep.container_id_text)
        # Now we should build and tag our new image
        build_container(dep.dir_text, dep.name_text)
        # Finally if it should be running we
        # should bring the container back up
        if dep.is_running:
            dep.container_id_text = start_container(dep)
            dep.save()

        return JsonResponse({'message': 'success'})
    except ObjectDoesNotExist as e:
        return JsonResponse({'message': 'not found'}, status=404)

####################################################################################
# Method for STARTING containers
####################################################################################
def start(requset, deployment_id):
    """
    This method will use the helper function
    to start a deployment's container
    """

    # Reject if the request is not get
    if requset.method != 'GET':
        return JsonResponse({'message': 'not found.'}, status=404)
    try:
        dep = Deployment.objects.get(pk=deployment_id)
        # check that this is not already started
        if dep.is_running:
            return JsonResponse({'message': 'already running'}, status=202)
        # Try to start the container
        if dep.is_compose:
            call(['docker-compose',
                    'up', '-d'],
                    shell=True, cwd=dep.dir_text)
        else:
            try:
                # update the container id so that it is easier to
                # stop it
                dep.container_id_text = start_container(dep)
            except requests.exceptions.ConnectionError:
                return JsonResponse({'message': 'Error starting container. Couldn\'t connect to the docker daemon. Is docker running?'}, status=500)
            except Exception as e:
                print(e)
                print(e.__class__.__name__)
                return JsonResponse({'message': 'Error starting container'}, status=500)
        # Okay now update the running var
        dep.is_running = True
        dep.save()
        return JsonResponse({'message': 'success'})
    except ObjectDoesNotExist as e:
        return JsonResponse({'message': 'not found'}, status=404)

####################################################################################
# Method for STOPING containers
####################################################################################
def stop(request, deployment_id):
    """
    Given a container id this method
    will stop the container if it is 
    running
    """
    if request.method != 'GET':
        return JsonResponse({'message': 'not found'}, status=404)

    try:
        dep = Deployment.objects.get(pk=deployment_id)
        # check that this is not already started
        # perhaps we should do this by querying the
        # status of the container itself? - maybe not
        # because its better if we are not constantly
        # querying for results
        if not dep.is_running:
            return JsonResponse({'message': 'not running'}, status=202)
        # Okay so we are __probably running, check if this is
        # a compose project or not
        if dep.is_compose:
            call(['docker-compose',
                    'down'],
                    shell=True, cwd=dep.dir_text)

        else:
            try:
                stop_container(dep.container_id_text)
            except Exception as e:
                print(e)
                print(e.__class__.__name__)
                return JsonResponse(
                    {
                        'message': 'error stopping container'
                    }, status=500)
        # Okay now update the running var
        # and set our container id back to
        # nothing
        dep.is_running = False
        dep.container_id_text = ''
        dep.save()
        return JsonResponse({'message': 'success'})

    except ObjectDoesNotExist as e:
        return JsonResponse({'message': 'not found'}, status=404)

####################################################################################
# Method for BUILDING containers
####################################################################################
def build(request, deployment_id):
    """
    This method is very simple, given a
    deployment id it will attempt to
    build the container in that folder.

    It does not handle high level errors
    like bad Dockerfiles and the like
    """
    if request.method != 'GET':
        return JsonResponse({'message': 'not found'}, status=404)
    try:
        # Pull out our dep
        dep = Deployment.objects.get(pk=deployment_id)
        # Check to make sure our repo has been cloned
        if not os.path.exists(dep.dir_text):
            # We need to clone first, ususally happens
            # when you have to generate a private key
            # first
            keypath = ''
            if dep.dir_text.endswith('/'):
                keypath = dep.dir_text[:-1] + "_keys/"
            else:
                keypath = dep.dir_text + "_keys/"

            key_pub = os.path.expanduser(keypath + 'id_rsa.pub')
            key_priv = os.path.expanduser(keypath + 'id_rsa')

            keypair = pygit2.Keypair("git", key_pub, key_priv, None)
            callbacks = pygit2.RemoteCallbacks(credentials=keypair)
            clone_repository(dep.git_url_text, dep.dir_text, callbacks=callbacks)

        # Use our helper function to build our container
        build_container(dep.dir_text, dep.name_text)
        return JsonResponse({'message': 'success'})
    except Exception as e:
        # NOTE During the development of this app I want as much
        # logging as possible so that I can try to create 
        # descriptive responses for all sorts of errors.
        # so for now we are going to handle everything as a
        # generic exception and print the error and its type
        print(e)
        print(e.__class__.__name__)
        return JsonResponse({'mesage': 'error building container'})

####################################################################################
# Method for deleting deployments
####################################################################################
def delete(request, deployment_id):
    """
    This method is very simple, given a
    deployment id it will delete that object
    we should potentially remove the directory
    that we cloned as well
    """
    if request.method != 'DELETE':
        return JsonResponse({'message': 'not found'}, status=404)
    # Okay they actually want to delete things
    try:
        dep = Deployment.objects.get(pk=deployment_id)
        dep.delete()
        return JsonResponse({'message': 'success'})
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'not found'}, status=404)

####################################################################################
# Method for deleting deployments
####################################################################################
def get_rsa_pub(request, deployment_id):
    if request.method != 'GET':
        return JsonResponse({'message': 'not found'}, status=404)
    # Get the deployment so we can get the path url
    try:
        dep = Deployment.objects.get(pk=deployment_id)
        # Check if the folder exists, if not we know
        # this deployment has no key
        direct = ""
        if dep.dir_text.endswith('/'):
            direct = dep.dir_text[:-1] + "_keys/"
        else:
            direct = dep.dir_text + "_keys/"

        if not os.path.exists(direct):
            return JsonResponse({'ssh_key': 'No key found for this deployment.'})
        key = read_ssh_key(dep.dir_text)
        return JsonResponse({'ssh_key': key})
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'not found'}, status=404)