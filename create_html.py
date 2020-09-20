import sys
from github import Github

import json

with open('total_contribs', 'r') as f:
    prev_contrib = int(f.read())

g = Github(sys.argv[1])
user = g.get_user()
cur_contrib = 0

start = """
<body>
    <div id="root" class="content">
        <div class="header">
            <div class="header-contents" style="display: block!important;">My Contributions</div>
        </div>
        <div class="results"><a target="_blank" class="h3 link-gray-dark no-underline author-name"
                href="https://github.com/{}">
                <div class="author"><img class="avatar mb-2" alt="{}"
                        src="{}"
                        height="190" width="190">
                    <div>{}</div>
                </div>
            </a>
            <div class="contributions pl-md-4 px-sm-2">
                <div class="flex-row mt-3">
                    <h3>Pull Requests</h3>""".format(user.login, user.name, user.avatar_url, user.name)

mid = """
                        </div>
                <div class="flex-row  mt-3">
                    <h3>Issues</h3>
"""

end = """
                </div>
            </div>
        </div>
    </div>
    <!-- <script src="./Show off your open source contributions and check out others_files/widgets.js" charset="utf-8"></script>
    <script src="./Show off your open source contributions and check out others_files/bundle.js"></script> -->
    <footer class="footer text-small text-gray">
        <div class="footer-content">
            <div>Template by <a target="_blank" class="no-underline" href="https://github.com/31z4">Elisey Zanko</a></div>
        </div>
    </footer>

</body></html>

"""

lang_colors = {
    'Python': 'rgb(53, 114, 165)',
    'Java': 'rgb(176, 114, 25)',
    'C++': 'rgb(243, 75, 125)',
    'Jupyter Notebook': 'rgb(218, 91, 11)',
    'JavaScript': 'rgb(255,255,0)',
    'C': 'rgb(169,169,169)',
}

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

    if is_pr and n_merged == 0:
        return "", (n_merged + n_open + n_closed)

    lang_color = (lang_colors[lang] if lang in lang_colors
                     else 'rgb(0,255,0)')

    repo_html = """
                        <div class="border-top py-1">
                            <div class="d-flex flex-justify-between text-gray">
                                <div><a target="_blank" class="link-gray no-underline"
                                        href="https://github.com/{}/{}"><span>{}</span>/<span
                                            class="text-bold">{}</span></a></div>
                                <div class="d-inline-flex flex-justify-end">""".format(org, repo_name, org, repo_name)

    if n_merged:
        repo_html += """
                                    <div><a target="_blank" class="link-gray no-underline"
                                            href={}
                                            style="cursor: pointer;"><span class="counter merged">{}</span>&nbsp;merged</a></div>""".format(merged_link, n_merged)

    if n_open:
        repo_html += """
                                    <div><a target="_blank" class="link-gray no-underline"
                                            href={}
                                            style="cursor: pointer;"><span class="counter open">{}</span>&nbsp;open</a></div>""".format(open_link, n_open)
    if n_closed:
        repo_html += """
                                    <div><a target="_blank" class="link-gray no-underline"
                                            href={}
                                            style="cursor: pointer;"><span class="counter closed">{}</span>&nbsp;closed</a></div>""".format(closed_link, n_closed)
        
    repo_html += """
                            </div>
                        </div>
                        <div class="d-flex flex-justify-between text-gray">
                            <div class="d-inline-flex">
                                <div class="f6 flex-items-center mr-3 mt-1"><span class="repository-language"
                                        style="background-color: {};"></span>&nbsp;{}</div>
                                <div class="repository-stars"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="16"
                                        viewBox="0 0 14 16">
                                        <path fill-rule="evenodd"
                                            d="M14 6l-4.9-.64L7 1 4.9 5.36 0 6l3.6 3.26L2.67 14 7 11.67 11.33 14l-.93-4.74L14 6z">
                                        </path>
                                    </svg>&nbsp;{}</div>
                            </div>
                            <div class="f6 mt-1">{}</div>
                        </div>
                    </div>""".format(lang_color, lang, stars, last_mod)
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

    f = open("starting.html", "r")
    html = f.read() + start

    for key in pr_keys:
        code, count = add_row(prs, key, True)
        html += code
        cur_contrib += count

    html += mid
    for key in issues_keys:
        code, count = add_row(issues, key, False)
        html += code
        cur_contrib += count

    html += end

    if prev_contrib == cur_contrib:
        exit(1)

    with open('total_contribs', 'w') as f:
        f.write(str(cur_contrib))
    with open('contributions.html', 'w') as f:
        f.write(html)
