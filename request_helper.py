import zlib
import gzip
import brotli
import zstandard
import io


def decompress_data(compressed_data: bytes) -> bytes:
    if not compressed_data:
        return b""

    if compressed_data.startswith(b'\x1f\x8b'):
        try:
            with gzip.GzipFile(fileobj=io.BytesIO(compressed_data), mode='rb') as f:
                return f.read()
        except OSError:
            pass  
    try:
        return zlib.decompress(compressed_data)
    except zlib.error:
        try:
            return zlib.decompress(compressed_data, wbits=-zlib.MAX_WBITS) #raw deflate
        except zlib.error:
            pass 
    try:
        return brotli.decompress(compressed_data)
    except brotli.error:
        pass  
    try:
        dctx = zstandard.ZstdDecompressor()
        return dctx.decompress(compressed_data)
    except zstandard.ZstdError:
        pass  
    return compressed_data