

Creating Retention Policies
===========================

.. toctree::
   :maxdepth: 2
   
.. contents::
   :local:

Lavatory policies are implemented as Python plugins. Each policy is a ``.py`` file named
after an Artifactory repository.

Each file/plugin represents one repository. The file name should match the 
repository name, replacing ``-`` with ``_``.

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

Return Value
~~~~~~~~~~~~

The return value of the policy should be a list of artifacts to delete.
The artifacts are a dictionary that at minimum needs a ``path`` and ``name`` key.
These keys are used by the delete function to remove the artifact.

.. include:: example_policies.rst