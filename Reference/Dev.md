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

BismuthClient is another PIP module that targets walelts and dApps usage.

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

All code atm is only copied over from node or bismuthclient repo.    
Nothing is in working state nor coherent.

Worked on files will be added there in due time.

- structures.py  
  First draft of the core objects. Transaction class. Compact storage as native properties, and seamless read from/to any needed format.
  
- bismuthconfig.py  
  BismuthConfig class, settings loading and default values.  
  Reorganized key names.
  
- bismuthcore.py  
  First draft of the BismuthNode class
  
- combackend.py  
  Abstract ancestors for communication backends
  
- tornadobackend.py  
  First draft of an Async, tornado based communication backend.
  
- Utils/convert_db.py  
  First tests of db conversion to assess gain of storage space as well as alternatives storage format. 
  
- Utils/node_test.py  
  Non working draft of a Bismuth node.
