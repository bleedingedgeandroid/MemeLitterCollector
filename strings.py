release_notes = '''
{data}

## How to use these files to get a working image:
1) Download all .tgz.part files(if you want fastboot file) or .zip.part(if you want recovery file)
2)
    - On Linux:
        - Run `cat {fileparts_tgz} > {filename_fb}` or run `cat {fileparts_zip} > {filename_r}` (depending on if you want fastboot or recovery file)
        - Then untar the .tar file or flash the .zip file
    - On Windows:
        - Run `copy /b {fileparts_tgz_win} {filename_fb}` or run `copy /b {fileparts_zip_win} {filename_r}` (depending on if you want fastboot or recovery file)
        - Then untar the .tar file or flash the .zip file
        

This is an automated release.
'''