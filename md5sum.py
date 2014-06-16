from hashlib import md5 as hashmd5


def md5sum(data_file):
    md5 = hashmd5()
    try:
        # try to open the data_file in read and binary mode.
        data_file = open(data_file, 'rb').readlines()
    except IOError:
        return 1
    for l in data_file:
        # get each binary line of data_file and addition it:
        # line1 -> 137f72c3708c6bd0de00a0e5a69c699b
        # line2 -> e6251bcf1a7dc3ba5e7933e325bbe605
        # line1 + line2 -> ce8bc0316bdd8ad1f716f48e5c968854
        md5.update(l)
    # hash all.
    return md5.hexdigest()

# on a .TAR of 3419781120 bytes:
#      md5    -> 23117172 function calls in 31.329 seconds
#      sha1   -> 23117172 function calls in 34.333 seconds
#      sha224 -> 23117172 function calls in 51.071 seconds
#      sha256 -> 23117172 function calls in 50.665 seconds
#      sha384 -> 23117172 function calls in 40.080 seconds
#      sha512 -> 23117172 function calls in 41.278 seconds
