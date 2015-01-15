---
layout: page
title: Overview
permalink: /
---
If you are looking for the git repo URL, it is: [https://github.com/OpenTreeOfLife/peyotl](https://github.com/OpenTreeOfLife/peyotl)


<code>peyotl</code> is a python package written to make it easier to
interact with the software produced by the [Open Tree of Life project] [1].
Specifically, to:

1. interact with a local version of the [phylesystem] [2] repository of curated phylogenetic studies ;

2. call web services associated with the studies (served by web app running the [phylesystem-api code] [3]);

3. call web services associated with taxonomic resolution services (running [taxomachine] [4] );

4. call web services associated with Open Tree of Life's "synthetic" estimate of the tree of life (running [treemachine] [5]);

5. call web services associated with an annotation database (that we have not built yet)

Currently peyotl is used to implement most of the functionality in the 
[phylesystem-api] [3] backend of the study curation tool.

## Documentation Table of Contents

  1. [Installation](./installation)
  2. [Configuration](./configuration)
  3. [Tutorials](./tutorial)
  4. [Testing](./testing)
  5. [Format conversion](./format-conversion)
  6. [NexSON validation](./nexson-validation)
  7. [Phylesystem](./phylesystem)
  8. [API wrappers](./api-wrappers)
  9. [Roadmap](./roadmap)

# Thanks

peyotl is primarily written by Mark Holder, Emily Jane McTavish, and Jim Allman, 
but see the [contributors file] [6] for a more complete list
of people who have contributed code.

The fabulous <a href="http://karlgude.com/about/">Karl Gude</a> created the logo.

Several parts of the setup.py, logging, documentation, and test suite were 
based on Jeet Sukumraran's work in the [DendroPy](http://pythonhosted.org/DendroPy/) package.

The sortattr.xslt stylesheet (which is only used in round-trip testing) is from 
   http://stackoverflow.com/questions/1429991/using-xsl-to-sort-attributes

The peyotl.phylesystem.git_actions (and the tests) were a part of the api.opentreeoflife.org
    repo which was primarily the work of Duke Leto (at that time).

Jim Allman, Karen Cranston, Cody Hinchliff, Mark Holder, Peter Midford, and Jonathon Rees
all participated in the discussions that led to the NexSON mapping.

The peyotl/test/data/nexson/phenoscape/nexml test file is from a [Phenoscape file](https://raw.github.com/phenoscape/phenoscape-data/master/Curation%20Files/completed-phenex-files/Characiformes/Buckup_1998.xml
) downloaded on Feb 16, 2014.  The citation for the data is in the nexml doc itself.

****************

*Etymology*: According to Wikipedia, peyotl is the Nahuatl word for [*Lophophora williamsii*](http://en.wikipedia.org/wiki/Lophophora_williamsii).

[1]: http://blog.opentreeoflife.org/
[2]: https://github.com/OpenTreeOfLife/phylesystem
[3]: https://github.com/OpenTreeOfLife/api.opentreeoflife.org/
[4]: https://github.com/OpenTreeOfLife/taxomachine
[5]: https://github.com/OpenTreeOfLife/treemachine
[6]: https://raw.githubusercontent.com/OpenTreeOfLife/peyotl/master/CONTRIBUTORS.txt