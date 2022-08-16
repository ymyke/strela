
These are internal notes that won't make much sense to anybody other than me...
-- ymyke







# Questions / TODOs

- Deployment:
  - Auf Pythonanywhere
  - Ueberwachungsscript nötig?
  - Auf X9 alle betr Prozesse löschen -- auch das prod Verzeichnis in code/

- Make this a separate package "strela" or incorporate into "tessa"?
  - Maybe keep it a separate package bc it has such a different character: a) not purely
    a library, but needs some script to be built on top and then called as a CLI tool,
    b) relies on external files such as symbols, c) needs a place to store the alert
    state (and will fail if that place doesn't exist -- this seems to be unacceptable
    behavior for a pure library such as tessa).
  - Maybe having strela as a sub package of tessa might be an option?
- If I still end up renaming the package or integrating into tessa: Find all occurences
  of "strela" and adapt accordingly.
- Improve what/how symbols are exposed by this package and simplify some of the import
  statements in the modules.
- Switch to production tessa library once the add-symbols branch is released.
- Improve doc, add pdoc, README (if standalone package)
