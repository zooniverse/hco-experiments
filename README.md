# hco-experiments

## swap
### Get the data
[SNHunters_classification_dump_20170109.mat](https://www.dropbox.com/s/0sjkfhbxocnkbbb/SNHunters_classification_dump_20170109.mat?dl=0)

Same as above but with magnitude metadata.
[SNHunters_classification_dump_20170109_metadata.mat](https://www.dropbox.com/s/4i2ilou79tixc61/SNHunters_classification_dump_20170109_metadata.mat?dl=0)

### Usage Example

Process the .mat file:

```python
from swap import MATSWAP
swap = MATSWAP("SNHunters_classification_dump_20170109.mat")
swap.process()
swap.save("swap_SNHunters_classification_dump_20170109.mat")

```

## machine-learning
### Get the data
[Pan-STARRS1 Medium Deep training set](https://www.dropbox.com/s/dft3qpnfn3clv9y/md_20x20_skew4_SignPreserveNorm_with_confirmed1.mat?dl=0) - [Wright et al. 2015](https://arxiv.org/abs/1501.05470)

[Pan-STARRS1 3pi training set](https://www.dropbox.com/s/btzji6ug9ikwlwm/3pi_20x20_skew2_signPreserveNorm.mat?dl=0) - used to train Supernova Hunters classifier

[STL-10 dataset](https://cs.stanford.edu/~acoates/stl10/) - [Coates et al. 2011](http://cs.stanford.edu/~acoates/papers/coatesleeng_aistats_2011.pdf)

[STL-10 grayscale mean-subtracted patches](https://www.dropbox.com/s/gairqidpyjxtzah/patches_stl-10_unlabeled_meansub_20150409_psdb_6x6.mat?dl=0) - patches used to train sparse filter
