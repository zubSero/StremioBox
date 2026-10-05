# Contributing

Hardware reports, focused fixes and documentation improvements are welcome. Start with [Discussions](https://github.com/zubSero/StremioBox/discussions) for general questions and use the issue forms for a reproducible bug or another hardware configuration.

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
