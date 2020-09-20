import sys

from github import Github
from datetime import datetime
import json

repo = {
        'stars': 0,
        'lang': None,
        'n_merged': 0,
        'n_closed': 0,
        'n_open': 0,
        'last_mod': float('inf'),
        'merged_url': None,
        'open_url': None,
        'closed_url': None,
        }


def creat_json(g, prs):
    my_contribs = {}
    issues = None
    name = 'issue'
    if prs: issues = g.search_issues(query="author:rushabh-v is:pr")
    else:   issues = g.search_issues(query="author:rushabh-v is:issue")
    n_issues = issues.totalCount
    repo_name = None
    for abc in issues:
        if prs:
            abc = abc.as_pull_request()
            name = 'pr'
            repo_name = abc.url[abc.url.index('repos')+6 : abc.url.index('pulls')-1]
        else: repo_name = abc.url[abc.url.index('repos')+6 : abc.url.index('issues')-1]
        if repo_name not in my_contribs:
            my_contribs[repo_name] = repo.copy()
            r = g.get_repo(repo_name)
            my_contribs[repo_name]['stars'] = r.stargazers_count
            my_contribs[repo_name]['lang'] = list(r.get_languages().keys())[0]
            org, repo_ = repo_name.split('/')
            if prs: my_contribs[repo_name]['merged_url'] = (
                        'https://github.com/search?q=is%3Apr+repo%3A'+org+'%2F'+repo_+'+author%3Arushabh-v+is%3Amerged')
            my_contribs[repo_name]['closed_url'] = (
            'https://github.com/search?q=is%3A'+name+'+repo%3A'+org+'%2F'+repo_+'+author%3Arushabh-v+is%3Aclosed')
            my_contribs[repo_name]['open_url'] = (
            'https://github.com/search?q=is%3A'+name+'+repo%3A'+org+'%2F'+repo_+'+author%3Arushabh-v+is%3Aopen')
        if prs and abc.merged: my_contribs[repo_name]['n_merged'] += 1
        elif abc.state == 'closed': my_contribs[repo_name]['n_closed'] += 1
        else: my_contribs[repo_name]['n_open'] += 1
        my_contribs[repo_name]['last_mod'] = min(my_contribs[repo_name]['last_mod'], (datetime.today() - abc.updated_at).days)
    return my_contribs, n_issues

if __name__ == '__main__':
    g = Github(sys.argv[1])
    pulls, n_pulls = creat_json(g, True)
    issues, n_issues = creat_json(g, prs=False)
    my_contribs = json.dumps({'pulls':pulls, 'issues':issues}, indent=4)
    with open('my_contribs.json', 'w') as json_file:
        json.dump(my_contribs, json_file)
