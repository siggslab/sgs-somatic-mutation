version development

task md5sumTask {
  input {
    File in_file
    String prefix
  }

  command {
    echo "start ~{prefix}" 
    md5sum ~{in_file} > ~{prefix}.md5.txt
    echo "done ~{prefix}" 
  }

  runtime {
    cpu: 1
    disks: "local-disk 10 SSD"
    docker: "ubuntu@sha256:1d7b639619bdca2d008eca2d5293e3c43ff84cbee597ff76de3b7a7de3e84956"
    memory: "1G"
  }
  output {
    File out_file = "~{prefix}.md5.txt"
    String out_str = read_string(stdout())
  }
}

workflow md5sum {
  input {
    File inpf
    String prefix
  }
  call md5sumTask {
    input:
      in_file = inpf,
      prefix = prefix
  }
  output {
    File md5_res = md5sumTask.out_file
  }
}
