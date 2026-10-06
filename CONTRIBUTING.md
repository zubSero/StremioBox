# Contributing

Anyone is welcome to submit updates through a pull request: bug fixes, hardware support, translations, documentation and other improvements. You can open a PR directly without asking for permission first. Changes are reviewed before merging.

Start with [Discussions](https://github.com/zubSero/StremioBox/discussions) for general questions and use the issue forms for a reproducible bug or another hardware configuration.

## Submit an update

1. [Fork StremioBox](https://github.com/zubSero/StremioBox/fork) to your GitHub account.
2. Create a branch in your fork, make your changes and run the relevant checks below.
3. Commit and push that branch to your fork.
4. [Open a pull request](https://github.com/zubSero/StremioBox/compare) from your fork's branch into `zubSero/StremioBox:main`. On the comparison page, choose **compare across forks** if needed.
5. Explain what changed and how you tested it using the PR template. Draft PRs are welcome if you want feedback while working.

You do not need write access to the upstream repository to contribute this way. Source and documentation updates are welcome; release images are published separately after validation.

## Before a change

Read the [architecture](docs/architecture.md), [hardware limits](docs/hardware.md) and [build scope](docs/building.md). Keep patches scoped to the NUC TV product where possible. Explain the visible behavior your change addresses, rather than claiming broad compatibility from one machine.

## Local checks

Python 3.10+ is sufficient for repository checks:

```sh
python3 tools/validate.py
python3 -m unittest discover -s tests -v
```

For changes to playback or power management, include relevant physical testing: codec/profile, resolution/frame rate, TV mode, audio output, remote recovery and reboot behavior. CI does not run Android or test a television.

## Pull requests

- Keep a PR focused and explain the trigger, resulting behavior and validation.
- Preserve upstream license notices. Include provenance when importing a patch.
- If changing a locked asset or patch intentionally, update its recorded SHA-256 and explain the new input.
- Do not commit disk images, private signing material, device data, accounts or raw logs with personal details.
- Do not regenerate the release image identity for unrelated documentation changes.

By contributing original material you agree to its applicable repository license. Platform edits remain under their upstream licenses; this repository's MIT license does not relicense them.
