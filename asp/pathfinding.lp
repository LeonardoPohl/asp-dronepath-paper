#include "input.lp".

isPoint(point(X, Y, Z)) :- point(X, Y, Z).

% Generate a path
{path(A, B)} :- isPoint(A), isPoint(B).

%------------------------
% Point Constraints

% Each path can only lead to a neightbour
:- path(point(X1, Y1, _), point(X2, Y2, _)), |X1 - X2| + |Y1 - Y2| <> 1.

% A path cannot lead to the same place
%:- path(point(X, Y, _), point(X, Y, _)).

% Each path can only lead forward
:- path(point(X1, Y1, _), point(X2, Y2, _)), X2 - X1 < 0.

:- path(point(X1, Y1, _), point(X2, Y2, _)), path(point(X2, Y2, _), point(X1, Y1, _)).

% This is only necessary for performance and midway solutions
:- path(point(_, _, _), point(X, Y, _)),
    path(point(X, Y, _), point(X1, Y1, _)),  path(point(X, Y, _), point(X2, Y2, _)),
    |X1 - X2| + |Y1 - Y2| > 0.
:- path(point(X1, Y1, _), point(X, Y, _)), path(point(X2, Y2, _), point(X, Y, _)),  |X1 - X2| + |Y1 - Y2| > 0.

%------------------------
% Path Constraints

% There must be a path that starts from the start position
:- not path(A, _), start(A).

% There must be a path that leads to the destination
:- not path(_, B), end(B).

%------------------------
% Path leads

% A path is connected to the start position if it is at the start position
connected(A) :- start(A).

% Recursive definition of connected to start, if a point is connected to the start, a new point is connected
%   to the previous point is also connected to the start
connected(B) :- connected(A), path(A, B).

% Every path has to be connected to the start
:- path(A, B), not connected(A).
:- path(A, B), not connected(B).

%------------------------
% Minimization

% Minimize hight delta |H1-H2| for the chosen paths
#minimize {|H2-H1| + 1, X1, Y1, X2, Y2 : path(point(X1, Y1, H1), point(X2, Y2, H2))}.

%------------------------
% Output

% Only show the path(A, B) atom
#show path/2.