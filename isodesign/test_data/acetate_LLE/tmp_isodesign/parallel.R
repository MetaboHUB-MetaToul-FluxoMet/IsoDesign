
        suppressPackageStartupMessages(library(parallel))
        suppressPackageStartupMessages(library(Rcpp))
        dirx="C:/Users/kouakou/AppData/Local/miniconda3/envs/influx/Lib/site-packages/influx_si/R"
        dirres="default" # can be "default" or empty
        source(file.path(dirx, "opt_cumo_tools.R"))
        doit=function(fR) {
           f=substr(fR, 1, nchar(fR)-2)
           fshort=basename(f)
           if (dirres == "default") {
              nm_flog=sprintf("%s_res/%s.log", f, fshort)
              nm_ferr=sprintf("%s_res/%s.err", f, fshort)
              flog=file(nm_flog, "a")
           } else {
              flog=base::stdout()
              ferr=base::stderr()
           }
           now=Sys.time()
           
           cat("calcul  : ", format(now, "%Y-%m-%d %H:%M:%S"), "\n", sep="", file=flog)
           if (dirres == "default") {
              close(flog)
           }
           source(fR)
           now=Sys.time()
           if (dirres == "default") {
              flog=file(nm_flog, "a")
           } else {
              flog=base::stdout()
           }
           cat("end     : ", format(now, "%Y-%m-%d %H:%M:%S"), "\n", sep="", file=flog)
           if (dirres == "default") {
              if (file.info(nm_ferr)$size > 0) {
                  cat("=>Check ", nm_ferr, "\n", sep="", file=flog)
              }
              close(flog)
           }
           return(retcode)
        }
        # build dyn lib
        nodes=4
        type="PSOCK"
        cl=makeCluster(nodes, type)
        clusterExport(cl, "dirres")
        flist=c("file_01.R", "file_03.R", "file_04.R", "file_02.R", "file_07.R", "file_06.R", "file_08.R", "file_05.R", "file_09.R", "file_10.R", "file_11.R")
        retcode=max(abs(unlist(parLapply(cl, flist, doit))))
        stopCluster(cl)
        q("no", status=retcode)
        