// 
// by happy coincidence the first thing encountered in nms_kernel.cu is 
// the declaration of _nms, so extern "C" will work on that declaration.
// 
extern "C"
#include "nms_kernel.cu"
