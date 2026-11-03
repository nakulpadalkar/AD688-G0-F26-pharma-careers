# Synchronize, build and publish main

- [x] G1: All remote branches inspected; source changes preserved and publication branch kept separate.
  MANUAL: Fetch all remotes, inspect branch ancestry and local changes.
- [x] G2: Rebuild all eight pages and verify inventory, local links, resources and dashboard behavior.
  CHECK: python scripts/verify_site.py
  EXPECT: EVIDENCE_OK
- [x] G3: Review and commit source updates, build outputs and cleanup separately; no private raw data staged.
  MANUAL: Inspect staged paths, diff checks, removal inventory and commit summaries.
- [x] G4: Push main and verify remote equality, empty status and empty stash list.
  MANUAL: Fetch remote main; compare HEAD, status and stash output.

Evidence: PowerShell, repository root: fetch --all --prune succeeded; main equals origin/main before local commits, only additional remote branch is generated gh-pages; no stashes or symlinks. Quarto render exited 0 after stopping existing preview and clearing cache. Inventory, JS syntax and dashboard checks exited 0; EVIDENCE_OK reports 282 links and anchors. Two redundant preview trees and root HTML copies removed. No local server started.


G3 evidence: source and curated evidence committed separately from _site. Source whitespace checks passed; generated Quarto template whitespace retained. Raw extracts, environment files and temporary previews excluded. Existing task gates and lessons retained as project records.

G4 evidence: PowerShell in repository root: push of d1dac34 succeeded; verification fetch confirmed HEAD equals origin/main, status --porcelain and stash list empty. All four gates met; zero unmet or abandoned. Final receipt commit is verified again after push.
