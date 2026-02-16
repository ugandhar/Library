# PR Submission Guide

If you don't see PRs in your GitHub repository, note that local commits and locally generated PR metadata do **not** create GitHub pull requests by themselves.

## What this repo currently has

The branch contains a stacked set of commits intended to be opened as separate PRs:

1. `1bbb900` - schema/bootstrap
2. `b7628eb` - backend data layer
3. `0ef9407` - books resource
4. `346d40c` - members resource
5. `05811d5` - lending resource
6. `fff5c9b` - protobuf contract
7. `90ee0e2` - frontend scaffold (historical)
8. `cad1bbd` - frontend books (historical)
9. `8490abb` - frontend members (historical)
10. `a79c643` - frontend lending/returns (historical)
11. `4ad3c0b` - docs
12. `e9b0f4c` - frontend moved to separate repository

## To create visible PRs on GitHub

1. Push your branch:
   ```bash
   git push -u origin work
   ```
2. Open GitHub and create PRs from `work` (or split branches) into your target base branch.
3. If you want one PR per logical change, create topic branches from the commit points above and push each branch.

