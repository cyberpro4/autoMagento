# autoMagento
Plugin directories and configurations generator for Magento 1.9.x written in Python

## Installation
Be sure to have Python 2.7 up and runnig on your system, then just put `autoMangento.py` inside your magento installation root directory (same directory of `index.php`).

## Syntax 

```
usage: autoMagento.py [-h] [-c COLLECTION] [-g GRID] [--version VERSION]
                      [--code CODE] [--base-path BASE_PATH]
                      [PLUGIN] [MODULE]

Magento 1.9.x plugin generator.

positional arguments:
  [PLUGIN]              Name of the plugin. Ex: Mage
  [MODULE]              Name of the plugin module. Ex: Core or Sales

optional arguments:
  -h, --help            show this help message and exit
  -c COLLECTION, --collection COLLECTION
                        Name of the collection to generate (Models and
                        Resources) Ex: Report
  -g GRID, --grid GRID  Name of adminhtml grid to generate Ex: Report
  --version VERSION     Base version in case of non-existing plugin (default
                        0.1.0)
  --code CODE           The code directory: core/local/community
  --base-path BASE_PATH
                        Magento installation root (default is current
                        directory)
```

## Examples
Just run on your console:

```python autoMagento.py MyCompany MyCustomModule```

This will create a new plugin the following directory/files structure:

```
/app
  /code
    /local
      /MyCompany
        /MyCustomModule
          /Blocks
          /controllers
          /etc
            /config.xml
          /Helper
            /Data.php
          /Model
          /sql
  /etc
    /modules
      /MyCompany_MyCustomModule.xml
```

Basic configuration file is also created:
```xml
<?xml version='1.0' encoding='utf8'?>
<config>
    <modules>
        <MyCompany_MyCustomModule>
            <version>0.1.0</version>
        </MyCompany_MyCustomModule>
    </modules>
    <global>
        <helpers>
            <mycompany_mycustommodule>
                <class>MyCompany_MyCustomModule_Helper</class>
            </mycompany_mycustommodule>
        </helpers>
    </global>
</config>
```

A basic Helper for the module:
```php
<?php
class MyCompany_MyCustomModule_Helper_Data extends Mage_Core_Helper_Abstract {
}
```

A module activation file:
```xml
<?xml version="1.0"?>
<config>
    <modules>
        <MyCompany_MyCustomModule>
            <active>true</active>
            <codePool>local</codePool>
        </MyCompany_MyCustomModule>
    </modules>
</config>
```

