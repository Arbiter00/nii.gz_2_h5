import nibabel as nib
import h5py
import os
import argparse
import numpy as np
import lzma

# transfer h5 to nii.gz

def h5_to_nifti(h5_path, nii_path):
    # Load the .h5 file
    with h5py.File(h5_path, 'r') as h5_file:
        # Extract affine matrix from the root group
        affine_matrix = np.array(h5_file.attrs['affine_matrix'])

        # Extract header information from the header group
        nii_header = {}
        for key, value in h5_file['header'].attrs.items():
            nii_header[key] = value

        # Reconstruct the NIfTI data from compressed blocks
        img_shape = nii_header['dim'][1:4]
        nii_data = np.zeros(img_shape, dtype=np.int16)
        block_size = (64, 64, 64)

        for i in range(img_shape[0] // block_size[0] + 1):
            for j in range(img_shape[1] // block_size[1] + 1):
                for k in range(img_shape[2] // block_size[2] + 1):
                    data_name = f'block_{i}_{j}_{k}'
                    if data_name in h5_file:
                        compressed_data = h5_file[data_name][:]
                        compressed_data = bytes(compressed_data)  # Convert to bytes
                        
                        # Check if compressed data is empty before decompression
                        if compressed_data:
                            decompressed_data = np.frombuffer(lzma.decompress(compressed_data), dtype=np.int16)

                            # Calculate the start and end index of the block
                            start_idx = (i * block_size[0], j * block_size[1], k * block_size[2])
                            end_idx = (min((i + 1) * block_size[0], img_shape[0]),
                                       min((j + 1) * block_size[1], img_shape[1]),
                                       min((k + 1) * block_size[2], img_shape[2]))

                            # Ensure decompressed data size matches block size
                            expected_size = np.prod(np.array(end_idx) - np.array(start_idx))
                            decompressed_data = decompressed_data[:expected_size]

                            # Fill the NIfTI data with decompressed block data
                            nii_data[start_idx[0]:end_idx[0], start_idx[1]:end_idx[1], start_idx[2]:end_idx[2]] = decompressed_data.reshape(
                                end_idx[0] - start_idx[0], end_idx[1] - start_idx[1], end_idx[2] - start_idx[2])

        # Save the reconstructed NIfTI data to a .nii.gz file
        nib.save(nib.Nifti1Image(nii_data, affine_matrix), nii_path)
    
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
    
    parser.add_argument('--datapath', type=str, default='/home/ylai/code/niigz2h5/test_save', help='path to the dataset')
    parser.add_argument('--savepath', type=str, default='/home/ylai/code/niigz2h5/test_save', help='path to save the h5 files')
    
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
