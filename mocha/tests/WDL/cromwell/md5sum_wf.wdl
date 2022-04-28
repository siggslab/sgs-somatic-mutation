version development

import "tools/md5sum.wdl" as M

workflow md5Sum {
  input {
    File inpf
    String prefix
  }
  call M.md5sum as md5 {
    input:
      in_file = inpf,
      prefix = prefix
  }
  output {
    File md5_res = md5.out_file
    String md5_str = md5.out_str
  }
}
