Fixture for the github-paths firing tests. A small repository whose
slot files are all present and mostly in the wrong place: FUNDING.yml
and dependabot.yml at the root, CITATION.cff under docs/, two
CODEOWNERS files that disagree, contributing and security guidance
written into the project README, and a minified bundle committed with
no .gitattributes to mark it. Nothing here is broken in a way git or
CI would notice; each file is simply invisible to the feature it was
written for.
