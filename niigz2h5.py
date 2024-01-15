import nibabel as nib
import h5py
import os
import argparse

def convert_nii_to_h5(nii_path, h5_path):
    # Load the .nii.gz file using nibabel
    nii_img = nib.load(nii_path)
    nii_data = nii_img.get_fdata()
    #meta data
    nii_header = nii_img.header
    affine_matrix = nii_img.affine

    #block compress
    block_size = (64, 64, 64)
    img_shape = nii_data.shape
    num_blocks = [int(np.ceil(dimension / block_size[i])) for i, dimension in enumerate(img_shape)]
    
    with h5py.File(h5_path, 'w') as h5_file:
        for i in range(num_blocks[0]):
            for j in range(num_blocks[1]):
                for k in range(num_blocks[2]):
                    # calculate the start and end index of the block
                    start_idx = (i * block_size[0], j * block_size[1], k * block_size[2])
                    end_idx = (min((i + 1) * block_size[0], img_shape[0]),
                            min((j + 1) * block_size[1], img_shape[1]),
                            min((k + 1) * block_size[2], img_shape[2]))

                    # the block data
                    block_data = nii_data[start_idx[0]:end_idx[0], start_idx[1]:end_idx[1], start_idx[2]:end_idx[2]]

                    # compress the block data
                    block_data = block_data.astype(np.int16)
                    compressed_data = lzma.compress(bytes(block_data))
                    dataset_name = f'block_{i}_{j}_{k}'
                    compressed_data = compressed_data[:len(compressed_data) // 2 * 2]
                    h5_file.create_dataset(dataset_name, data=np.frombuffer(compressed_data, dtype=np.int16))

        # write affine matrix to the root group
        h5_file.attrs['affine_matrix'] = affine_matrix.tolist()

        # write header to the header group
        header_group = h5_file.create_group('header')
        for key, value in nii_header.items():
            header_group.attrs[key] = value
       
        

def batch_convert_nii_to_h5(nii_folder, h5_folder):
    # get nii files
    nii_files = os.listdir(nii_folder)

    # create h5_folder if not exists
    for nii_file in nii_files:
        if not nii_file.startswith('._'):
            if nii_file.endswith('.nii.gz'):
                # get nii path
                nii_path = os.path.join(nii_folder, nii_file)
                # h5 path
                h5_path = os.path.join(h5_folder, nii_file.replace('.nii.gz','.h5'))
                # convert
                print('Converting {} to {}'.format(nii_path, h5_path))
                convert_nii_to_h5(nii_path, h5_path)


def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--datapath', type=str, default='/ccvl/net/ccvl15/zzhou82/PublicAbdominalData/05_KiTS', help='path to the dataset')
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
    
    
    batch_convert_nii_to_h5(img_path, save_img_path)
    batch_convert_nii_to_h5(label_path, save_label_path)
    
    
    
if __name__ == "__main__":
    main()

    
    
    
if __name__ == "__main__":
    main()
