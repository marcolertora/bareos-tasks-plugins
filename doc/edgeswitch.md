# BareOS FileDaemon EdgeSwitch Plugin
This plugin makes backup of Ubiquity Edge Switch. It can be used to back up device configuration
To restore select the needed file, found in */@EDGESWITCH* in the catalog.

## Prerequisites
The plugins have been developed and tested with Ubiquity Edge Switch v1.8.2

You need the packages *bareos-filedaemon-python-plugin* installed on your client.

You need these python libraries:
* requests

## Installation
1. Make sure you have met the prerequisites.
2. Install the files *BareosFdTaskClass.py*, *xenserver/BareosFdEdgeSwitchClass.py* and *xenserver/bareos-fd-edgeswitch.py* in your Bareos plugin directory (usually */usr/lib/bareos/plugins*)

## Configuration

Activate your plugin directory in the *fd* resource configuration on the client
```
FileDaemon {                          
    Name = client-fd
    ...
    Plugin Directory = /usr/lib/bareos/plugins
}
```

Include the Plugin in the fileset definition on the director
```
FileSet {
    Name = "client-data"
        Include  {
            Options {
                compression = LZO
                signature = MD5
            }
            File = /etc
            #...
            Plugin = "python:module_path=/usr/lib/bareos/plugins:module_name=bareos-fd-edgeswitch:host=192.168.1.1:username=admin:password=secret"
        }
    }
}
```

### Options
You can append options to the plugin call as key=value pairs, separated by ':'.
Please read more about the BareOS Python Plugin Interface here: http://doc.bareos.org/master/html/bareos-manual-main-reference.html#Python-fdPlugin

Example plugin options:
```
    Plugin = "python:module_path=/usr/lib/bareos/plugins:module_name=bareos-fd-edgeswitch:host=192.168.1.1:username=admin:password=secret"
```

#### folder
Virtual folder used in catalog. Default: *@EDGESWITCH*

#### host
Specifies the host of the device. Required

#### username
Specifies the username of the device. Required

#### password
Specifies the password of the device. Required