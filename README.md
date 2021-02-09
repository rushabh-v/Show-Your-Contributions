# Show-Your-Contributions
- An automated workflow that generates/updates your **GitHub page (Website)** and your **GitHub profile readme** to showcases your GitHub contributions.
- It will check your activities every day at `00:00 UTC` and will automatically update the `contributrions.html` if it finds any new Contributions.

See it working: [GitHub page](https://rushabh-v.github.io/contributions) | [GitHub profile readme](https://github.com/rushabh-v/)


![my-contribs](https://rushabh-v.github.io/images/my-contribs.png)

## Usage Guide
1. Generate a `Personal access token` from `Account settings -> Developer settings -> Personal access tokens`.
2. Add a secret named `GIT_TOKEN` having your that `personal access token` from `repo settings -> secrets -> new secret` to the repo you want to add this workflow to.

3. Go to `Actions -> New workflow -> set up a workflow yourself`, paste the following code snippet there, replace `PR_THRESHOLD` with your desired threshold, commit, and it will add a document named `contributions.html` in that repo which will automatically get updated on your new contributions (On the first occurrence of `00:00 UTC` after your contribution).

- For profile readme setup, you can decide the `PR_THRESHOLD/minimum number of your PRs` for a repo to be included in your profile readme. That means you can set a number - `PR_THRESHOLD`, and all the repos to which you have made more than `PR_THRESHOLD` number of PRs will be added to the list of your contributions in your profile readme. **Any repo crossing the threshold will be automatically appended to your profile readme in the future.**


**Note**: Replace`<PR_THRESHOLD>` on line 20 with your desired threshold to set up profile readme, Leave otherwise.

```yml
name: update-my-contributions
on:
  push:
   paths: ".github/workflows/*"
  schedule:
   - cron: "0 0 * * *"

jobs:
  main:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v1
      - uses: actions/setup-node@v1
      - name: Get Updates
        run: |
          sudo apt install python3-setuptools
          git clone https://github.com/rushabh-v/Show-Your-Contributions
          cp -r ./Show-Your-Contributions/* ./
          pip3 install pygithub
          python3 fetch_contribs.py ${{ secrets.GIT_TOKEN }}
          python3 generate_doc.py ${{ secrets.GIT_TOKEN }} <PR_THRESHOLD>
      - name: Commit
        uses: test-room-7/action-update-file@v1
        with:
          file-path: |
            contributions.html
            contributions.png
            total_contribs
            profile_readme.txt
          commit-msg: Update resources
          github-token: ${{ secrets.GIT_TOKEN }}
```

### Profile readme setup
After completing the above steps, paste the following line into your profile readme and replace `<username>` with your username, and commit.
Or you can find your personalized line in the file named `profile_readme.txt` in your GitHub pages' repo.

```markdown
[![My contributions](https://<username>.github.io/contributions.png)](https://<username>.github.io/contributions)
```
