version development

workflow hello1 {
  input {
    File inpf
    String prefix
  }

  command {
    echo "~{prefix} start"
    md5sum ~{inpf} &> ~{prefix}.md5.txt
    echo "~{prefix} done"
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
