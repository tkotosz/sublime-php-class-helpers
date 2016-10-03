Sublime PHP Class Helper commands
=========================

`add_dependency` command:
------------
configure key binding like this:
```
{ "keys": ["ctrl+í"], "command": "add_dependency" }
```
It will show 2 input panel to read property name and property class then it will:
- add class property
- add constructor if not exists
- add constructor param
- add $this->property = $property to constructor
- triggers the SublimePHPCompanion's find_use command to add use statement for the property's class if can be found
- triggers the DocBlockr's jsdocs command to create/update constructor docblock
- add use statement for the property's class if can be found (this one uses the SublimePHPCompanion find_use command)
Result:
```php
<?php

use Symfony\Component\Filesystem\Filesystem;

/**
 * My test class
 */
class TestClass
{
    /**
     * @var Filesystem
     */
    private $filesystem;
    
    /**
     * @param Filesystem $filesystem
     */
    public function __construct(Filesystem $filesystem)
    {
        $this->filesystem = $filesystem;
    }
}
```

