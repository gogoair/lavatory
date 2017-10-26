# ArtifactoryPurge

Artifactory tooling for managing repository specific retention policies

## Authentication

This tool looks for 3 enviroment variables in order to authenticate:

`ARTIFACTORY_URL` - Base URL to use for Artifactory connections
`ARTIFACTORY_USERNAME` - Username to Artifactory
`ARTIFACTORY_PASSWORD` - Password for Artifactory

These will be loaded in at the beginning of a run and raise an exception if missing.