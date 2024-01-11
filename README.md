# nii.gz_2_h5
Script for transferring nii.gz CT images to h5 file.

## 0. Installation

```bash
pip install -r requirements.txt
```

## 1. Transfer

```bash
datapath=/ccvl/net/ccvl15/zzhou82/PublicAbdominalData/05_KiTS
savepath=/ccvl/net/ccvl15/ylai45/ccvl14/h5
python niigz2h5.py --datapath $datapath --savepath $savepath
```
