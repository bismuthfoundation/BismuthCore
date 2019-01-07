# Dev doc & FAQ


## Work on node and BismuthCore

You have one git with node repo, one git with bismuthcore.  
In your node repo, add "bismuthcore" to your .gitignore file, then symlink the bismuthcore/bismuthcore dir from the bismuthcore repo to your node repo.  
This way, you will use your local version instead of the pip one, but still be able to git commit your changes to bismuthcore.

## Standards

- Conform to PEP 8 as much as possible.

- Use consistent naming, do not hesitate to use full_explicit_variables_names

- Dup code is a candidate for rework. Use an helper function or class.

- Use type hinting as much as possible

- fStrings are the preferred way to format things. % is to be avoided, .format() is to be updated to fStrings.

- Requirements go into setup.py

## Relationship to BismuthClient

BismuthClient is another PIP module that targets wallets and dApps usage.

However, some classes and code can be common to both packages.  
Why the need for clear versioning and a version number in every class file.  
Goal would be to work only on one version a time, keep compatibility if possible, and keep both package in the same state as long as possible.

An alternative would be to have BismuthCore require BismuthClient.

## Publish to Pypi

See  
https://manikos.github.io/a-tour-on-python-packaging  
For the whole packaging process.

In practice:

- edit setup.py, bump version
- update HISTORY.rst
- make docs
- make clean
- git commit & push
- make release

## Status

Code begins to be sorted out but far from final.      
Nothing is supposed to be in working state nor coherent yet.

Worked on files are listed thereafter with comments being edited as work goes on.

- structures.py  
  First draft of the core objects. Transaction class. Compact storage as native properties, and seamless read from/to any needed format.  
  Lowlevel objects, not supposed to be worked on once working.  
  
- bismuthconfig.py  
  BismuthConfig class, settings loading and default values.  
  Reorganized key names.
  Lowlevel object, not supposed to be worked on once working, except for adding config items.
  
- bismuthcore.py  
  First draft of the main BismuthNode class
  
- combackend.py  
  Abstract ancestors for communication backends  
  Lowlevel object, not supposed to be worked on once working.
    
- tornadobackend.py  
  First draft of an Async, tornado based communication backend.  
  Lowlevel object, not supposed to be worked on once working. 

- helpers.py  
  Helper classes and functions.  
  Lowlevel object, not supposed to be worked on once working.
  
- clientcommands.py  
  Handler for the commands used by the core clients, not the node themselves.
  
- Utils/convert_db.py  
  First tests of db conversion to assess gain of storage space as well as alternatives storage format. 
  
- Utils/bisnode.py  
  Draft of a Bismuth node/daemon. Answers to statusjson only.


## Client

- Use Antimony
