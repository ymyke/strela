
These are internal notes that won't make much sense to anybody other than me...
-- ymyke







## Other dependencies

- What about MetricHistory? -- I guess this is part of alerts? Or should this be another
  separate package? If so, why? -- Or should the whole thing be a library and alerts,
  ticker, metric history etc. be packages within it?
  - See also the notes in tessa/DEVNOTES re this topic!


# Questions / TODOs

- Use tessa.symbols
- Make sure the strela package also works with a simple dict with the righth attributes
  in the end so it doesn't have to strictly rely on symbols. -- really??
- Get tests from fignal
- What to do w MetricHistory?
  - Get rid of it.
  - But keep the old code somewhere safe. -- Where? In some branch of fignal or strela.
  - This means we con't have P/E & P/S any longer.
- Where to put the shelves? (cf AlertState)
- Need some kind of config file that gets read w/?
  - Secrets such as mail pwd
  - Config such as alerts to be triggered??? -> tessa.symbols
- Use this? https://schedule.readthedocs.io/en/stable/examples.html


- Deployment:
  - Auf Pythonanywhere
  - Ueberwachungsscript nötig?
  - Auf X9 alle betr Prozesse löschen
  - Change the gmail app pwd

