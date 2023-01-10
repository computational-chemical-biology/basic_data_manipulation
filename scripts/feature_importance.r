#https://www.r-bloggers.com/2015/09/passing-arguments-to-an-r-script-from-command-lines/
suppressPackageStartupMessages(library(randomForest))
suppressPackageStartupMessages(library("mixOmics"))
suppressPackageStartupMessages(library(ropls))
args = commandArgs(trailingOnly=TRUE)

featImp <- function(feat, meta, field, out, ptype='ortho', 
                    norm=FALSE, scale=TRUE, classes=NULL) {
    feat2 <- feat[,grepl('Peak area', colnames(feat))] 
    colnames(feat2) <- sub(' Peak area', '', colnames(feat2)) 
    feat2 <- data.frame(t(feat2)) 

    if (norm){
        feat2 <- t(apply(feat2, 1, function(x) x/sum(x)))
    }

    if(scale){
        feat2 <- scale(feat2)
    }

    feat2 <- as.data.frame(feat2) 
    feat2$filename <- rownames(feat2) 

    if (!is.null(classes)) {
        meta <- meta[meta[,field] %in% strsplit(classes, ',')[[1]],]
    }
    data <- merge(meta[, c('filename', field)], feat2) 
    print('Turning two classes model...')
    data[data[,field]=='B', field] = 'A'
    data <- data[,-1]
    data[,1] <- as.factor(data[,1])

    ## Classification:
    ##data(iris)
    set.seed(71)
    print('Fitting Random Forest Model...')
    rf <- randomForest(data[,-1], data[,1], importance=TRUE,
                       proximity=TRUE, ntree=5000)
    print(rf)
    sink(paste0("rf_fit_", out, ".txt")) 
    print(rf)
    sink() 
    ## Look at variable importance:
    imp <- cbind(feat[,1:3], importance(rf)) 
    imp <- imp[order(abs(imp[,"MeanDecreaseAccuracy"]), decreasing=TRUE),]
    write.table(imp, paste0('rf_var_imp_', out, '.tsv'), row.names=FALSE, sep='\t') 

    ## Do MDS on 1 - proximity:
    mds <- cmdscale(1 - rf$proximity, eig=TRUE)
    pdf(paste0('rf_mdf_', out, '.pdf'))
    plot(mds$points, pch=19, col=c('blue', 'red')[as.numeric(data[,1])],
         xlab=paste0('Comp 1 (', round(mds$GOF[1],3)*100, '%)'),
         ylab=paste0('Comp 2 (', round(mds$GOF[2],3)*100, '%)'),
         main=paste('RF proximity MDS', out))
    legend("top", legend=unique(data[,1]), col=c("blue", "red"), pch=19) 
    dev.off() 

    if (ptype=='ortho'){
        print('Fitting OPLS-DA Model...')
        oplsda.res <- opls(data[,-1], data[,1],
                                predI = 1, orthoI = NA)
        vip.res <- cbind(feat[,1:3], oplsda.res@orthoVipVn) 
        write.table(vip.res, paste0('plsda_vip_', out, '.tsv'), row.names=FALSE, sep='\t') 
        write.table(oplsda.res@modelDF, paste0('plsda_summary_', out, '.tsv'), sep='\t') 
        pdf(paste0('oplsda_', out, '.pdf'))
        #plot(oplsda.res@scoreMN, oplsda.res@orthoScoreMN[,1], col=c('blue', 'red')[as.numeric(data[,1])], pch=19) 
        ropls::plot(oplsda.res, typeVc = "x-score") 
        dev.off() 
    } else {
        print('Fitting OPLS-DA Model...')
        plsda.res <- plsda(data[,-1], data[,1], ncomp = 10)
        pdf(paste0('plsda_', out, '.pdf'))
        plotIndiv(plsda.res, ellipse = TRUE, legend = TRUE)
        dev.off()

        pdf(paste0('plsda_roc_', out, '.pdf'))
        auc.plsda <- auroc(plsda.res)
        dev.off()
        #tune.plsda = perf(plsda.res, tune = "all", validation = "Mfold", folds = 5, progressBar = FALSE)

        vip.res <- cbind(feat[,1:3], vip(plsda.res)) 
        write.table(vip.res, paste0('plsda_vip_', out, '.tsv'), row.names=FALSE, sep='\t') 
    }


}

if (length(args)){
    print('Loading features...')
    feat = read.csv(args[1], check.names=FALSE) 
    print('Loading metadata...')
    meta <- read.delim(args[2], check.names=FALSE, stringsAsFactors=FALSE)
    field <- args[3]
    out <- args[4]
    if (length(args) > 4){
        classes <- args[5]
    } else {
        classes <- NULL
    }
    print('Computing data formatting...')
    featImp(feat, meta, field, out, classes=classes) 
}
