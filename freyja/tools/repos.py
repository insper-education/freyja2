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
       command = 'clone {} {}/{} '.format(repo, dir, repo.split(sep='/')[-1])
       out = subprocess.check_output('git {}'.format(command), shell=True).decode('utf-8')
   except:
       status = False
   return status


def get_default_branch(repo):
    command = 'git -C {} remote show origin | sed -n \'/HEAD branch/s/.*: //p\''.format(repo)
    branch = subprocess.check_output(command, shell=True).decode('utf-8')
    return(branch)


@click.option(
    "--dir",
    default='repos',
    help="Directory to clone the repositories"
)
@repos.command()
@click.pass_obj
def clone(freyja, dir):
    if freyja.open_repos_file() is False:
        return -1

    if os.path.isdir(dir):
        if len(os.listdir(dir)) > 0:
            click.echo('Repos dir folder already exist, please use freyja repos update')
            click.confirm('Do you want to run the update?')
            update(dir, 'main')

    log = {}
    repoFail = []
    for repo in freyja.repos_url:
        log[repo] = clone_repo(repo, dir)

    report(log)


@click.option(
    "--dir",
    default='repos',
    help="Directory to clone the repositories"
)
@click.option(
    "--branch",
    default='auto',
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
    repos_new = [repo for repo in freyja.repos_name if repo not in repos_dir]

    if len(repos_new) > 0:
        click.echo("Repo list has been updated and there is a new repository in the list")
        click.echo("this script only checks for new repositories in the list")
        click.echo(repos_new)
        click.confirm('Do you want to clone this repositories?')
        for repo in repos_new:
            clone_repo(repo, dir)

    for repo in repos_dir:
        status = True
        out = ''
        repo_dir = os.path.join(dir, repo)
        try:
            if branch == 'auto':
                branch_c = get_default_branch(repo_dir)
            else:
                branch_c = branch
            command = '-C {} pull origin {}'.format(repo_dir, branch_c)
            out = subprocess.check_output('git {}'.format(command), shell=True).decode('utf-8')
        except:
            status = False

        if status is False:
            print("{}: {}".format(repo, out))

        log[repo] = status

    report(log)
