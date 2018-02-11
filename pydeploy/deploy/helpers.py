"""
This module contains many useful
modular functions to try to keep
our routes/views cleaner
"""

# import or Docker sdk
from docker import APIClient
import docker

# import our git sdk
from pygit2 import discover_repository, Repository
import pygit2

# import Crypto for unique ssh key generation
from Crypto.PublicKey import RSA
import os

def parse_git_url(the_url):
    """"
    This method takes a string of an entire
    git repo url and returns the name of
    the folder that it will be cloned into
    """
    path = the_url.split('/')
    # Check to make sure it ends in '.git'
    if '.git' in path[-1]:
        return path[-1].replace('.git', '')
    return ''

#############################################################
#############################################################
def build_container(dir_path, ttag):
    """
    This method takes a directory path and a tag
    using those it builds and tags the container
    in the directory
    """
    print("here")
    cli = APIClient(base_url='unix://var/run/docker.sock')
    response = [line for line in cli.build(path=dir_path, rm=True, tag=ttag)]
    print(response)

#############################################################
#############################################################
def stop_container(cont_id):
    """
    Given a container id this method
    simply tries to stop it, first
    checking if it is running
    """
    client = docker.from_env()
    cont = client.containers.get(cont_id)
    print(cont.status)
    cont.stop()
    return

#############################################################
#############################################################
def start_container(dep):
    """
    Given a deployment object this starts
    a container with the deployment's
    settings
    """
    client = docker.from_env()
    nid = client.containers.run(
        dep.name_text,
        detach=True,
        ports={
            dep.container_port + '/tcp': int(dep.local_port)
        })
    return nid.short_id

#############################################################
#############################################################
def pull_repo(repo_path, repo_branch):
    """
    Given a path to one of our managed repos
    this method will basically preform a pull,
    because the files should not be changing
    we do not need to reset or anything
    """
    repository_path = discover_repository(repo_path)
    repo = Repository(repository_path)
    # Go through our remotes
    for remote in repo.remotes:
        # Look for origin, we will add functionality
        # to change remotes soon
        if remote.name == 'origin':
            remote.fetch()
            remote_master_id = repo.lookup_reference('refs/remotes/origin/%s' % (repo_branch)).target
            merge_result, _ = repo.merge_analysis(remote_master_id)

            # No new changes
            if merge_result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
                return
            elif merge_result & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
                repo.checkout_tree(repo.get(remote_master_id))
                try:
                    master_ref = repo.lookup_reference('refs/heads/%s' % (repo_branch))
                    master_ref.set_target(remote_master_id)
                except KeyError:
                    repo.create_branch(repo_branch, repo.get(remote_master_id))
                repo.head.set_target(remote_master_id)
            elif merge_result & pygit2.GIT_MERGE_ANALYSIS_NORMAL:
                repo.merge(remote_master_id)

                if repo.index.conflicts is not None:
                    for conflict in repo.index.conflicts:
                        print('Conflicts found in:', conflict[0].path)
                    raise AssertionError('Conflicts, ahhhhh!!')

                user = repo.default_signature
                tree = repo.index.write_tree()
                commit = repo.create_commit('HEAD',
                                            user,
                                            user,
                                            'Merge!',
                                            tree,
                                            [repo.head.target, remote_master_id])
                # We need to do this or git CLI will think we are still merging.
                repo.state_cleanup()
#############################################################
#############################################################
def generate_ssh_key(repo_path):
    '''ssh-keygen -f $HOME/.ssh/id_rsa -t rsa -N '' -C "foo@bar.com"'''
    key = RSA.generate(4096)
    # Make our directory for keys
    direct = ""
    if repo_path.endswith('/'):
        direct = repo_path[:-1] + "_keys/"
    else:
        direct = repo_path + "_keys/"

    if not os.path.exists(direct):
        os.makedirs(direct)
    
    f = open(direct + "id_rsa", "wb")
    f.write(key.exportKey('PEM'))
    f.close()

    pubkey = key.publickey()
    f = open(direct + "id_rsa.pub", "wb")
    f.write(pubkey.exportKey('OpenSSH'))
    f.close()

#############################################################
#############################################################
def read_ssh_key(repo_path):
    data = ''
    direct = ''
    if repo_path.endswith('/'):
        direct = repo_path[:-1] + "_keys/"
    else:
        direct = repo_path + "_keys/"
    with open (direct + "id_rsa.pub", "r") as rsa_pub_file:
        data = rsa_pub_file.read()
    return data.rstrip()