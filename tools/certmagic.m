clear; clc; close all;

pkg load signal;


%{
permutations = nchoosek([0:1:3], 2);

for i=1:length(permutations)
  sprintf("c%d.bin", permutations(i, 1))
  sprintf("c%d.bin", permutations(i, 2))

  a = loadbytes(sprintf("c%d.bin", permutations(i, 1)));
  b = loadbytes(sprintf("c%d.bin", permutations(i, 2)));
  
  r = bitxor(a, b);
  plot(0:length(a)-1, r, "o");
  hold on;
  
  writebytes(sprintf("xored_%d_%d.bin", permutations(i, 1), permutations(i, 2)), r);
endfor
%}

%{
for i=0:1
  bytes = loadbytes(sprintf("ee%d.bin", i));
  
  permutations = nchoosek([0:1:2], 2);
  for j=1:length(permutations)
    st0 = 16 + permutations(j, 1)*16;
    st1 = 16 + permutations(j, 2)*16;
    
    block0 = bytes(st0:st0+16);
    block1 = bytes(st1:st1+16);
  
    corr = xcorr(block0, block1)
    plot(1:length(corr), corr);
    hold on;
  endfor
endfor
%}

%{
bytes = loadbytes("cert_long_bullshit.bin");
#bytes = loadbytes("random.bin");
corr = xcorr(bytes);
plot(1:length(corr), corr);
%}

%{
cipher = loadbytes("cert_long_bullshit.bin");
plain =  loadbytes("cert_long_bullshit_plain.bin");
 
bitcounts = zeros(16*8, 2);

for i=1:((length(cipher)/16) - 1)
    if i*16 + 16 > length(plain)
      printf("Skipping iteration %d - no plain text", i);
      continue;
    endif
  
    a = cipher((i*16):(i*16+16));
    b = plain((i*16):(i*16+16));
  
    r = bitxor(a, b);
    for bit=0:(16*8 - 1)
      idx = uint64(bit / 8);
      off = uint64(mod(bit, 8));
      v = bitget(r(1 + idx), 1 + off);
      bitcounts(1+bit, 1+v) += 1;
    endfor
endfor
  
h = bar(bitcounts)
%}