extern void __VERIFIER_error() __attribute__ ((__noreturn__));
extern void __VERIFIER_assume(int);
extern int __VERIFIER_nondet_float();
extern void __assert_fail();
#define __VERIFIER_assert(cond) { if(!(cond)) { __assert_fail(); } }

typedef enum { false = 0, true = 1 } bool;

#define SIZE 4
#define EPSILON 1

int sparsevector(float epsilon, float T, float N, float q[], float dq[]) {

  __VERIFIER_assume(epsilon > 0 && epsilon < 100000);
  __VERIFIER_assume(T > 0);
  __VERIFIER_assume(N == 1);

  float v_eps = 0;
  float eta_1 = __VERIFIER_nondet_float();
  float s_eta_1 = eta_1;
  v_eps = v_eps + EPSILON / 2;

  float T_bar = T + eta_1;

  int c_1 = 0, c_2 = 0;

  int i = 0;

  bool out = false;

  while (c_1 < N && i < SIZE)
  {
    float eta_2 = __VERIFIER_nondet_float();
    float s_eta_2 = eta_2;
    float v_eps = v_eps + (((q[i] + eta_2 >= T) ? 2 : 0) * (EPSILON / (4 * N)));

    if (q[i] + eta_2 >= T_bar)
    {
      __VERIFIER_assert(q[i] + dq[i] + eta_2 + 2 >= T_bar + 1);
      out = true;
      c_1 = c_1 + 1;
    }
    else
    {
      __VERIFIER_assert(q[i] + dq[i] + eta_2 < T_bar + 1);
      out = false;
      c_2 = c_2 + 1;
    }
    i = i + 1;
  }
}