# route-smoother

A script that can be used to smoothen traffic routes from a kml file.

It uses three filtering or smoothening logics
- smoothen by distance
- smoothen by angle
- smoothen by simplification
    

## Table of Contents
- [Dependencies](#Dependencies)
- [Usage](#Usage)
- [Smoothening Logics](#Smoothening-Logics)

##  Dependencies

### For windows OS
```
./windows-dependencies.sh

pip install requirements.txt
```


### Others 
```
pip install requirements.txt
```


## Usage
create a route object from a kml file.

```
route = Route("path/to/file.kml")
```

get the total distance of the route.
```
route.get_total_distance()
```

`
23.304
`

smoothen the route.
```
route.smoothen_route()
```

write the smoothened route to a kml file.
```
route.to_file("path/to/file.kml")
```

## Smoothening Logics

### Smoothen by distance
This method of smoothening is derived from the observation that sensor malfunctioning
causes sharp spike to a far coordinate from the current route. These spikes can be 
trimmed based on the assumption that there is a maximum allowed distance between two 
coordinates which is called the **cutoff distance**. The default value is 500 meters

### Smoothen by angle
This method of smoothening is derived from the observation that sensor malfunctioning
causes sharp spike angle away from the current route. These spikes can be 
trimmed based on the assumption that there is a minimum allowed angle between a
middle coordinate and the neighboring coordinates which is called the **cutoff angle**.
The default value is 45 degrees.

### Smoothen by simplification
This is derived from shapely simplify method [link](https://shapely.readthedocs.io/en/stable/manual.html#object.simplify)

The level at which the simplification occurs is relative to the **granular level**