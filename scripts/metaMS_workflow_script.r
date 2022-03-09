# Load libraries
suppressPackageStartupMessages(library(metaMS))

mzmatch <- function(spec1, spec2) {
  common.masses1 <- which(spec1[,1] %in% spec2[,1])
  common.masses2 <- which(spec2[,1] %in% spec1[,1])

  if (length(common.masses1)>0) {
    sum(spec1[common.masses1, 2, drop = FALSE] *
	        spec2[common.masses2, 2, drop = FALSE])
  } else {
    0
  }
}

makeAnnotation <- function(n) {
  data.frame(pattern = rep(0, n),
	                  annotation = rep(0, n),
	                  alternatives = rep("", n),
	                  stringsAsFactors = FALSE)
}

annotations2tab <- function(annlist, matches) {
  single.hits <- which(sapply(annlist, length) == 1)
  single.result <- makeAnnotation(length(single.hits))
  single.result[,"pattern"] <- single.hits
  single.result[,"annotation"] <- unlist(annlist[single.hits])

  hits <- which(sapply(annlist, length) > 1)
  nhits <- length(hits)
  if (nhits == 0) {
    single.result
  } else {
    double.result <- makeAnnotation(nhits)
  
    for (i in 1:nhits) {
      ann <- annlist[[ hits[i] ]]
      matchfactors <- matches[ann, hits[i]]
      bestone <- which.max(matchfactors)
      double.result[i, 1:2] <- c(hits[i], ann[bestone])
      double.result[i, 3] <- paste(ann[-bestone], collapse = ",")
    }
    
    rbind(single.result, double.result)
  }
}
 matchSamples2DB <- function (xset.msp, DB, settings, quick) {
    if (settings$timeComparison == "RI") {
        standard.rts <- sapply(DB, function(x) x$std.RI)
        rt.matches <- lapply(1:length(xset.msp), function(ii) {
            group.rts <- sapply(xset.msp[[ii]], function(x) mean(x[, 
                "RI"]))
            which(abs(outer(standard.rts, group.rts, FUN = "-")) < 
                settings$RIdiff, arr.ind = TRUE)
        })
    }  else {
        standard.rts <- sapply(DB, function(x) x$std.rt)
        rt.matches <- lapply(1:length(xset.msp), function(ii) {
            group.rts <- sapply(xset.msp[[ii]], function(x) mean(x[, 
                "rt"]))
            which(abs(outer(standard.rts, group.rts, FUN = "-")) < 
                settings$rtdiff, arr.ind = TRUE)
        })
    }
    if (quick) {
        match.results <- lapply(1:length(xset.msp), function(ii) {
            result <- matrix(0, length(DB), length(xset.msp[[ii]]))
            for (i in 1:nrow(rt.matches[[ii]])) {
                DB.idx <- rt.matches[[ii]][i, 1]
                sample.idx <- rt.matches[[ii]][i, 2]
                result[DB.idx, sample.idx] <- mzmatch(DB[[DB.idx]]$pspectrum, 
                  xset.msp[[ii]][[sample.idx]])
            }
            result
        })
    } else {
        match.results <- list()
        for(ii in 1:length(xset.msp)) {
            result <- matrix(0, length(DB), length(xset.msp[[ii]]))
            if(nrow(rt.matches[[ii]])==0){
                match.results[[ii]] <- result 
                next
            }
            for (i in 1:nrow(rt.matches[[ii]])) {
                DB.idx <- rt.matches[[ii]][i, 1]
                sample.idx <- rt.matches[[ii]][i, 2]
                exp.pat <- xset.msp[[ii]][[sample.idx]]
                MWlimit <- DB[[DB.idx]]$monoMW + 4
                if (length(MWlimit) == 0) 
                  MWlimit <- max(DB[[DB.idx]]$pspectrum[, 1])
                ok.mz <- which(exp.pat[, "mz"] <= MWlimit)
                if (length(ok.mz) > settings$minfeat) {
                  exp.pat <- treat.DB(list(exp.pat[ok.mz, ]), 
                    isMSP = FALSE)
                  result[DB.idx, sample.idx] <- mzmatch(DB[[DB.idx]]$pspectrum, 
                    exp.pat[[1]])
                }
            }
            match.results[[ii]] <- result 
        }
    }
    names(match.results) <- names(xset.msp)
    annotations <- lapply(match.results, function(xx) {
        sapply(1:ncol(xx), function(ii) which(xx[, ii] > settings$simthresh))
    })
    list(annotations = mapply(annotations2tab, annotations, match.results, 
        SIMPLIFY = FALSE))
}

main <- function(args) {
    # Load settings
    data(FEMsettings)
    
    # After parameter selection, perform peak picking
    GCset <- peakDetection(args[1], settings = metaSetting(TSQXLS.GC, "PeakPicking"), convert2list = TRUE, nSlaves = 6)
    
    # Group the peaks corresponding to the fragmentation pattern
    allSamples <- lapply(GCset, runCAMERA, chrom = "GC", settings = metaSetting(TSQXLS.GC, "CAMERA"))
    
    # Format spectra to databse search
    allSamples.msp <- lapply(allSamples, to.msp, file = NULL, settings = metaSetting(TSQXLS.GC, "DBconstruction"))

    sempty <- lapply(allSamples.msp, length)>0
    if(sum(!sempty)) {
    	allSamples.msp <- allSamples.msp[sempty] 
    }
    # Load a example databse to simulate database search
    data(threeStdsDB)
    DB.treated <- treat.DB(DB)
    
    # Match spectra to database to obtain a format we can export
    allSam.matches <- matchSamples2DB(allSamples.msp, DB = DB.treated, settings = metaSetting(TSQXLS.GC, "match2DB"), quick = FALSE)
    allSamples.msp.scaled <- lapply(allSamples.msp, treat.DB, isMSP = FALSE)
    
    # change paramters
    TSQXLS.GC@betweenSamples.min.class.fraction <- 0.001
    TSQXLS.GC@betweenSamples.min.class.size <- 1
    
    allSam.matches <- matchSamples2Samples(allSamples.msp.scaled, allSamples.msp, annotations = allSam.matches$annotations, settings = metaSetting(TSQXLS.GC, "betweenSamples"))

   d <- data.frame(pattern=integer(0), annotation=integer(0), alternatives=character(0))
   for(l in 1:length(allSam.matches$annotations)) {
       cnames <- colnames(allSam.matches$annotations[[l]])
       if (!('annotation' %in% cnames)) {
           allSam.matches$annotations[[l]] <- d
       }
   }
    
    # create the fragmentation spectra
    PseudoSpectra <- constructExpPseudoSpectra(allMatches = allSam.matches,standardsDB = DB)
    
    # Format quantification table
    ann.df <- getAnnotationMat(exp.msp = allSamples.msp, pspectra = PseudoSpectra, allMatches = allSam.matches)
    ann.df2 <- sweep(ann.df, 1, sapply(PseudoSpectra,function(x) max(x$pspectrum[, 2])), FUN = "*")
    ann.df3 <-  cbind(do.call(rbind, lapply(PseudoSpectra, function(x) c(x$Name, x$rt, x$pspectrum[which.max(x$pspectrum[,2])[1],1]))), ann.df2) 
    colnames(ann.df3)[1:3] <- c("ID", "RT", "BP")
    #write.msp(PseudoSpectra, "win_cf_optim.msp")
    
    file.create(paste0(args[1], ".mgf"))
    for(i in 1:nrow(ann.df3)) {
        name <- i 
        bpmass <- ann.df3[i, 'BP'] 
        rt <-  PseudoSpectra[[i]]$rt 
        id <- i 
        mgf <- c("BEGIN IONS",
    	                   paste0("FEATURE_ID=", id),
    	                   paste0("PEPMASS=", bpmass),
    	                   paste0("RTINSECONDS=", rt),
    	                   paste0("SCANS=", id),
    	                   "MSLEVEL=2",
    	                   "CHARGE=1+",
                                apply(PseudoSpectra[[i]]$pspectrum, 1, function(x) paste(x, collapse=' ')),
    	                    "END IONS",
    	                  ""
    	                  )
        # CHANGE THE NAME OF THE OUTPUT FILE HERE ON: test.mgf
        write.table(mgf, paste0(args[1], ".mgf"), row.names=FALSE, col.names = FALSE, quote=FALSE, append = TRUE)
    }
    write.table(ann.df3, paste0(args[1], ".tsv"), row.names=FALSE, sep="\t", quote=FALSE) 
}
    
if (!interactive()) {
    args <- commandArgs(trailingOnly = TRUE)
    main(args)
    #print(args)
}



