

Creating Retention Policies
===========================

.. toctree::
   :maxdepth: 2
   
.. contents::
   :local:

Lavatory policies are implemented as Python plugins. Each policy is a ``.py`` file named
after an Artifactory repository.

Each plugin represents one repository. The file name should match the repository name,
replacing ``-`` with ``_``.

For example, the repository ``yum-local`` should have a retention policy named ``yum_local.py``

Anatomy of a Policy 
-------------------

Each policy needs to provide one function, ``purgelist(artifactory)``. 
This function takes one arguement, ``artifactory`` which is an object containing
artifactory specific functions. 

This function needs to return a list of artifacts to delete.

Entry Function 
~~~~~~~~~~~~~~

The entrypoint to a policy is the function ``def purgelist(artifactory)``.
The argument is an instance of the ``lavatory.utils.artifactory.Artifactory`` class
and handles all communication with artifactory.

Docstring Description
~~~~~~~~~~~~~~~~~~~~~

The docstring following the function definition will be used as the policy description.
This gets used in logging, as well as generating a list of all active policies. 


Return Value
~~~~~~~~~~~~

The return value of the policy should be a list of artifacts to delete.
The artifacts are a dictionary that at minimum needs a ``path`` and ``name`` key.
These keys are used by the delete function to remove the artifact.

``path``: path to artifact in the repository

``name``: Name of the artifact

Example Minimal Return:

::

    [{ 'path': '222', 'name': 'Application-10.6.0-10.6.0.07-9cd3c33.iso'}]


This will delete artifact ``<repo_name>/222/Application-10.6.0-10.6.0.07-9cd3c33.iso``

.. include:: policy_helpers.rst