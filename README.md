# strela - a python package for financial alerts 📈🚨📉

strela provides a toolbox to generate and send different kinds of alerts based on
financial information.

The package is intended to be used to write a Python script that can be scheduled via
cronjob or similar facilities and runs everything necessary according to your needs. See
`strela.my_runner` as an example.

## Features & overview

- `strela.alert_generator`: The central logic that brings all the building blocks
  together to retrieve and analyze the financial metrics and to generate and send alerts
  if applicable.
- `strela.alertstates.alertstate.AlertState`: The abstract base class for all alert
  states. Alert states encapsulate the logic to determine whether an alert has triggered
  or not. There are two concrete types of alerts:
    - `strela.alertstates.fluctulertstate.FluctulertState`: Alerts for fluctuations (up
      or down) over certain thresholds.
    - `strela.alertstates.doubledownalertstate.DoubleDownAlertState`: Alerts for
      significant downward movement which could trigger an over-proportional buy.
- `strela.templates`: Classes to turn alerts into text or html strings that can be
  printed or mailed.
- `strela.mailer`: To send alerts via email.
- `strela.config`: Configuration management. Use the override mechanism described there
  to put your own user config file in place that overrides the settings in the default
  config file according to your environment.
- `strela.my_runner`: The script that brings it all together and runs the alert
  generator according to your requirements. Use this script as a blueprint to build your
  own runner script.
- `strela.alertstates.alertstaterepository`: Repositories (in memory or on disk) to
  store and retrieve alert states.

## How to install and use

1. Install the package. Two options:
   - `pip install strela`
   - Clone the repository and install the requirements using poetry.
2. Set up your config file `my_config.py` based on the documentation in `strela.config`.
   (Review your config via `strela.config.print_current_configuation`.)
3. Write your own runner script based on the blueprint in `strela.my_runner`. (Test your
   script by running it and -- if necessary -- setting `strela.config.ENABLE_ALL_DOWS`
   and/or `strela.config.NO_MAIL` to `True`.)
4. Install your runner script as a daily cronjob or similar.

## Limitations

The overall software architecture does feature decent modularization and separation of
concerns, but also have a lot of room left for improvement. E.g., better separation of
concerns in AlertStates (they mix logic and output currently), better parametrization of
alert states and templates, better extensibility, etc. 

## strela vs tessa

The strela package works seamlessly with [tessa](https://github.com/ymyke/tessa) and its
Symbol class and financial information access functionality.

At the same time, care was taken to make strela open and flexible enough to be used with
other packages and/or your own code.

Still, many or most people will end up using strela together with tessa so it's worth
discussing whether strela should be incorporated into tessa.

I decided to keep strela separate from tessa because strela has a distinctly different
character: a) it is not purely a library but needs some script to be built on top and
then called as a CLI tool / cronjob, b) it tends to rely on external files such as a
list of symbols to be loaded, c) it needs a place to store the alert state (and will
fail if that place doesn't exist, which seems to be unacceptable behavior for a pure
library such as tessa).

But I would like to have your thoughts on this. Should strela and tessa be separate
packages or better both in one? [Add your thoughts to the respective
issue.](https://github.com/ymyke/strela/issues/1)

## A note on tests

Some of the tests hit the net and are marked as such with `pytest.mark.net`.

