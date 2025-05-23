# Chord diagram, Angular mapping and Parallel coordinates VISualization

library(circlize) 



# Read data ----
#d1 <- read.csv("plano_4D.csv", header = FALSE)
#d1 <- read.csv("wfg4_dwu-dec-r9.csv", header = FALSE)

d1 <- read.csv("decision_NSGAII_0.csv", header = FALSE)
#d1 <- read.csv("decision_DWU_0.csv", header = FALSE)

d1$V1 <- NULL

npop_d1 <- nrow(d1) # population size
nobj_d1 <- ncol(d1) # dimension
na_d1 <- matrix(data = NA, nrow = npop_d1, ncol = 3)
colnames(na_d1) <- c('rho', 'angle', 'axis')

# Transformations ----

# calculate the norm, smallest angle and do the association
for (i in 1:npop_d1) {
  if (norm(d1[i,], type = "2")==0){
    na_d1[i, "rho"] <- 0
    na_d1[i, "angle"] <- 0
    na_d1[i, "axis"] <- 1
  }
  else {
  na_d1[i, "rho"] <- norm(d1[i,], type = "2")
  aux <- acos(d1[i,] / na_d1[i, "rho"])
  na_d1[i, "angle"] <- min(aux)
  na_d1[i, "axis"] <- which.min(aux)}
}

na_d1 <- as.data.frame(na_d1)
df_d1 = data.frame(factors = na_d1$axis,
                   x = na_d1$angle,
                   y = na_d1$rho)

# Angular mapping ----
circos.clear()
circos.par(points.overflow.warning = FALSE)
circos.par(gap.after = c(rep(2, nobj_d1 - 1), 15), start.degree = 90)
circos.initialize(factors = 1:nobj_d1, xlim = c(0, acos(1 / sqrt(nobj_d1))))
circos.trackPlotRegion(
  factors = 1:nobj_d1,
  ylim = c(0, nobj_d1),
  track.height = 0.1,
  bg.border = NA,
  panel.fun = function(x, y) {
    circos.text(
      CELL_META$xcenter,
      CELL_META$cell.ylim[2],
      get.cell.meta.data("sector.index"),
      facing = "downward"
    )
  }
)
circos.trackPlotRegion(
  factors = 1:nobj_d1,
  ylim = c(min(c(na_d1$rho)), max(c(na_d1$rho))),
  track.height = 0.35,
  panel.fun = function(x, y) {
    xlim = get.cell.meta.data("xlim")
    ylim = get.cell.meta.data("ylim")
    sector.index = get.cell.meta.data("sector.index")
    circos.axis(labels.cex = 0.5)
  }
)

circos.yaxis(side = "left", sector.index = 1, labels.cex = 0.5)
circos.trackPoints(na_d1$axis,
                   na_d1$angle,
                   na_d1$rho,
                   col = "blue",
                   pch = 16,
                   cex = 0.4)



#  Chord Diagram ----
circos.clear()
circos.par(gap.after = c(rep(2, nobj_d1 - 1), 15), start.degree = 90,track.height = 0.2)
par(new = TRUE) # <- magic
a<-2
circos.par("canvas.xlim" = c(-a, a),"canvas.ylim" = c(-a, a))
circos.initialize(factors = rep(1:nobj_d1, length.out = npop_d1),xlim = c(0, max(d1)))
circos.track(
  ylim = c(0, 2),
  bg.border=c(0,0,0,0),
  panel.fun = function(x, y) {
    circos.axis(labels.cex = 0.5,
                major.tick.length = .9,
                h = "bottom",
                lwd = 1)
  }
)
for (i in 1:npop_d1) {
  for (j in 1:(nobj_d1 - 1)) {
    for (k in (j + 1):nobj_d1) {
      circos.link(j,
                  as.numeric(d1[i, j]),
                  k,
                  as.numeric((d1[i, k])),
                  col = "blue",
                  lwd = 0.1)
    }
  }
}

