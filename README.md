# Pycord rest
The goal of this repository is to make pycord work with discord's http interactions, as described [here](https://discord.com/developers/docs/interactions/receiving-and-responding#receiving-an-interaction) and [here](https://discord.com/developers/docs/interactions/overview#preparing-for-interactions).

To implement this, I will use:
- fastapi - for the webserver
- py-cord - for http only methods and reusing the command builders

This would essentially be a wrapper of pycord providing its own classes and methods.

todo:
- [ ] webserver
- [ ] Slash commands
- [ ] Slash options
- [ ] Slash autocomplete
- [ ] UI components
