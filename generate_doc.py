
from os.path import isfile
import sys
from github import Github

import imgkit
import json
from PIL import Image

g = Github(sys.argv[1])
user = g.get_user()
cur_contrib = 0

with open("templates.json", "r") as j:
    templates = json.load(j)

start = templates["start"].format(
    user.login,
    user.name if user.name is not None else user.login,
    user.avatar_url,
    user.name if user.name is not None else user.login,
)
middle = templates["middle"]
tail = templates["tail"]

with open("colors.json", "r") as j:
    lang_colors = json.load(j)

if isfile("total_contribs"):
    with open("total_contribs", "r") as f:
        try:
            prev_contrib = int(f.read())
        except:
            prev_contrib = -1
else:
    prev_contrib = -1


def add_row(contribs, key, is_pr):
    org, repo_name = key.split("/")
    merged_link = contribs[key]["merged_url"]
    open_link = contribs[key]["open_url"]
    closed_link = contribs[key]["closed_url"]
    n_merged = contribs[key]["n_merged"]
    n_open = contribs[key]["n_open"]
    n_closed = contribs[key]["n_closed"]
    lang = contribs[key]["lang"]
    n_days = contribs[key]["last_mod"]
    stars = contribs[key]["stars"]
    last_mod = ""

    if n_days >= 365: last_mod = str(n_days // 365) + " years ago"
    elif n_days > 30: last_mod = str(n_days // 30) + " months ago"
    elif n_days > 0:  last_mod = str(n_days) + " days ago"
    else:             last_mod = "today"

    if is_pr and (n_merged + n_open) == 0:
        return "", (n_merged + n_open + n_closed)

    lang_color = lang_colors[lang] if lang in lang_colors else "rgb(0,255,0)"

    repo_html = templates["pr_head"].format(org, repo_name, org, repo_name)
    if n_merged:
        repo_html += templates["pr_merged"].format(merged_link, n_merged)
    if n_open:
        repo_html += templates["pr_open"].format(open_link, n_open)
    if n_closed:
        repo_html += templates["pr_closed"].format(closed_link, n_closed)
    repo_html += templates["pr_tail"].format(lang_color, lang, stars, last_mod)

    return repo_html, (n_merged + n_open + n_closed)


def remove_prs_below_threshold(prs, threshold):
    filtered_prs = {}
    for repo, contrib in prs.items():
        if contrib["n_merged"] + contrib["n_open"] >= threshold:
            filtered_prs[repo] = contrib
    return filtered_prs


def generate_readme_image(readme_prs, readme_pr_keys):
    html = templates["head"] + templates["readme_start"]
    for key in readme_pr_keys:
        code, _ = add_row(readme_prs, key, True)
        html += code
    html += templates["readme_tail"]
    options = {"xvfb": ""}
    imgkit.from_string(html, "contributions.png", options=options)
    img = Image.open("contributions.png")
    _, height = img.size
    img = img.crop((120, 10, 730, height))
    width, height = int(610 * 0.60), int(height * 0.65)
    img = img.resize((width, height))
    img.save("contributions.png")


def save_profile_readme_txt():
    with open("profile_readme.txt", "w") as file:
        content = ("[![My contributions]" +
            "(https://{}.github.io/contributions.png)]".format(user.login) +
            "(https://{}.github.io/contributions)".format(user.login))
        file.write(content)


if __name__ == "__main__":
    with open("my_contribs.json", "r") as j:
        contribs = json.load(j)
    contribs = json.loads(contribs)
    try:
        threshold = int(sys.argv[2])
    except:
        threshold = 0

    issues = contribs["issues"]
    prs = contribs["pulls"]
    readme_prs = remove_prs_below_threshold(prs, threshold)

    get_count_pr = lambda d: (prs[d]["n_open"] + prs[d]["n_merged"])
    get_count_issue = lambda d: (issues[d]["n_open"] + issues[d]["n_closed"])

    pr_keys = sorted(prs.keys(), key=get_count_pr, reverse=True)
    issues_keys = sorted(issues.keys(), key=get_count_issue, reverse=True)
    readme_pr_keys = sorted(readme_prs.keys(), key=get_count_pr, reverse=True)

    html = templates["head"] + start
    for key in pr_keys:
        code, count = add_row(prs, key, is_pr=True)
        html += code
        cur_contrib += count

    html += middle
    for key in issues_keys:
        code, count = add_row(issues, key, False)
        html += code
        cur_contrib += count
    html += tail

    # Exit if no new contributions
    if prev_contrib == cur_contrib:
        if not isfile("profile_readme.txt"):
            save_profile_readme_txt()
        if not isfile("contributions.png"):
            generate_readme_image(readme_prs, readme_pr_keys)
        exit()

    generate_readme_image(readme_prs, readme_pr_keys)
    save_profile_readme_txt()
    with open("total_contribs", "w") as file:
        file.write(str(cur_contrib))
    with open("contributions.html", "w") as file:
        file.write(html)
