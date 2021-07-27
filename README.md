# flair-client
flair-client is an asynchronous wrapper to the [@flair-systems](https://github.com/flair-systems) API.
It was written to be used with home-assistant but can have other uses.

## Usage
```py
import flair_client

flair_client.make_client()
```

## TODO
* Error handling
* Ability to control more entity types (structures, rooms, etc.)
* Add a CLI (Maybe for another project)
* Change methods to rely on a single `make_client()` function rather than indepently await their dependencies ([source](https://github.com/flair-systems/flair-api-client-py/blob/master/flair_api/client.py#L340-L350))

## Credits
Much of the code was inspired from the original
[synchronous](https://github.com/flair-systems/) wrapper.
