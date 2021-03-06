import click
import subprocess
import yaml


def get(orgName, listLimit):
    command = 'gh repo list {} --limit {}'.format(orgName, listLimit)
    raw = subprocess.check_output(command, shell=True).decode('utf-8')
    return(raw.splitlines())


def search(rawList, prefix):
    l = []
    for url in rawList:
        if url.find(prefix) > 0:
            l.append(url.split()[0])
    return(l)


def get_repos(org_name, prefix, size=500):
    rawList = get(org_name, size)
    return(search(rawList, prefix))


def append_url(repos, https):
    if https is False:
        base_url = 'git@github.com:'
    else:
        base_url = 'https://'
    return([base_url + repo for repo in repos])


@click.group()
def list():
    pass


@click.argument('prefix')
@click.option(
    "--org_name",
    default="insper-classroom",
    help="Gh organization name to search"
)
@click.option(
    "--https",
    default=False,
    help="Create the list with https:// instead ssh://"
)
@list.command()
@click.pass_obj
def create(freyja, org_name, prefix, https):
    if freyja.open_repos_file(log=False) is True:
        click.echo('Repos list already exist do you want to update it? run: freyja list update')
        return 0

    freyja.org = org_name
    freyja.prefix = prefix
    freyja.repos_name = get_repos(org_name, prefix)
    freyja.repos_url = append_url(freyja.repos_name, https)
    freyja.write_config()


@list.command()
@click.pass_obj
def update(freyja):
    if freyja.open_repos_file() is False:
        return false

    c_repos_name = get_repos(freyja.org, freyja.prefix)
    c_repos_url = append_url(c_repos_name, False)
    cnt = 0
    for r in c_repos_name:
        if r not in freyja.repos_url:
            cnt = cnt + 1
            freyja.repos_url.append(r)
    click.echo("{} updated with {} repos".format(freyja.repos_yml, cnt))
    freyja.write_config()


@list.command()
@click.pass_obj
def print(freyja):
    if freyja.open_repos_file():
        for e in freyja.repos:
            click.echo(e)
