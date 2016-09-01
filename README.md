TaCo Server ![Caleydo Web Server Plugin](https://img.shields.io/badge/Caleydo%20Web-Server-10ACDF.svg)
=====================

TaCo (for **Ta**ble **Co**mparison) is an interactive comparison tool that effectively visualizes the differences between multiple tables at various levels of granularity.


Installation
------------

[Set up a virtual machine using Vagrant](http://www.caleydo.org/documentation/vagrant/) and run these commands inside the virtual machine:

```bash
./manage.sh clone Caleydo/taco_server
./manage.sh resolve
```

If you want this plugin to be dynamically resolved as part of another application of plugin, you need to add it as a peer dependency to the _package.json_ of the application or plugin it should belong to:

```json
{
  "peerDependencies": {
    "taco_server": "*"
  }
}
```

To use TaCo make sure that you installed the [TaCo application](Caleydo/taco).

Generating artificial data
------------

The server part comes with a Python table generator and modifier.

For now it reads a csv file and modify it randomly using the following operations:

* Add random rows
* Add random columns
* Delete random rows
* Delete random columns
* Modify random cells


***

<a href="https://caleydo.org"><img src="http://caleydo.org/assets/images/logos/caleydo.svg" align="left" width="200px" hspace="10" vspace="6"></a>
This repository is part of **[Caleydo Web](http://caleydo.org/)**, a platform for developing web-based visualization applications. For tutorials, API docs, and more information about the build and deployment process, see the [documentation page](http://caleydo.org/documentation/).
