function writebytes(path, bytes)
  fd = fopen(path, "wb");
  fwrite(fd, cast(bytes, "uint8"), "uint8");
  fclose(fd);
endfunction
