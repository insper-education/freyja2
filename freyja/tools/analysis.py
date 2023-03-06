#!/usr/bin/env python3
#
import click
import subprocess
import os
import csv
from pydriller import Repository

@click.group()
def analysis():
    pass


@click.option(
    "--dir",
    default='repos',
    help="Directory to clone the repositories"
)
@click.argument('filename',
                help='csv output file name')
@analysis.command()
@click.pass_obj
def contributions(freyja, dir, filename):

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
