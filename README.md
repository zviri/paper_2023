## Mining debt formation patterns
This repository contains the source code for all the experiments used for the paper *Mining debt formation patterns* submitted for review in 2023.

See the original paper for more details.

### Acknowledgment
I would like to thank the author of the pure python reimplementation of the gSpan algorithm ([betterenvi/gSpan](https://github.com/betterenvi/gSpan)) that was used as a basis to implement our own, extended version of the GERM algorithm, which you can find at ([zviri/gSpan](https://github.com/zviri/gSpan)).

### How to run the experiments

**Install requirements**:
* latest `docker`
* latest `docker-compose`

With requirements installed you can run the experiments simply by:
```
docker-compose run paper_2023
```

All the experiment data will be stored in the `data` folder.