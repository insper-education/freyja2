import click
import subprocess
import yaml
import os

@click.group()
def repos():
    pass

def report(log):
    for r, s in log.items():
        print("{}: {}".format(r.split(sep='/')[-1], s))

def clone_repo(repo, dir):
   status = True
   try:
       url = 'git@github.com:' + repo
       command = 'clone {} {}/{} '.format(url, dir, repo.split(sep='/')[-1])
       out = subprocess.check_output('git {}'.format(command), shell=True).decode('utf-8')
   except:
       status = False
   return status

@click.option(
    "--dir",
    default='repos',
    help="Directory to clone the repositories"
)
@repos.command()
@click.pass_obj
def clone(freyja, dir):
    if freyja.open_repos_file() is False:
        return

    log = {}
    repoFail = []

    for repo in freyja.repos:
        log[repo] = clone_repo(repo, dir)
        report(log)

@click.option(
    "--dir",
    default='repos',
    help="Directory to clone the repositories"
)
@click.option(
    "--branch",
    default='main',
    help="branch to update: main/master/.."
)
@repos.command()
@click.pass_obj
def update(freyja, dir, branch):
    if freyja.open_repos_file() is False:
        return

    log = {}
    repoFail = []

    if os.path.isdir(dir) is False:
        click.echo('{} dir not found, use --dir or freyja repos clone'.format(dir))
        return False

    repos_dir = os.listdir(dir)
    repos_new = []
    for repo in freyja.repos:
        if repo.split('/')[-1] not in repos_dir:
            repos_new.append(repo)

    if len(repos_new) > 0:
        click.echo("Repo list has been updated and there is new repository in the list")
        click.echo("this script wont check for deleted repositories in the list (after clone)")
        click.echo(repos_new)
        click.confirm('Do you want to clone this repositories?')
        for repo in repos_new:
            clone_repo(repo, dir)

    for repo in os.listdir(dir):
        status = True

        if repo not in freyja.repos:
            click.echo("")

        try:
            command = '-C {} pull origin main'.format(os.path.join(dir,repo))
            print(command)
            out = subprocess.check_output('git {}'.format(command), shell=True).decode('utf-8')
        except:
            status = False

    log[repo] = status
    report(log)
