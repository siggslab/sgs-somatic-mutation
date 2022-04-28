version development

task md5 {
    input {
        File inputFile
        String prefix
    }

    command {
        echo "start"
        md5sum ~{inputFile} &> ~{prefix}.md5.txt
        echo "done"
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

workflow calMD5 {
    input {
        File inputFile
        String prefix
    }

    call md5 { input: inputFile=inputFile, prefix=prefix }

    output {
        File out = md5.out_file
        String out_s = md5.out_str
    }
}

