import click
import os
import yaml
from .tools.list import list
from .tools.repos import repos
from .tools.issues import issues

class Freyja:
    def __init__(self, repos_yml):
        self.repos_yml = repos_yml
        self.repos_url = []
        self.repos_name = []
        self.org = ''
        self.https = False
        self.prefix = ''
        self.verbose = False


    def open_repos_file(self, log=True):
        if os.path.isfile(self.repos_yml) is False:
            if log:
                click.echo('Please informe a valid repo list (--repos-yml) or generate a new one with the freyja list create FILTER')
            return False

        with open(self.repos_yml, 'r') as file:

            config = yaml.load(file, Loader=yaml.FullLoader)

            if 'org' not in config:
                click.echo('To use the full power of this script generate a repo config file with a org key.')
                return False
            else:
                self.org = config['org']

            if 'prefix' not in config:
                click.echo('Please generate a repo config file with a prefix key.')
                return False
            else:
                self.prefix = config['prefix']

            if 'repos' not in config:
                click.echo('Please generate a repo config file with a repos key.')
                return False
            else:
                self.repos = config['repos']

            if config['repos'] is None:
                self.repos_url = []
                self.repos_name = self.get_repos_name()
                return False
        return True


    def get_repos_name(self):
        return[repo.split('/')[-1] for repo in self.repos_url]


    def write_config(self):
        config = {'org': self.org, 'prefix': self.prefix, 'repos': self.repos}
        with open(self.repos_yml, 'w+') as f:
            y = yaml.dump(config, default_flow_style=False, indent=None)
            f.write(y)
        click.echo('{} config file created/updated with a total of {} repos'.format(self.repos_yml, len(self.repos)))


    def __repr__(self):
        return f"<Freyja {self.home}>"

pass_config = click.make_pass_decorator(Freyja)

@click.group()
@click.option(
    '-r', "--repos_yml",
    default="repos.yml",
    help="Set the repository list file.",
)
@click.option("--verbose", "-v", is_flag=True, help="Enables verbose mode.")
@click.pass_context
def cli(ctx, repos_yml, verbose):
    ctx.obj = Freyja(repos_yml)
 #   ctx.obj.verbose = verbose

cli.add_command(list)
cli.add_command(repos)
cli.add_command(issues)
