%include "std_string.i"  // required to use std::string.

%{
#include "basic.h"
%}

namespace yunabe {
int int_sum(int x, int y);

std::string get_hello();

class Lib {
 public:
  static int int_mul(int x, int y);
};
 
}  // namespace yunabe
