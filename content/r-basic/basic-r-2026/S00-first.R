## Variables

x <- 1 + 1
y <- x * 12

z <- x + y

z

mass
age

mass <- 47.5            # mass?
age  <- 122             # age?
mass <- mass * 2.0      # mass?
age  <- age - 20        # age?
mass_index <- mass/age  # mass_index?

## Functions

round(3.1415)

?round

round(3.1415, digits = 2)

round(x = 3.1415, digits = 2)

round(3.1415, 2)

ls()

c(1, 4, 34, 32, 4)

w <- c(40, 50, 47, 63)
w

length(w)

class(w)
class(z)


## Ex:

x <- 10.2463
y <- 2.45
z <- round(x + y, y)

z

round(x + y, 2.999)

as.integer(2.999)
round(2.999)


molecules <- c("dna", "rna", "protein")

length(molecules)

nchar(molecules)

class(molecules)


"hello"

character()

## Ex: create a new vector molecules2, that
## contains dna, rna, protein and metabolite.
## Do not type dna, rna, protein, but reuse,
## molecules.

(molecules2 <- c(molecules, "metabolites"))

TRUE
FALSE

# T <- 12
# T <- FALSE
# F <- TRUE

c(TRUE, FALSE, FALSE)

## Ex:

num_char <- c(1, 2, 3, "a")
(num_logical <- c(1, 2, 3, TRUE, FALSE))
(char_logical <- c("a", "b", "c", TRUE))
(tricky <- c(1, 2, 3, "4"))

class(num_char)
class(num_logical)
class(char_logical)
class(tricky)

as.character(123)
as.numeric("1")
as.numeric("dna")

## subsetting

molecules2

molecules2[2]

molecules2[c(1, 3)]

molecules2[-2]

molecules2[c(-1, -3)]

molecules2[-c(1, 3)]


## molecules2[1, 3]

## Ex: using molecules2, create a new vector
## containing protein, dna, rna, dna, protein

molecules2[c(3, 1, 2, 1, 3)]

w <- c(21, 34, 39, 54, 55)
w[c(TRUE, FALSE, TRUE, TRUE, FALSE)]


## Ex: extract the heavy rat weights
w[c(4, 5)]
w[c(FALSE, FALSE, FALSE, TRUE, TRUE)]

w[w > 50]

w[w >= 50]

## < <= > >= == !=

## Ex: we define heavy rats as those that are
## heavier (or equal) to 50g. 
## 1. compute the mean weight of heavy rats
## 2. compute the mean weight of light rats

mean(w[w >= 50])

w < 50
mean(w[!w >= 50])

heavy_rats <- w > 50

w[heavy_rats]

w[!heavy_rats]

## heavy >= 50
## light <= 35

w >= 50

w <= 35

w >= 50 & w <= 35

w[w >= 50 | w <= 35]


## Ex: among all molecules, extract
## nucleic acids - do not use indices.

## using is equal to (==) and or (|)

molecules2[molecules2 == "dna" | 
             molecules2 == "rna"]

nucl_acids <- c("rna", "dna")

molecules2 %in% nucl_acids

molecules2[molecules2 %in% nucl_acids]

w
names(w)

names(w) <- c("rat12", "rat34",
              "rat421", "rat2",
              "rat92")

w
names(w)

w > 33

w[w > 33]

names(w[w > 33])

x <- 1:5
x
names(x) <- letters[1:4]
x

(x <- 1:10)
(y <- 1:2)

x + y

(z <- 1:3)

x + z

sum(x)  
 
## Missing data/values

heights <- c(2, 5, 6, 2, NA, 4)
heights

class(heights)

class(c(molecules2, NA))

class(c(TRUE, FALSE, NA))

mean(heights)

## Ex: compute the mean of the known
## values of heights. First by looking
## at the manual page of mean, then
## by doing it by hand with is.na()
## and [].

?mean

mean(heights, na.rm = TRUE)


heights

mean(heights[!is.na(heights)])

mean(heights[-which(is.na(heights))])

na_index <- which(is.na(heights))
height_not_missing <- heights[-na_index]
mean(height_not_missing)

na.omit(heights)

complete.cases(heights)


mean(heights[!is.na(heights)])









