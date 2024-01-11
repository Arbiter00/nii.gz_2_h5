import nibabel as nib
import h5py
import os
import argparse
import numpy as np

# transfer h5 to nii.gz

def h5_to_nifti(h5_path, nifti_path):
    with h5py.File(h5_path, 'r') as h5f:
        data = np.array(h5f['nii_data'])
        header_group = h5f.get('header')
        header_dict = {key: header_group.attrs[key] for key in header_group.attrs.keys()}
        affine_matrix = np.array(h5f.attrs['affine_matrix'])

    header = nib.Nifti1Header()
    for key, value in header_dict.items():
        header[key] = value
        
    # Create nii image
    nii_img = nib.Nifti1Image(data, affine=affine_matrix, header=header)

    # Save nii image
    nib.save(nii_img, nifti_path)
    
def batch_h5_to_nifti(h5_folder, nifti_folder):
    # Get a list of all .h5 files in the folder
    h5_files = [f for f in os.listdir(h5_folder) if f.endswith('.h5')]

    # Convert each .h5 file to .nii.gz
    for h5_file in h5_files:
        # Get the path to the .h5 file
        h5_path = os.path.join(h5_folder, h5_file)
        # Get the path to the .nii.gz file
        nifti_path = os.path.join(nifti_folder, h5_file.replace('.h5', '.nii.gz'))
        # Convert
        print('Converting {} to {}'.format(h5_path, nifti_path))
        h5_to_nifti(h5_path, nifti_path)
    
def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--datapath', type=str, default='/ccvl/net/ccvl15/ylai45/ccvl14/h5', help='path to the dataset')
    parser.add_argument('--savepath', type=str, default='/ccvl/net/ccvl15/ylai45/ccvl14/h5', help='path to save the h5 files')
    
    args = parser.parse_args()
    
    
    datapath = args.datapath
    img_path = os.path.join(datapath, 'img')
    label_path = os.path.join(datapath, 'label')
    
    save_path = args.savepath
    save_img_path = os.path.join(save_path, 'img')
    save_label_path = os.path.join(save_path, 'label')
    
    # Create directories if not exist
    os.makedirs(save_img_path, exist_ok=True)
    os.makedirs(save_label_path, exist_ok=True)
    
    
    batch_h5_to_nifti(img_path, save_img_path)
    batch_h5_to_nifti(label_path, save_label_path)
    
    
    
if __name__ == "__main__":
    main()
