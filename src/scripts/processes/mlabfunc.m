function doe_linear_model
%
% SDP based design for 4th order linear polynomial
%
% global parameters
%clear all;
clear           all;
digits          =   10;
%
tinicio     =       cputime;
%
% global variables
global  npar nw ind_criterion
global  inv_fim
%
% n. of parameters
npar                =   2;
%
% initial grid
low_x               =   -1.0;
up_x                =   1.0;
dx                  =   0.02;
x                   =   [low_x:dx:up_x];
x                   =   x';
nx                  =   size(x,1);
%
% save the initial grid
x_all(1,:)          =   x;  
y1(1, 1:nx)         =   1;
dx_all              =   diff(x);
%
% initialization of variables
iter_max            =   4;
icount              =   1;
V                   =   cell(1,1);
%
% variables used to save values
x_history           =   [];
x_history(:,1)      =   x;
obj_history         =   [];
psi_history         =   [];
xp_design(1:2*npar,1:iter_max)          =   0;
wp_design           =   [];
%
% initialization of the solver
cvx_setup
cvx_solver mosek
cvx_save_prefs     
% ind_criterion - variable that sets the criterion:
% 1 - D; 2 - A; 3 - E 
ind_criterion       =   3;
%
while icount<=1
    %
    % construct the vector V to provide the SDP solver
    [V]                 =   compute_cell(x, nx, npar);
    %
    % invoke the SDP solver
    [xf, obj_dec, nw(icount)]   =   optim_design(V, x, nx, npar, ind_criterion);
    % 
    % save
    xp_design(1:nw,1)   =   xf(:,1);
    obj_history         =   [obj_history;obj_dec];
    %
    % construct the matrix derivative function
    [inv_fim]           =   compute_disp_fun(x, xf, nx, nw(icount), ...
        npar, ind_criterion);
    %
    % find the points near to each support point - those are
    % the bounds for the NLP problem
    [x_lo, x_up]        =   find_lims(xf, nw(icount));
    %
    % compute the x maximum for the derivative function
    [xz, zi]            =   FindVTheta(xf, x_lo, x_up, nw(icount));
    xz                  =   xz';
    xf1(1:nw(icount),1) =   xz;     
    %
    % collapse points
    [xq, nq]            =   collapse_points(xf1, nw(icount));
    nw(icount)          =   nq;
    %
    % construct the vector V to provide the SDP solver
    [V]                 =   compute_cell(xq, nw(icount), npar); 
    %
    % invoke the SDP solver
    [xf, obj_dec, nw(icount+1)]   =   optim_design(V, xq, nw(icount), ...
        npar, ind_criterion);
    % 
    % save
    xp_design(1:nw(icount),2)   =   xf(:,1);
    obj_history         =   [obj_history;obj_dec];
    icount              =   icount+1;
end
%
% convergence
while abs((obj_history(icount)-obj_history(icount-1))/obj_history(icount))>=1e-4 && ...
        icount<=iter_max ,
    %
    % construct the matrix derivative function
    [inv_fim]           =   compute_disp_fun(xz, xf, nw(icount-1), nw(icount), ...
        npar, ind_criterion);
    %
    % find the points near to each support point - those are
    % the bounds for the NLP problem
    [x_lo, x_up]        =   find_lims(xf, nw(icount));
    %
    % compute the x maximum for the derivative function
    [xz, zi]            =   FindVTheta(xf, x_lo, x_up, nw);
    xz                  =   xz';
    %
    % construct the vector V to provide the SDP solver
    [V]                 =   compute_cell(xz, nw(icount), npar); 
    %
    % invoke the SDP solver
    [xf, obj_dec, nw(icount+1)] =   optim_design(V, xz, nw(icount), npar, ...
        ind_criterion);
    % 
    % save
    xp_design(1:nw(icount),icount+1)    =   xf(:,1);
    obj_history                         =   [obj_history;obj_dec];
    icount                              =   icount+1; 
end
xf
time_el                 =   cputime-tinicio
icount                  =   icount
%figure(1)
%for i=1:icount+1
%    ct                  =   [];
%    ct(1:nw(i),1)       =   i;
%    plot(xp_design(1:nw(i),i), ct(1:nw(i),1), 'ko')
%    hold on
%end
%axis([low_x, up_x, 1, icount+1])
end

%%
%
function  [V]    =   compute_cell(x, nx, npar)
%
% function that computes the vector of cells V
% problem dependent
%
% construct the vector h(x), so that h(x)*h(x)^T=M 
for i=1:nx
    h(1:npar, i)     =   [1.0; x(i)];
end
%
% construct the cells vector
V{1}                =   h(1:npar, 1:nx);
return
end
%%
%
function [xf, obj_dec, nw]   =  optim_design(V, x, nx, npar, ind_criterion)
%
% solve the SDP problem for a given criterion
if ind_criterion == 1
    %
    % solve the SDP problem for D-optimality
    cvx_begin sdp
    cvx_precision default
    variables lambda(nx)
 	maximize (det_rootn(V{1}*diag(lambda)*V{1}'))
        subject to
            V{1}*diag(lambda)*V{1}' == semidefinite(npar);
            sum(lambda)     == 1;
            lambda          >= 0;
    cvx_end
    %
    % optimum
    obj_dec                 =   det_rootn(V{1}*diag(lambda)*V{1}');
elseif ind_criterion == 2
    %
    % solve the SDP problem for A-optimality
    cvx_begin sdp
    cvx_precision default
    variables lambda(nx)
 	minimize (trace_inv(V{1}*diag(lambda)*V{1}'))
        subject to
            V{1}*diag(lambda)*V{1}' == semidefinite(npar);
            sum(lambda)     == 1;
            lambda          >= 0;
    cvx_end
    %
    % optimum
    obj_dec         =   trace_inv(V{1}*diag(lambda)*V{1}');
elseif ind_criterion == 3
    %
    % solve the SDP problem for E-optimality
    cvx_begin sdp
    cvx_precision default
    variables lambda(nx)
 	maximize (lambda_min(V{1}*diag(lambda)*V{1}'))
        subject to
            V{1}*diag(lambda)*V{1}' == semidefinite(npar);
            sum(lambda) == 1;
            lambda >= 0;
    cvx_end
    %
    % optimum
    obj_dec         =   lambda_min(V{1}*diag(lambda)*V{1}');
end
%
% prunning
lambdaD             =   lambda;
[lambdaj]           =   find(lambda>1e-5);
qt                  =   sum(lambda(lambdaj),1);
nw                  =   size(lambdaj,1);
x1z                 =   x(lambdaj);
lambdaz1            =   lambda(lambdaj)/qt;
xf                  =   [x1z, lambdaz1];
return
end
%%
% 
function    [inv_fim]       =   compute_disp_fun(x, xf, nx, nw, npar, ...
    ind_criterion)
%
%   compute the derivative of the criterion
x1z(1:nw)           =   xf(1:nw,1)';
lambdaz(1:nw)       =   xf(1:nw,2)';
%
% compute the FIM for optimal design
[V]                 =   compute_cell(x1z, nw, npar);
fim                 =   V{1}*diag(lambdaz)*V{1}';
%
% compute the derivative of matrix
if ind_criterion == 1
    for i=1:nw
        inv_fim(1:nw,1:nw,i)  =   inv(fim);
    end
elseif ind_criterion == 2
   inv_fim1             =   inv(fim);
   for i=1:nw
       inv_fim(1:nw,1:nw,i)  =   mpower(inv_fim1,2);
   end
elseif ind_criterion == 3
   [vec_eig, val_eig]   =   eig(fim);
   [lambda_min, iz_min] =   min(diag(val_eig));
   for i=1:nw
       p_eig                =   vec_eig(1:npar,i);
       inv_fim(1:nw,1:nw,i) =   p_eig*p_eig';
   end
end
return
end
%%
%
function  [x_lo, x_up]  =   find_lims(xf, nw)
%
% function that computes the limits for each support point
%
nx                      =   size(xf, 2)-1;
xz(1:nw,1:nx)           =   xf(1:nw,1:end-1);
xf1                     =   xz;
for k=1:nw
    for j=1:nw
        d(k,j)          =   sum((xz(k,1:nx)-xf1(j,1:nx)).^2,2);
    end
    [dist(k,1:nw), ind_x(k,1:nw)]   =   sort(d(k,1:nw), 2, 'ascend');
    for i=1:nx
        if k==1
            x_lo(k,i)   =   xz(1,i);
            x_up(k,i)   =   xz(ind_x(k,2),i)-1.0e-5;
        elseif k==nw
            x_lo(k,i)   =   xz(ind_x(k,2),i)+1e-5;
            x_up(k,i)   =   xz(end,i);
        elseif xf(ind_x(k,1),i) > xf(ind_x(k,2),i)
            x_up(k,i)   =   xz(ind_x(k,1),i);
            x_lo(k,i)   =   xz(ind_x(k,2),i);
        else
            x_up(k,i)   =   xz(ind_x(k,2),i);
            x_lo(k,i)   =   xz(ind_x(k,1),i);
        end
    end
end
return
end
%%
%
function  [xq, nz]      =   collapse_points(xf, nw)
%
% function that collapse points
%
nx                      =   size(xf, 2);
xz(1:nw,1:nx)           =   xf(1:nw,1:end);
for k=1:nw-1
    d(k)                =   sqrt(sum((xz(k+1,1:nx)-xz(k,1:nx)).^2,2));
end
xq                      =   xz(1,1:nx);
nz                      =   1;
for k=1:nw-1
    if d(k)>=1.0e-5
        nz              =   nz+1;
        xq              =   [xq; xz(k+1,1:nx)];
    end
end
return
end
%%
% compute the maximum for dispersion function
%
function    [v_sup, z] =   FindVTheta(xf, x_lo, x_up, nw)
% find the maximum of the dispersion function in X
%
nx                  =   size(xf, 2)-1;
for i=1:nx
    x0((i-1)*nw+1:i*nw)     =   xf(1:nw,i);
end
x0                  =   x0';
% linear inequalities
A                   =   [];
b                   =   [];
% linear equalities
Aeq                 =   [];
beq                 =   [];
%
nlcon=  '';
cl =    '';
cu =    '';
% Options
opts = optiset('solver','ipopt','display','iter');
%
% Build OPTI Problem
Opt = opti('fun',@V_theta_obj, 'grad', @V_theta_grad, ...
    'nl',nlcon, cl, cu, 'bounds', x_lo, x_up, ...
    'x0', x0, 'options', opts)
%
% Solve NLP
[th,z,exitflag,info] = solve(Opt);
v_sup               =   th';
end
%%
% objective function
function [z] =    V_theta_obj(x)
% objective
global  npar nw ind_criterion
global  inv_fim
%
adopts = admOptions();
[J, z]   =   admDiffFor(@V_minmax_M1, 1, x, adopts);
return
end
%%
% objective function
function [J] =    V_theta_grad(x)
% objective
global  npar nw ind_criterion
global  inv_fim
%
adopts = admOptions();
[J, z]   =   admDiffFor(@V_minmax_M1, 1, x, adopts);
J        =   J';
return
end


