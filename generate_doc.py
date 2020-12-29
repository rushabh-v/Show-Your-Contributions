from os.path import isfile
import sys
from github import Github

import json

g = Github(sys.argv[1])
user = g.get_user()
cur_contrib = 0

with open('templates.json', 'r') as j:
    templates = json.load(j)

start = templates["start"].format(
    user.login,
    user.name if user.name is not None else user.login,
    user.avatar_url,
    user.name if user.name is not None else user.login
)
middle = templates["middle"]
tail = templates["tail"]

with open('colors.json', 'r') as j:
    lang_colors = json.load(j)

if isfile('total_contribs'):
    with open('total_contribs', 'r') as f:
        try: prev_contrib = int(f.read())
        except: prev_contrib = -1
else: prev_contrib = -1


def add_row(contribs, key, is_pr):
    org, repo_name = key.split('/')
    merged_link = contribs[key]['merged_url']
    open_link = contribs[key]['open_url']
    closed_link = contribs[key]['closed_url']
    n_merged = contribs[key]['n_merged']
    n_open = contribs[key]['n_open']
    n_closed = contribs[key]['n_closed']
    lang = contribs[key]['lang']
    n_days = contribs[key]['last_mod']
    stars = contribs[key]['stars']
    last_mod = ''
    if n_days > 30: last_mod = str(n_days // 30) + " months ago"
    else: last_mod = str(n_days) + " days ago"

    if is_pr and (n_merged + n_open) == 0:
        return "", (n_merged + n_open + n_closed)

    lang_color = (lang_colors[lang] if lang in lang_colors
                     else 'rgb(0,255,0)')

    repo_html = templates["pr_head"].format(org, repo_name, org, repo_name)
    if n_merged: repo_html += templates["pr_merged"].format(merged_link, n_merged)
    if n_open:   repo_html += templates["pr_open"].format(open_link, n_open)
    if n_closed: repo_html += templates["pr_closed"].format(closed_link, n_closed)
    repo_html += templates["pr_tail"].format(lang_color, lang, stars, last_mod)

    return repo_html, (n_merged + n_open + n_closed)


if __name__ == '__main__':
    with open('my_contribs.json', 'r') as j:
        contribs = json.load(j)
    contribs = json.loads(contribs)
    prs = contribs['pulls']
    issues = contribs['issues']

    def get_count_pr(d):
        return prs[d]['n_open'] + prs[d]['n_merged']
    def get_count_issue(d):
        return issues[d]['n_open'] + issues[d]['n_closed']

    pr_keys = sorted(prs.keys(), key=get_count_pr, reverse=True)
    issues_keys = sorted(issues.keys(), key=get_count_issue, reverse=True)

    html = templates["head"] + start
    for key in pr_keys:
        code, count = add_row(prs, key, True)
        html += code
        cur_contrib += count

    html += middle
    for key in issues_keys:
        code, count = add_row(issues, key, False)
        html += code
        cur_contrib += count
    html += tail

    if prev_contrib == cur_contrib:
        exit()

    with open('total_contribs', 'w') as f:
        f.write(str(cur_contrib))
    with open('contributions.html', 'w') as f:
        f.write(html)
