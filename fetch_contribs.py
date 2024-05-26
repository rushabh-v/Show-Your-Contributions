import sys
from os import system

from github import Github
from datetime import datetime
import json

repo = {
    "stars": 0,
    "lang": None,
    "n_merged": 0,
    "n_closed": 0,
    "n_open": 0,
    "last_mod": float("inf"),
    "merged_url": None,
    "open_url": None,
    "closed_url": None,
}


def create_json(g, prs):
    my_contribs = {}
    user = g.get_user()
    issues = None
    name = "issue"
    if prs:
        issues = g.search_issues(query="author:{} is:pr".format(user.login))
    else:
        issues = g.search_issues(query="author:{} is:issue".format(user.login))
    n_issues = issues.totalCount
    repo_name = None
    private_repos = set()
    for abc in issues:
        if prs:
            abc = abc.as_pull_request()
            name = "pr"
            repo_name = abc.url[abc.url.index("repos") + 6 : abc.url.index("pulls") - 1]
        else:
            repo_name = abc.url[
                abc.url.index("repos") + 6 : abc.url.index("issues") - 1
            ]
        if repo_name not in my_contribs and repo_name not in private_repos:
            my_contribs[repo_name] = repo.copy()
            r = g.get_repo(repo_name)
            if r.private is True:
                private_repos.add(repo_name)
                continue
            my_contribs[repo_name]["stars"] = r.stargazers_count

            repo_langs = list(r.get_languages().keys())
            if len(repo_langs) > 0:
                my_contribs[repo_name]["lang"] = repo_langs[0]
            else:
                my_contribs[repo_name]["lang"] = "GitHub"

            org, repo_ = repo_name.split("/")
            if prs:
                my_contribs[repo_name]["merged_url"] = (
                    "https://github.com/search?q=is%3Apr+repo%3A"
                    + org
                    + "%2F"
                    + repo_
                    + "+author%3A{}+is%3Amerged".format(user.login)
                )
            my_contribs[repo_name]["closed_url"] = (
                "https://github.com/search?q=is%3A"
                + name
                + "+repo%3A"
                + org
                + "%2F"
                + repo_
                + "+author%3A{}+is%3Aclosed".format(user.login)
            )
            my_contribs[repo_name]["open_url"] = (
                "https://github.com/search?q=is%3A"
                + name
                + "+repo%3A"
                + org
                + "%2F"
                + repo_
                + "+author%3A{}+is%3Aopen".format(user.login)
            )
        if prs and abc.merged:
            my_contribs[repo_name]["n_merged"] += 1
        elif abc.state == "closed":
            my_contribs[repo_name]["n_closed"] += 1
        else:
            my_contribs[repo_name]["n_open"] += 1
        my_contribs[repo_name]["last_mod"] = min(
            my_contribs[repo_name]["last_mod"], (datetime.today() - abc.updated_at.replace(tzinfo=None)).days
        )
    return my_contribs, n_issues


if __name__ == "__main__":
    # Install deps
    system("sudo apt update")
    system("sudo apt install wkhtmltopdf xvfb")
    system("pip3 install imgkit pillow")

    # Fetch Data
    g = Github(sys.argv[1])
    pulls, n_pulls = create_json(g, True)
    issues, n_issues = create_json(g, prs=False)
    my_contribs = json.dumps({"pulls": pulls, "issues": issues}, indent=4)
    with open("my_contribs.json", "w") as json_file:
        json.dump(my_contribs, json_file)
