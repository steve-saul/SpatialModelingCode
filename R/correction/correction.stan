  /* correction model */

  data {
      int<lower=0> N;   // number of data items
      int<lower=0> P;   // number of predictors
      matrix[N, P+1] X;   // predictor matrix
      vector[P + 1] uB;  // expectation of betas
      matrix[P + 1, P + 1] VB;  //covariance of betas
      vector[N] Y_i_pred;  // predictions 
      vector[N] Dinv_i;   //distance mean inverse 
      vector[N] Y_i_cpue; //cpue values
      real sr;  // variance for real abundance
      real sc;  // varaince for cpue
      real sk;  // varaince for k
  }

  transformed data {
    cholesky_factor_cov[P + 1] L_VB;
    vector[N] Zero;
    vector[N] I;
    matrix<lower = 0>[N, N] D;
    {
      Zero = rep_vector(0, N);
      I = rep_vector(1, N);
      D = diag_matrix(I);
      L_VB = cholesky_decompose(VB);
    }
  }

  parameters{
      vector[P + 1] beta;
      real<lower = 0> tau;
      real<lower = 0> sigma;
      real<lower = 0> k;
      vector[N] resi_cpue;
  }

  transformed parameters {
      real tausq = square(tau);
      real sigmasq = square(sigma);
      //real resi;
  }

  model{
      vector[N] Y_i_real;  // predictions
      vector[N] Y_E_i_real;
      vector[N] temparg;  
      vector[N] tempreal;
      

      beta ~ multi_normal_cholesky(uB, L_VB);
      tau ~ normal(0, sr);
      sigma ~ normal(0,sc);
      k ~ normal(1,sk);
      resi_cpue ~ multi_normal(Zero,square(sigma)*D);
      
      temparg = Dinv_i/k;
      Y_E_i_real = Y_i_cpue .* temparg;
      
      Y_i_real = Y_E_i_real + resi_cpue;
      tempreal = Y_i_real - Y_i_pred;
      
      tempreal ~ normal(X * beta, tau);
  }













