#include "./input.lp".

% Generate a path
{path((X_1, Y_1, _),(X_2, Y_2, _)) : point(X_1, Y_1, _), point(X_2, Y_2, _}.

% Points need
:- path((X_1, Y_1, _), (X_2, Y_2, _)), |X_1 - X_2| + |Y_1 - Y_2| > 2, |X_1 - X_2| = 0, |Y_1 - Y_2| = 0.



#path/3
