# Show-Your-Contributions
An automated workflow that generates/updates an HTML doc that showcases your GitHub contributions.

This Workflow will check your activities everyday at `00:00 UTC` and will automatically update the `contributrions.html` if it finds any new Contributions.

See it working for me [HERE](https://rushabh-v.github.io/contributions.html).
![my-contribs](https://rushabh-v.github.io/images/my-contribs.png)

## Usage Guide
1. Add a secret named `GIT_TOKEN` having your GitHub access token from `settings -> secrets -> new secret` to the repo you want to add this workflow to.
2. Go to `Actions -> New workflow -> set up a workflow yourself`, paste the following code there, and You're Done!

```yml
name: update-my-contributions
on:
  schedule:
   - cron: "0 0 * * *"

jobs:
  resources:
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
          python3 generate_doc.py ${{ secrets.GIT_TOKEN }}
      - name: Commit
        uses: test-room-7/action-update-file@v1
        with:
          file-path: |
            contributions.html
            total_contribs
          commit-msg: Update resources
          github-token: ${{ secrets.GIT_TOKEN }}

```
