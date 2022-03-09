
suppressPackageStartupMessages(library(RJSONIO))
suppressPackageStartupMessages(library(rcdk)) 
suppressPackageStartupMessages(library(rinchi))

cpd2pth <- function(cpd) {
	read.delim(paste0('http://rest.kegg.jp/link/pathway/', cpd), header=FALSE, stringsAsFactors=FALSE)[,2]
}

inchi2kegg <- function(inchi) {
    inchikey <- get.inchi.key(parse.inchi(inchi)[[1]]) 
    query <- paste0("http://cts.fiehnlab.ucdavis.edu/rest/convert/InChIKey/KEGG/", inchikey)
    fromJSON(query)[[1]]$results 
}

#gtaskid <- 'cf52aa4d7cb54ac4ad595dcbb633a8b2' 
### kegg_script.r <taskid> <name>
gnps2kegg <- function(args) {
    gtaskid <- args[1]
    url_to_result = paste0("http://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=",  gtaskid, "&block=main&file=result/")
    url_to_db = paste0("http://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=",  gtaskid, "&block=main&file=DB_result/")
    url_to_db_filt = paste0("http://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=",  gtaskid, "&block=main&file=DB_result_filtered/")
    url_to_networking_pairs_results_file_filtered = paste0("http://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=",  gtaskid, "&block=main&file=networking_pairs_results_file_filtered/")
    
    all_results <- read.delim(url_to_result, check.names=FALSE, stringsAsFactors=FALSE)
    all_db <- read.delim(url_to_db, check.names=FALSE, stringsAsFactors=FALSE)
    all_db_filt <- read.delim(url_to_db_filt, check.names=FALSE, stringsAsFactors=FALSE)
    all_networking_pairs <- read.delim(url_to_networking_pairs_results_file_filtered, check.names=FALSE, stringsAsFactors=FALSE)

    kid <- sapply(all_db_filt[,'INCHI'], function(x) try(inchi2kegg(x), TRUE)) 
    kid[unlist(lapply(kid, function(x) inherits(x, "try-error")))] <- '' 
    kid[unlist(lapply(kid, function(x) length(x)==0))] <- '' 
    kid <- unlist(lapply(kid, function(x) paste(x, collapse=','))) 
    
    kpth <- lapply(kid, function(x) try(cpd2pth(x), TRUE))
    kpth[unlist(lapply(kpth, function(x) inherits(x, "try-error")))] <- '' 
    kpth[unlist(lapply(kpth, function(x) length(x)==0))] <- '' 
    kpth <- unlist(lapply(kpth, function(x) paste(x, collapse=','))) 

    all_db_filt$keggid <- kid 
    all_db_filt$keggpth <- kpth 
    return(list(all_results=all_results, all_db=all_db,
               all_db_filt=all_db_filt, all_networking_pairs=all_networking_pairs))
}

if (!interactive()) {
    args <- commandArgs(trailingOnly = TRUE)
    gnps <-  gnps2kegg(args)
    gtask <- sub('(.{5}).+$', '\\1', args[1])
    prefix <- paste(args[2], gtask, '', sep='_')
    write.table(gnps$all_results, paste0(prefix, 'all_results.tsv'),
               sep='\t', row.names=FALSE)
    write.table(gnps$all_db, paste0(prefix, 'all_db.tsv'),
               sep='\t', row.names=FALSE)
    write.table(gnps$all_db_filt, paste0(prefix, 'all_db_filt.tsv'),
               sep='\t', row.names=FALSE)
    write.table(gnps$all_networking_pairs, paste0(prefix, 'all_networking_pairs.tsv'),
               sep='\t', row.names=FALSE)
    
}

