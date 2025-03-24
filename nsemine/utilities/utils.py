import gzip
import io
import zlib
import brotli
import zstandard


def decompress_data(compressed_data: bytes) -> bytes:
    """
    Automatically detects and decompresses data compressed with gzip, deflate, brotli, or zstd.

    Args:
        compressed_data: The compressed bytes.

    Returns:
        The decompressed bytes, or the original bytes if decompression fails.
    """
    if not compressed_data:
        return b""

    # gzip check
    if compressed_data.startswith(b'\x1f\x8b'):
        try:
            with gzip.GzipFile(fileobj=io.BytesIO(compressed_data), mode='rb') as f:
                return f.read()
        except OSError:
            pass  

    # deflate check
    try:
        return zlib.decompress(compressed_data)
    except zlib.error:
        try:
            return zlib.decompress(compressed_data, wbits=-zlib.MAX_WBITS) #raw deflate
        except zlib.error:
            pass 

    # brotli check
    try:
        return brotli.decompress(compressed_data)
    except brotli.error:
        pass  
    # zstd check
    try:
        dctx = zstandard.ZstdDecompressor()
        return dctx.decompress(compressed_data)
    except zstandard.ZstdError:
        pass  

    # If all decompression attempts fail, returning the original data.
    return compressed_data