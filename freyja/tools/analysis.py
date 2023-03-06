#!/usr/bin/env python3
#
import click
import subprocess
import os
import csv
from pydriller import Repository
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from math import ceil

color_green="#00ff00"
color_red="#ff0000"


@click.group()
def analysis():
    pass


@click.option(
    "--dir",
    default='repos',
    help="Directory to clone the repositories"
)
@click.argument('filename')
@analysis.command()
@click.pass_obj
def create_log(freyja, dir, filename):
    results = []
    for r in freyja.interact_repos(dir):
        for commit in Repository(r).traverse_commits():
            if commit.author.name != "github-classroom[bot]":
                data = {}
                files = []
                complexity = []
                add_complexity = 0
                for m in commit.modified_files:
                    files.append(m.filename)
                    complexity.append(m.complexity)
                    if m.complexity is not None:
                        add_complexity = m.complexity + add_complexity
                data['repo'] = os.path.split(r)[-1]
                data['author'] = commit.author.name
                data['date'] = commit.author_date
                data['files'] = files
                data['complexity'] = complexity
                data['add_complexity'] = add_complexity
                data['insertions'] = commit.insertions
                data['deletions'] = commit.deletions
                data['total_n_lines'] = commit.insertions + commit.deletions
                results.append(data)
        print(f"{r} parsed ok")

    heads = ['repo', 'author', 'date', 'files', 'complexity', 'add_complexity', 'insertions', 'deletions', 'total_n_lines']
    with open('filename', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames = heads)
        writer.writeheader()
        writer.writerows(results)


@analysis.command()
@click.argument('filename')
def graphic(filename):
    pass

    # import data
    df = pd.read_csv(filename, parse_dates=['date'])
    df.date = pd.to_datetime(df.date, utc=True)

    # get repos list name
    repos_names = df.drop_duplicates(subset=['repo'], keep='first')['repo'].values

    # slice and resample
    repos = []
    for r in repos_names:
        t = df[df.repo == r]
        df_resampled = (t.resample('D', on='date').agg({'total_n_lines':sum,
                                                        'insertions':sum,
                                                        'deletions':sum,
                                                        'add_complexity':sum}))
        df_resampled['repo'] = r
        repos.append(df_resampled)

    # create fig
    n_subplot_cols = 4
    fig_commits = make_subplots(rows=ceil(len(repos) / n_subplot_cols), cols=n_subplot_cols, shared_xaxes='all', subplot_titles=repos_names)

    for i in range(len(repos)):
        col = i %  n_subplot_cols + 1
        row = i // n_subplot_cols + 1
        repo = repos[i]
        fig_commits.add_trace(go.Scatter(x=repo.index,
                                y=repo["add_complexity"],
                                name=repo['repo'][0],
                                line_color='yellow', mode = "lines+markers"),
                    col=col, row=row)
        fig_commits.add_trace(go.Scatter(x=repo.index, y=repo["insertions"],
                                name=repo['repo'][0],
                                line_color='forestgreen', mode = "lines+markers"),
                    col=col, row=row)
        fig_commits.add_trace(go.Scatter(x=repo.index,
                                y=repo["deletions"],
                                name=repo['repo'][0],
                                line_color='indianred', mode = "lines+markers"),
                    col=col, row=row)

    fig_commits.update_layout(title='Repos insertions/deletions/complexity', showlegend=False)
    fig_commits.show()

    # create fig
    n_subplot_cols = 4
    fig_cumulative = make_subplots(rows=ceil(len(repos) / n_subplot_cols), cols=n_subplot_cols, shared_xaxes='all', subplot_titles=repos_names)

    for i in range(len(repos)):
        col = i %  n_subplot_cols + 1
        row = i // n_subplot_cols + 1
        repo = repos[i]
        fig_cumulative.add_trace(go.Scatter(x=repo.index,
                                y=repo["insertions"].cumsum(),
                                name=repo['repo'][0],
                                line_color='forestgreen',
                                            fill='tozeroy',
                                            mode='lines'),
                                col=col, row=row)
        fig_cumulative.add_trace(go.Scatter(x=repo.index,
                                y=repo["deletions"].cumsum(),
                                name=repo['repo'][0],
                                line_color='indianred',
                                fill='tozeroy'),
                                col=col, row=row)
        fig_cumulative.add_trace(go.Scatter(x=repo.index,
                                y=repo["add_complexity"].cumsum(),
                                name=repo['repo'][0],
                                line_color='yellow',
                                fill='tozeroy'),
                                col=col, row=row)

    fig_cumulative.update_layout(title='Repos acumulative insertions/deletions/complexity', showlegend=False)
    fig_cumulative.show()
