import io
import h5py

def write_empty_file(filename):
    # Create a new file using default properties.
    fh = h5py.File(filename,'w')
    fh.close()

def read_file_image(filename):
    with open(filename, mode='rb') as fh:
        file_bytes = fh.read()
        # read file into byte array
        file_image = h5py.h5f.open_file_image(file_bytes
                                           , h5py.h5f.FILE_IMAGE_OPEN_RW
                                            ).get_file_image()
        return file_image

def get_empty_file_image():
    bio = io.BytesIO()
    fh = h5py.File(bio, mode='w')
    fh.flush()

    return bio.getvalue()


def get_memory_file_id():
            
    file_image = get_empty_file_image()
    
    # file access property list
    fapl = h5py.h5p.create(h5py.h5p.FILE_ACCESS)
    fapl.set_fapl_core(backing_store=False) # in mem only
    fapl.set_file_image(file_image)

    # encode str as bytes object
    bname = 'core.h5'.encode()
    # open file image as file (filename only used upon file system 
    # write)
    file_id = h5py.h5f.open(fapl=fapl
                          , flags=h5py.h5f.ACC_RDWR
                          , name=bname
                           )
    return file_id

if __name__ == '__main__':
    import sys
    print(sys.version) # v3
    print(h5py.version.hdf5_version)
    print(h5py.__version__)
    #write_empty_file('test.h5')

    file_image = get_empty_file_image()

    #print(type(file_image))
    #print(len(file_image))

    # file access property list
    fapl = h5py.h5p.create(h5py.h5p.FILE_ACCESS)
    fapl.set_fapl_core(backing_store=False) # in mem only
    fapl.set_file_image(file_image)

    # encode str as bytes object
    bname = 'core.h5'.encode()
    # open file image as file (filename only used upon file system write)
    file_id = h5py.h5f.open(fapl=fapl
                          , flags=h5py.h5f.ACC_RDWR#ACC_RDONLY
                          , name=bname
                           )

    # create group
    with h5py.File(file_id, mode='w') as root:
        root.create_group("dda")
        # update in memory file image
        root.flush()
        # save changes as image
        afile_image = file_id.get_file_image()

    # change backing store to file system
    fapl.set_fapl_core(backing_store=True)
    # set changed file image
    fapl.set_file_image(afile_image)
    file_id = h5py.h5f.open(fapl=fapl
                          , flags=h5py.h5f.ACC_RDWR
                          , name='test.h5'.encode()
                           )

    # write changed file image to file
    with h5py.File(file_id, mode='w') as root:
        root.flush()

    wfile_image = read_file_image('test.h5')

    print('length empty image', len(file_image)
        , 'length test image', len(wfile_image)
         )
    print('sum empty image', sum(file_image)
        , 'sum test image', sum(wfile_image)
         )
