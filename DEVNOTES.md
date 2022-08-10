
These are internal notes that won't make much sense to anybody other than me...
-- ymyke







## Other dependencies

- What about MetricHistory? -- I guess this is part of alerts? Or should this be another
  separate package? If so, why? -- Or should the whole thing be a library and alerts,
  ticker, metric history etc. be packages within it?
  - See also the notes in tessa/DEVNOTES re this topic!


# Questions / TODOs

- What about config.py?
- Rename all string.* to text.*
- Use tessa.symbols
- Get rid of the term "ticker"
- What to do w MetricHistory?
  - Get rid of it.
  - But keep the old code somewhere safe. -- Where? In some branch of fignal or strela.
  - This means we con't have P/E & P/S any longer.
- Need some kind of config file that gets read w/?
  - Secrets such as mail pwd
  - Enabling overrides: "What I've done in the past is to have a default config file
    which is checked in to source control. Then, each developer has their own override
    config file which is excluded from source control. The app first loads the default,
    and then if the override file is present, loads that and uses any settings from the
    override in preference to the default file."
- Look for all occurences of personal information such as my mail address or my name
- Mark all the tests that hit the network -- like in tessa.
- Improve doc, add pdoc
- Check all imports and maybe "nicify".
- Document this: (from https://yagmail.readthedocs.io/en/latest/setup.html)
  import yagmail
  yagmail.register('mygmailusername', 'mygmailpassword')
  (this is just a wrapper for keyring.set_password('yagmail', 'mygmailusername', 'mygmailpassword')) Now, instantiating yagmail.SMTP is as easy as doing:
  -- or --, support uid/pwd -- or both somehow?
  -> https://yagmail.readthedocs.io/en/latest/usage.html


- Deployment:
  - Auf Pythonanywhere
  - Ueberwachungsscript nötig?
  - Auf X9 alle betr Prozesse löschen
  - Change the gmail app pwd

# later

- If I end up renaming the package or integrating into tessa: Find all occurences of
  "strela" and adapt accordingly.
- Where would mysymbols.yaml later "live"? Put it in a gist?
