import click
import subprocess
import yaml
import os
import time


@click.group()
def issues():
    pass


class gh_issues():
    def __init__(self, repos, issues):
        self.repos = repos
        self.issues = issues
        self.log = {}

    def report(self):
        click.echo('-----========-----')
        click.echo('Issues run on {} repos:'.format(len(self.log)))
        for r, s in self.log.items():
            existed = len([item[1] for item in s if item[1] == 'Existed'])
            created = len([item[1] for item in s if item[1] == 'Created'])
            erro = len([item[1] for item in s if item[1] == 'Erro'])
            click.echo('\t {}: Create {} / Existed {} / Erro'.format(r, existed, created, erro))

    def list(self, repo):
        command = 'issue list -s all -R {}'.format(repo)
        out = subprocess.check_output('gh {}'.format(command), shell=True).decode('utf-8')
        return(out)

    def check_if_exist(self, issueList, issue):
        if issueList.find(issue['Title']) > 0:
            return True
        return False

    def creeate(self, issue, repo):
        title = f"{issue['Title']}"
        body = f"{issue['Body']}"
        process = subprocess.Popen(['gh', 'issue', 'create', '-t', title, '-b', body, '-R', repo],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return stderr

    def bulk_run(self):
        for repo in self.repos:
            log = []
            status = None
            issueList = self.list(repo)

            click.echo(repo)
            for k, v in self.issues.items():
                if self.check_if_exist(issueList, v) is False:
                    click.echo('\t criando issue   : {}'.format(v['Title']))
                    r = self.creeate(v, repo)
                    if r:
                        status = 'Erro'
                    else:
                        status = 'Created'
                    time.sleep(5)
                else:
                    status = 'Existed'
                    click.echo('\t issue já existia: {}'.format(v['Title']))
                log.append([v['Title'], status])
            self.log[repo] = log


@click.argument('issues_yml', type=click.File('rb'))
@issues.command()
@click.pass_obj
def create(freyja, issues_yml):
    if freyja.open_repos_file() is False:
        return

    issues = yaml.load(issues_yml, Loader=yaml.FullLoader)['issues']

    gh = gh_issues(freyja.repos_url, issues)
    gh.bulk_run()
    gh.report()
