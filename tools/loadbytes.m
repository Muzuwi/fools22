function bytes = loadbytes(path)
  fd = fopen(path, "rb");
  bytes = fread(fd, Inf, "uint8");
  bytes = cast(bytes, "uint8");
  fclose(fd);
endfunction
