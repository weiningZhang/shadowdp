extern void __VERIFIER_error() __attribute__ ((__noreturn__));
extern int __VERIFIER_nondet_float(void);
extern int __VERIFIER_nondet_int();
extern void __VERIFIER_assume(int);
extern void __assert_fail();
#define __VERIFIER_assert(cond) { if(!(cond)) { __assert_fail(); } }
#define abs(x) ((x) < 0 ? -(x) : (x))
typedef enum { false = 0, true = 1 } bool;
    
int partialsum(float epsilon, int size, float q[])
{
  __VERIFIER_assume(epsilon >= 0);
  float __LANG_v_epsilon = 0;
  float __LANG_distance_q[size];
  for (int __LANG_i = 0; __LANG_i < size; __LANG_i++)
    __LANG_distance_q[__LANG_i] = __VERIFIER_nondet_float();

  float out = 0;
  float sum = 0;
  int i = 0;
  while (i < size)
  {
    __VERIFIER_assert(i < size);
    sum = sum + q[i];
    i = i + 1;
  }

  float eta = __VERIFIER_nondet_float();
  __LANG_v_epsilon = __LANG_v_epsilon + ((1.0 * __LANG_distance_sum) * epsilon);
  out = sum + eta;
  __VERIFIER_assert(__LANG_v_epsilon <= epsilon);
}

